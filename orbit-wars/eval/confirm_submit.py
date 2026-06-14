"""
CONFIRM a candidate (evolved params or a bot file) on a FRESH seed set vs the full
gauntlet + incumbent, gate with Wilson LB (§5.1/§5.2 confirm stage), and — only if it
passes — bake a standalone submission main.py and submit to Kaggle.

This is the ship gate. Screen-stage tuning numbers are NEVER submitted directly.

  python eval/confirm_submit.py --params artifacts/tuning/island_3/best_params.json \
         --games 200 --procs 16 [--submit] [--msg "Orbiter v2 ..."]
  python eval/confirm_submit.py --bot bots/orbiter_mc.py --games 200 [--submit]
"""
import argparse, json, os, re, subprocess, sys, time, warnings
warnings.filterwarnings("ignore")
RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RUN)
from eval.league import run_match

# fresh seeds, disjoint from tuning (tuning uses 1000 + gen*131 and +5000 for 4p)
CONFIRM_BASE_SEED = 900000
GAUNTLET_2P = ["arch:rusher", "arch:turtle", "arch:expander", "arch:comet", "pool:sniper", "pool:starter"]
GAUNTLET_4P = ["arch:rusher", "arch:expander"]
INCUMBENT = "orbiter"          # the bot currently on the ladder (v1 defaults)


def spec_for(args):
    if args.bot:
        return f"file:{args.bot}", None
    if args.params:
        return f"orbiter:{os.path.abspath(args.params)}", args.params
    raise SystemExit("need --params or --bot")


def confirm(spec, games, procs):
    rows = []
    print(f"== CONFIRM {spec} (fresh seeds, {games} games/opp) ==", flush=True)
    # head-to-head vs the incumbent first (the key accept gate)
    r = run_match(spec, INCUMBENT, games=games, procs=procs,
                  base_seed=CONFIRM_BASE_SEED, n_agents=2)
    rows.append(("vs-incumbent(2p)", r))
    for opp in GAUNTLET_2P:
        r = run_match(spec, opp, games=games, procs=procs,
                      base_seed=CONFIRM_BASE_SEED + 100, n_agents=2)
        rows.append((f"{opp}(2p)", r))
    for opp in GAUNTLET_4P:
        r = run_match(spec, opp, games=games, procs=procs,
                      base_seed=CONFIRM_BASE_SEED + 200, n_agents=4)
        rows.append((f"{opp}(4p)", r))
    print(f"{'matchup':24s} {'winrate':>8s} {'wilsonLB':>9s}  n")
    for name, r in rows:
        print(f"{name:24s} {r['winrate']:>8.3f} {r['wilson_lb']:>9.3f}  {r['n']}")
    inc = rows[0][1]
    # PASS: beats incumbent with Wilson LB clearly > 0.5, and no archetype crushes us
    beats_inc = inc["wilson_lb"] > 0.53
    worst_arch = min(r["winrate"] for n, r in rows[1:5])  # the 4 archetypes
    robust = worst_arch > 0.40
    verdict = beats_inc and robust
    print(f"\nVERDICT: beats_incumbent(LB>0.53)={beats_inc} (LB={inc['wilson_lb']:.3f}) "
          f"robust(worst_arch>0.40)={robust} (worst={worst_arch:.3f}) => "
          f"{'PASS — ship it' if verdict else 'FAIL — keep tuning'}", flush=True)
    return verdict, rows


def bake_main(params_path, out_path):
    """Generate a standalone submission main.py = orbiter.py with PARAMS overridden."""
    src = open(os.path.join(RUN, "bots", "orbiter.py")).read()
    with open(params_path) as f:
        p = json.load(f)
    override = "\n# --- tuned params (baked at submission) ---\nPARAMS.update(%r)\n" % (p,)
    # insert the override right before the final default-agent line
    marker = "\n# default agent for submission"
    src = src.replace(marker, override + marker, 1)
    open(out_path, "w").write(src)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params"); ap.add_argument("--bot")
    ap.add_argument("--games", type=int, default=200)
    ap.add_argument("--procs", type=int, default=16)
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--msg", default=None)
    args = ap.parse_args()
    spec, params_path = spec_for(args)
    verdict, rows = confirm(spec, args.games, args.procs)
    if not verdict:
        print("Not submitting (did not pass the gate).")
        return
    if not args.submit:
        print("PASS, but --submit not given; not submitting.")
        return
    # build submission file
    sub = os.path.join(RUN, "submit", "main.py")
    if params_path:
        bake_main(params_path, sub)
    else:
        import shutil; shutil.copy(args.bot, sub)
    inc_lb = rows[0][1]["wilson_lb"]
    msg = args.msg or f"Orbiter tuned: beats incumbent LB={inc_lb:.3f} vs gauntlet"
    env = dict(os.environ, KAGGLE_CONFIG_DIR=os.path.expanduser("~/.kaggle"),
               PYTHONIOENCODING="utf-8")
    print(f"submitting {sub} ...", flush=True)
    out = subprocess.run(["kaggle", "competitions", "submit", "orbit-wars",
                          "-f", sub, "-m", msg], env=env, capture_output=True, text=True)
    print(out.stdout.strip()[-500:]); print(out.stderr.strip()[-300:])


if __name__ == "__main__":
    main()
