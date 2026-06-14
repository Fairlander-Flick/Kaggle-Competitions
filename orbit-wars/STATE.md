# STATE — where we are (orbit-wars)

_Live "you are here". Newest at top. Full invariants/log on the cluster `$WORK`
(`kaggle/orbit-wars-run/context.md`, `SESSION_SUMMARY.md`)._

## Status @ 2026-06-14 (T-9 days, deadline 2026-06-23 23:59 UTC)

- **Champion = `agent/main.py` = Orbiter-MC (forward-model Monte-Carlo SEARCH).** Submitted
  as our 2nd agent (sub 53665873). Each turn it generates candidate full-turn action-sets
  (greedy heuristic + 7 "mood" variants + idle), rolls each forward ~14 turns through a
  compact EXACT-engine simulator (both sides play the greedy policy), scores by an economic
  eval, and picks the best — within the 1 s/turn budget (worst 0.84 s; adaptive horizon).
- **It beats everything we have:** vs the v1 heuristic 100% (2p) / 92% (4p); vs the `rusher`
  archetype 65% (2p) / 54% (4p) — the rusher had beaten *both* v1 and the aggressive
  `orbiter2` rewrite. Search handles 2p (aggression) and 4p (survival) natively, which a
  single heuristic param-set could not.
- v1 (sub 53649581) settled at ladder μ≈533; field top ≈1807. Watching v2 climb.

### What we learned (the iteration that mattered)
1. **v1 was too passive** — replay intel (`docs/intel_report.md`) showed top bots issue ~560
   launches/game vs our 17-130; we froze hoarding 300-400 idle ships. 
2. **But pure throughput is a trap** — the aggressive `orbiter2` rewrite won 2p (0.73 vs v1)
   yet collapsed in 4p (0.18) by over-extending. Throughput is a *correlate* of having many
   planets, not a cause of winning.
3. **Forward-model search wins** — evaluating the actual consequences of moves (not a fixed
   policy) is robust across 2p/4p and beats aggressive archetypes. This is the champion.

### Campaign infra (on the cluster `$WORK`, not in git)
- **832 cores / 12 CMA-ES islands** tuning the heuristic vs a strong+diverse gauntlet
  (`rusher/turtle/expander/comet` + incumbent), on TinyFat (CPU: 128-core `work` + 24-core
  `long256`, self-requeue to deadline). Global-best ~0.91-0.94 vs the strong gauntlet.
  The tuned heuristic doubles as a better rollout policy for the search bot.
- Harness `eval/league.py` (Wilson-LB gate), gauntlet `eval/archetypes.py`, tuner
  `eval/cmaes_tune.py`, ship-gate `eval/confirm_submit.py`.

## Next steps (ranked)
1. Watch v2's ladder rating + **timing** (timeout = instant loss; lower `time_budget` if it ERRORs).
2. **Tune Orbiter-MC's own params** (horizon, eval weights, candidate moods) — biggest lever left.
3. Feed best island heuristic params into the MC rollout policy (synergy).
4. S5 loss-replay analysis on v2's ladder games → next refinements; deeper search if budget allows.
