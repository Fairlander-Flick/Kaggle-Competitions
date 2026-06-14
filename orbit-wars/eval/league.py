"""
Orbit Wars local league — the campaign's MEASUREMENT CONTRACT.

A match = N fixed seeds, each played twice (positions swapped) to cancel any
first-position bias.  Win counts a draw as 0.5.  We report the Wilson 95% lower
bound on the win rate; the acceptance gate (significance) reads that bound.

Agents are referenced by a STRING SPEC so workers can rebuild them after a
process fork (closures aren't reliably picklable):

    pool:random | pool:starter | pool:sniper | pool:idle
    orbiter                       -> Orbiter with baked-in PARAMS
    orbiter:/abs/params.json      -> Orbiter with evolved params
    arch:<name>                   -> diverse archetype (eval/archetypes.py)
    sg:<name>                     -> STRONG, replay-mimicking opponent
                                     (eval/strong_gauntlet.py): snowball | blitz
                                     | bigfleet | swarm | econdef
    file:/abs/main.py             -> load mod.agent from a file

Usage:
    python league.py --a orbiter --b pool:sniper --games 200 --procs 16
    python league.py --a orbiter:/path/p.json --b orbiter --games 300
"""

import argparse
import json
import math
import os
import sys
import warnings
from multiprocessing import Pool

warnings.filterwarnings("ignore")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RUN_DIR)


def resolve(spec):
    """spec string -> agent callable. Rebuilt inside each worker."""
    from bots.orbiter import make_agent
    from eval.baselines import POOL
    if spec in ("orbiter",) or spec.startswith("orbiter:"):
        if ":" in spec:
            path = spec.split(":", 1)[1]
            with open(path) as f:
                return make_agent(json.load(f))
        return make_agent()
    if spec.startswith("pool:"):
        return POOL[spec.split(":", 1)[1]]
    if spec.startswith("arch:"):
        from eval.archetypes import get_archetypes
        return get_archetypes()[spec.split(":", 1)[1]]
    if spec.startswith("sg:"):
        from eval.strong_gauntlet import get_strong
        return get_strong(spec.split(":", 1)[1])
    if spec.startswith("file:"):
        # load an agent() from an arbitrary main.py-style file
        import importlib.util
        path = spec.split(":", 1)[1]
        s = importlib.util.spec_from_file_location("loaded_agent", path)
        mod = importlib.util.module_from_spec(s)
        s.loader.exec_module(mod)
        return mod.agent
    raise ValueError(f"unknown agent spec: {spec}")


def _play(args):
    """Run one game. Returns +1 (A wins), -1 (B wins), 0 (draw)."""
    spec_a, spec_b, seed, swap, n_agents, steps = args
    warnings.filterwarnings("ignore")
    from kaggle_environments import make
    A = resolve(spec_a)
    B = resolve(spec_b)
    if n_agents == 2:
        line = [B, A] if swap else [A, B]
        a_idx = 1 if swap else 0
    else:
        # 4p: A in one seat, B fills the rest
        line = [A, B, B, B]
        # rotate A's seat by swap so seat bias cancels
        a_idx = swap % 4
        line = line[-a_idx:] + line[:-a_idx] if a_idx else line
    env = make("orbit_wars",
               configuration={"seed": seed, "episodeSteps": steps},
               debug=False)
    env.run(line)
    final = env.steps[-1]
    rewards = [s["reward"] for s in final]
    a_r = rewards[a_idx]
    others = [r for i, r in enumerate(rewards) if i != a_idx]
    if a_r == 1 and all(r != 1 for r in others):
        return 1
    if a_r != 1 and any(r == 1 for r in others):
        return -1
    return 0


def _play_params(args):
    """Like _play but side A is Orbiter built from an explicit params dict
    (no file IO / spec round-trip — used by the CMA-ES tuner)."""
    params_a, spec_b, seed, swap, n_agents, steps = args
    warnings.filterwarnings("ignore")
    from kaggle_environments import make
    from bots.orbiter import make_agent
    A = make_agent(params_a)
    B = resolve(spec_b)
    if n_agents == 2:
        line = [B, A] if swap else [A, B]
        a_idx = 1 if swap else 0
    else:
        line = [A, B, B, B]
        a_idx = swap % 4
        line = line[-a_idx:] + line[:-a_idx] if a_idx else line
    env = make("orbit_wars",
               configuration={"seed": seed, "episodeSteps": steps},
               debug=False)
    env.run(line)
    rewards = [s["reward"] for s in env.steps[-1]]
    a_r = rewards[a_idx]
    others = [r for i, r in enumerate(rewards) if i != a_idx]
    if a_r == 1 and all(r != 1 for r in others):
        return 1
    if a_r != 1 and any(r == 1 for r in others):
        return -1
    return 0


def winequiv_params(pool, params_a, opponents, games_per_opp, base_seed,
                    n_agents=2, steps=500):
    """Build the task list for one candidate over several opponents; return
    tasks to be mapped on a shared Pool (caller owns the pool for efficiency)."""
    tasks = []
    n_seeds = games_per_opp // 2
    for spec_b in opponents:
        for i in range(n_seeds):
            seed = base_seed + i
            tasks.append((params_a, spec_b, seed, 0, n_agents, steps))
            tasks.append((params_a, spec_b, seed, 1, n_agents, steps))
    return tasks


def wilson_lower(wins, n, z=1.96):
    if n == 0:
        return 0.0
    p = wins / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return center - margin


def run_match(spec_a, spec_b, games=200, procs=16, base_seed=1000,
              n_agents=2, steps=500):
    n_seeds = games // 2
    tasks = []
    for i in range(n_seeds):
        seed = base_seed + i
        tasks.append((spec_a, spec_b, seed, 0, n_agents, steps))
        tasks.append((spec_a, spec_b, seed, 1, n_agents, steps))
    if procs > 1:
        with Pool(procs) as pool:
            results = pool.map(_play, tasks)
    else:
        results = [_play(t) for t in tasks]
    n = len(results)
    a_wins = sum(1 for r in results if r == 1)
    b_wins = sum(1 for r in results if r == -1)
    draws = sum(1 for r in results if r == 0)
    score = a_wins + 0.5 * draws            # A's win-equivalent
    wr = score / n
    lb = wilson_lower(score, n)
    return {
        "a": spec_a, "b": spec_b, "n": n,
        "a_wins": a_wins, "b_wins": b_wins, "draws": draws,
        "winrate": round(wr, 4), "wilson_lb": round(lb, 4),
        "n_agents": n_agents,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--games", type=int, default=200)
    ap.add_argument("--procs", type=int, default=16)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--n_agents", type=int, default=2)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    res = run_match(args.a, args.b, args.games, args.procs,
                    args.seed, args.n_agents, args.steps)
    print(json.dumps(res, indent=2))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
