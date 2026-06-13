# STATE — where we are (orbit-wars)

_Live "you are here". Newest at top. Full invariants/log on the cluster `$WORK`
(`kaggle/orbit-wars-run/context.md`)._

## Status @ 2026-06-13 (T-10 days)

- **Deadline:** 2026-06-23 23:59 UTC (then ~2 weeks of games → final LB). $50k, ~4407 teams.
- **Current agent:** **Orbiter v1** (`agent/main.py`) — heuristic core (intercept lead,
  production-aware capture sizing, EV target selection, path clearance, defense reserve).
  **Submitted** 2026-06-13 (sub `53649581`), status PENDING (validation episode). Awaiting rating.
- **Local league:** 2p win-rate 1.00 / 0.87 / 0.90 vs random / starter / sniper;
  4p ~0.72 vs 3-bot pools. (<10 ms/turn vs the 1 s limit.)
- **Engine:** fully read; key facts in [`docs/engine_notes.md`](docs/engine_notes.md).

### Campaign infra (on the cluster `$WORK`, not in git)
- Run dir: `$WORK/kaggle/orbit-wars-run/` (`bots/orbiter.py`, `eval/`, `submit/main.py`,
  `context.md`, `SESSION_SUMMARY.md`, `jobs/`, `logs/`, `artifacts/`).
- Env: conda `kaggle` (`$WORK/software/private/conda/envs/kaggle/bin/python`),
  `kaggle-environments` with the `orbit_wars` engine. CPU-bound, embarrassingly parallel.
- Cluster: TinyGPU frontend `tinyx`, SLURM suffix `.tinygpu`; self-play fans out over
  64–128-core nodes (`work`/`rtx3080`/`a100` partitions).

## Next steps (ranked)
1. **Watch the live rating** of Orbiter v1 (`kaggle competitions submissions orbit-wars`,
   `kaggle competitions leaderboard orbit-wars -s`). Snapshot rank/μ into context.md.
2. **24/7 CMA-ES tuning league** — evolve `PARAMS` via parallel self-play vs the fixed
   pool + incumbent; accept generations only through the Wilson-LB gate.
3. **Loss-replay analysis** (`kaggle competitions episodes <subid>` → `replay`/`logs`):
   see how the field beats us → next-version hypotheses (defense, staging, comets, openings).
4. Keep v1 as a frozen incumbent in the opponent pool; every new version must beat it.
