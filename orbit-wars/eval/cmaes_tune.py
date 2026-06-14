"""
CMA-ES self-play tuner for Orbiter PARAMS — the campaign's 24/7 "learning" engine.

Each candidate parameter vector is scored by win-equivalent rate vs a fixed opponent
set (sniper, starter, and the frozen incumbent Orbiter) across 2p and 4p, on COMMON
random seeds within a generation (variance reduction; seeds rotate per generation to
avoid seed-overfit). All candidate×game tasks for a generation are mapped on ONE
multiprocessing Pool so every core stays saturated.

Checkpoints CMA state + best params every generation; resumes from the checkpoint.
Exits cleanly before the SLURM walltime so a requeue continues seamlessly.

Run:  python eval/cmaes_tune.py --procs 64 --pop 16 --games2p 30 --games4p 24 \
                               --walltime_h 23.5 --out artifacts/tuning
"""

import argparse, json, os, pickle, sys, time, warnings
from multiprocessing import Pool

warnings.filterwarnings("ignore")
RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RUN_DIR)
from bots.orbiter import PARAMS
from eval.league import _play_params

# (name, lo, hi, is_int) — the tunable subset of PARAMS
TUNE = [
    ("reserve_frac",        0.0,  0.6,  False),
    ("reserve_min",         0.0,  10.0, False),
    ("capture_margin",      0.0,  8.0,  False),
    ("capture_margin_frac", 0.0,  0.30, False),
    ("prod_weight",         0.5,  3.0,  False),
    ("dist_weight",         0.0,  3.0,  False),
    ("cost_weight",         0.2,  3.0,  False),
    ("enemy_bonus",         0.7,  2.5,  False),
    ("comet_penalty",       0.1,  1.2,  False),
    ("neutral_bias",        0.5,  2.0,  False),
    ("max_launches",        2,    14,   True),
    ("min_fleet",           1,    8,    True),
    ("endgame_turn",        400,  498,  True),
    ("sun_margin",          0.5,  5.0,  False),
    ("graze_margin",        0.0,  3.0,  False),
    ("defense_tol",         0.05, 0.8,  False),
    ("threat_reserve",      0.8,  1.6,  False),
    ("max_eta",             60.0, 300.0,False),
]

# STRONG + DIVERSE gauntlet (anti-overfit): diverse archetypes + the frozen incumbent,
# plus the two trivial baselines as a floor. Tuning that beats THIS generalises.
OPP_2P = ["arch:rusher", "arch:turtle", "arch:expander", "arch:comet",
          "orbiter", "pool:sniper"]
OPP_4P = ["arch:rusher", "arch:expander"]


def decode(x):
    """normalized [0,1] vector -> params dict overlay."""
    p = {}
    for xi, (name, lo, hi, is_int) in zip(x, TUNE):
        xi = min(1.0, max(0.0, xi))
        v = lo + xi * (hi - lo)
        p[name] = int(round(v)) if is_int else float(v)
    return p


def encode_default():
    x = []
    for name, lo, hi, is_int in TUNE:
        v = PARAMS[name]
        x.append((v - lo) / (hi - lo) if hi > lo else 0.5)
    return x


def gen_tasks(cand_params, base_seed, g2p, g4p):
    tasks = []
    for spec in OPP_2P:
        for i in range(g2p // 2):
            s = base_seed + i
            tasks.append((cand_params, spec, s, 0, 2, 500))
            tasks.append((cand_params, spec, s, 1, 2, 500))
    for spec in OPP_4P:
        for i in range(g4p // 2):
            s = base_seed + 5000 + i
            tasks.append((cand_params, spec, s, 0, 4, 500))
            tasks.append((cand_params, spec, s, 1, 4, 500))
    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=64)
    ap.add_argument("--pop", type=int, default=16)
    ap.add_argument("--games2p", type=int, default=30)
    ap.add_argument("--games4p", type=int, default=24)
    ap.add_argument("--walltime_h", type=float, default=23.5)
    ap.add_argument("--sigma", type=float, default=0.22)
    ap.add_argument("--seed", type=int, default=12345)   # island diversity
    ap.add_argument("--out", default=os.path.join(RUN_DIR, "artifacts", "tuning"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    ckpt = os.path.join(args.out, "cma_state.pkl")
    best_path = os.path.join(args.out, "best_params.json")
    log_path = os.path.join(args.out, "tuning_log.csv")
    deadline = time.time() + args.walltime_h * 3600

    import cma
    if os.path.exists(ckpt):
        with open(ckpt, "rb") as f:
            es, best = pickle.load(f)
        print(f"[resume] gen={es.countiter} best_fit={best['fit']:.4f}", flush=True)
    else:
        es = cma.CMAEvolutionStrategy(
            encode_default(), args.sigma,
            {"bounds": [0, 1], "popsize": args.pop, "seed": args.seed,
             "verbose": -9},
        )
        best = {"fit": -1e9, "params": dict(PARAMS), "gen": 0}
        with open(log_path, "w") as f:
            f.write("gen,wall_s,best_fit_gen,mean_fit_gen,global_best_fit\n")

    pool = Pool(args.procs)
    try:
        while not es.stop() and time.time() < deadline:
            t0 = time.time()
            sols = es.ask()
            base_seed = 1000 + es.countiter * 131       # rotate CRN seeds per gen
            # build all candidate tasks, tag with candidate index
            all_tasks, owners = [], []
            cand_params = [decode(x) for x in sols]
            for ci, cp in enumerate(cand_params):
                ts = gen_tasks(cp, base_seed, args.games2p, args.games4p)
                all_tasks.extend(ts)
                owners.extend([ci] * len(ts))
            results = pool.map(_play_params, all_tasks, chunksize=4)
            # aggregate win-equiv per candidate
            agg = [[0, 0] for _ in sols]   # [score_sum, n]
            for r, ci in zip(results, owners):
                agg[ci][0] += 1 if r == 1 else (0.5 if r == 0 else 0.0)
                agg[ci][1] += 1
            fits = [(sc / n) for sc, n in agg]            # win-equiv in [0,1]
            es.tell(sols, [-f for f in fits])             # cma minimizes
            gi = max(range(len(fits)), key=lambda i: fits[i])
            if fits[gi] > best["fit"]:
                best = {"fit": fits[gi], "params": cand_params[gi],
                        "gen": es.countiter}
                with open(best_path, "w") as f:
                    json.dump(best["params"], f, indent=2)
            with open(ckpt, "wb") as f:
                pickle.dump((es, best), f)
            with open(log_path, "a") as f:
                f.write(f"{es.countiter},{time.time()-t0:.1f},"
                        f"{fits[gi]:.4f},{sum(fits)/len(fits):.4f},{best['fit']:.4f}\n")
            print(f"gen {es.countiter:4d} | best_gen {fits[gi]:.3f} "
                  f"mean {sum(fits)/len(fits):.3f} | global_best {best['fit']:.3f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
    finally:
        pool.close(); pool.join()
        with open(ckpt, "wb") as f:
            pickle.dump((es, best), f)
    print(f"[done] global_best_fit={best['fit']:.4f} gen={best['gen']} "
          f"-> {best_path}", flush=True)


if __name__ == "__main__":
    main()
