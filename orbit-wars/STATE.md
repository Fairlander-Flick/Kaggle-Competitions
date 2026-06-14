# STATE — where we are (orbit-wars)

_Live "you are here". Full invariants/log on the cluster `$WORK/kaggle/orbit-wars-run/`._

## Status @ 2026-06-14 — PARKED (strong bot submitted, plays passively on Kaggle)

Decision: ship our strongest agent and let Kaggle's servers grind the ladder (deadline
2026-06-23 + ~2 weeks of post-deadline games). HPC jobs stopped to free the cluster.

- **Submitted champion = `agent/main.py` = Orbiter-MC v3 (search + tuned policy)**
  (sub 53677385). Forward-model Monte-Carlo SEARCH (horizon 22 @ 0.72 s/turn, faster
  exact-engine sim) using the **832-core CMA-ES tuned heuristic** as its rollout +
  candidate policy. Self-contained (base64-embedded), worst turn ~0.84 s.
- Strength (local league): beats the prior MC champion **88% head-to-head**; vs the
  strong replay-derived gauntlet **0.83 (sg:swarm) / 0.92 (sg:econdef)** — the
  transfer-relevant opponents that previously beat us. Clear top of everything we built.
- Latest-2 (count for final): v3 tuned (53677385) + v2 fast (53676278). Both MC bots.

## How we got here (the iteration that worked)
1. Heuristic v1 → too passive (replay intel) ; aggressive rewrite (orbiter2) → 4p-weak.
2. **Forward-model search** (orbiter_mc) → robust 2p+4p, beat all our archetypes.
3. **Faster sim** → deeper search (horizon 14→22) at the same safe budget (orbiter_mc_fast).
4. **832-core CMA-ES** tuned the heuristic (vs a strong gauntlet) → much better policy.
5. **Combined** search + tuned policy = the champion. (Learned-eval path was rejected:
   slower AND weaker.)

## Honest outlook
Field top ≈1700; we started ~600. Winning #1 is a long shot (strong veteran teams +
the fixed 1 s/turn ladder limit — HPC tunes/tests offline but can't add per-turn compute).
A solid rank / medal zone is realistic as the bot climbs over the multi-week game period.

## To RESUME later (everything is preserved on $WORK)
- `SESSION_SUMMARY.md` + `context.md` in `$WORK/kaggle/orbit-wars-run/` have full state.
- Re-launch tuning: `sbatch.tinyfat jobs/cmaes_island.sbatch` (+ `_long.sbatch`).
- Next levers if resumed: harvest newer island bests into the rollout policy; pull the
  champion's ladder LOSS replays (`kaggle competitions episodes 53677385`) → S5 analysis;
  faster sim → deeper search; a learned eval done right (fast model).
