"""Measurement contract for the Crawl sim spine (§12.2).

Plays a candidate agent vs an opponent over a FIXED seed set, BOTH player slots,
reports win_rate, (W-D-L), mean factory survival depth, reach-500 rate, and a
one-sided z-score vs 0.5 (and vs an incumbent if given). CPU-parallel.
"""
import argparse, importlib.util, math, os, sys, warnings, statistics
from concurrent.futures import ProcessPoolExecutor
warnings.filterwarnings("ignore")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "agent_src")
DATA = os.path.join(ROOT, "data")


def load_agent(spec):
    """spec: 'random' | path to .py with agent() | 'name' in agent_src/<name>.py"""
    if spec == "random":
        return "random"
    if spec == "starter":
        return os.path.join(DATA, "main.py")
    if spec.endswith(".py") and os.path.exists(spec):
        path = spec
    else:
        path = os.path.join(SRC, spec + ".py")
    return path  # pass file path to env.run (isolated, mimics real submission)


def _play(args):
    seed, a_spec, b_spec, swap = args
    import warnings; warnings.filterwarnings("ignore")
    from kaggle_environments import make
    a = load_agent(a_spec); b = load_agent(b_spec)
    p0, p1 = (b, a) if swap else (a, b)
    env = make("crawl", configuration={"randomSeed": seed}, debug=False)
    env.run([p0, p1])
    last = env.steps[-1]
    r0, r1 = last[0]["reward"], last[1]["reward"]
    # candidate is at slot (1 if swap else 0)
    cand_slot = 1 if swap else 0
    rc = r1 if swap else r0
    ro = r0 if swap else r1
    if rc > ro:
        res = 1.0
    elif rc < ro:
        res = 0.0
    else:
        res = 0.5
    return res, len(env.steps)


def evaluate(cand, opp, seeds, workers):
    jobs = []
    for s in seeds:
        jobs.append((s, cand, opp, False))
        jobs.append((s, cand, opp, True))
    if workers <= 1:
        out = [_play(j) for j in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            out = list(ex.map(_play, jobs))
    results = [o[0] for o in out]
    steps = [o[1] for o in out]
    n = len(results)
    wr = sum(results) / n
    w = sum(1 for r in results if r == 1.0)
    d = sum(1 for r in results if r == 0.5)
    l = sum(1 for r in results if r == 0.0)
    # one-sided z vs 0.5 (binomial, draws count as 0.5)
    se = math.sqrt(0.25 / n)
    z = (wr - 0.5) / se if se > 0 else 0.0
    return {
        "opp": opp, "n": n, "winrate": wr, "W": w, "D": d, "L": l, "z_vs_0.5": z,
        "mean_steps": statistics.mean(steps), "reach500": sum(1 for s in steps if s >= 500) / n,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", required=True)
    ap.add_argument("--opps", nargs="+", default=["random", "starter", "ref_climb"])
    ap.add_argument("--nseeds", type=int, default=50)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    args = ap.parse_args()
    seeds = list(range(args.seed0, args.seed0 + args.nseeds))
    print(f"# cand={args.cand} nseeds={args.nseeds} workers={args.workers}")
    print(f"{'opp':<12} {'n':>4} {'winrate':>8} {'W-D-L':>12} {'z':>6} {'msteps':>7} {'r500':>6}")
    overall = []
    for opp in args.opps:
        r = evaluate(args.cand, opp, seeds, args.workers)
        overall.append(r["winrate"])
        print(f"{opp:<12} {r['n']:>4} {r['winrate']:>8.3f} "
              f"{str(r['W'])+'-'+str(r['D'])+'-'+str(r['L']):>12} {r['z_vs_0.5']:>6.2f} "
              f"{r['mean_steps']:>7.1f} {r['reach500']:>6.2f}")
    print(f"# POOL mean winrate = {statistics.mean(overall):.3f}")


if __name__ == "__main__":
    main()
