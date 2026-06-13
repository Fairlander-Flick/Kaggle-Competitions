# STATE — where we are (maze-crawler)

_Live "you are here" for the campaign. Newest at top._

## Status @ 2026-06-13

- **Deadline:** 2026-06-16 23:59 UTC (T-3 days). 444 teams. LB #1 ≈ 2079.
- **Current agent:** **v6** (`agent/main.py`) — channel-rush climber. **Submitted**
  (submission `main.py`, 2026-06-13 13:55). Awaiting live rating.
- **Prior submissions** (from an earlier session whose local code was LOST): v0 925, v2 960,
  v3 **1068** (best so far), v4 945. v6 is far stronger locally and should pass v3.
- **Local eval (measurement contract, 100 games/opp):** v6 pool-mean win-rate **0.877**;
  vs `random` 0.835 (z=6.7), vs `v5` 0.86, vs `ref_climb` 0.98. Mirror survival depth
  median **342** (v5 was 205, ref_climb 85).

### Campaign infra (on the HPC `$WORK`, not in git)
- Working dir: `$WORK/kaggle/maze-crawler-run/` (context.md, agent_src/, eval/, artifacts/).
- Env: conda `kaggle` (`/home/woody/.../envs/kaggle/bin/python`), `kaggle-environments` installed.
- Eval is CPU + embarrassingly parallel; runs on frontend cores (16) in ~1–2 min for 400 games.

## Next steps (ranked)
1. **Watch the live rating** of v6 (`kaggle competitions submissions maze-crawler`,
   `kaggle competitions leaderboard maze-crawler -s`). Pull a replay/logs of a *loss* to see
   how the field beats us (`kaggle competitions episodes <subid>` → `replay` / `logs`).
2. **v7 — energy economy:** build a Miner → Mine early to fund *continuous* wall-punching so
   the channel stays straight past step ~300 (current bankroll runs out there). Accept only
   via the harness with a significance gate vs v6.
3. **v7 — endgame jump squeeze:** reach-500 is still 0; maximise survival in steps 400–500.
4. Keep v6 as the incumbent in the opponent pool; every new version must beat it (z-gated).

## Submission log
| date | file | idea | local vs-random | public score |
|---|---|---|---:|---|
| 2026-06-13 | v6 main.py | channel-rush + cooldown fix | 0.835 (z=6.7) | _pending_ |
| 2026-06-12 | main_v4.py | ascend-only mining | — | 945 |
| 2026-06-12 | main_v3.py | survival pack | — | **1068** |
| 2026-06-12 | main_v2.py | mine-economy | — | 960 |
| 2026-06-12 | main_v0.py | public jpbfs | — | 925 |

## Known facts / gotchas (don't relearn these)
- Factory dies ONLY by scrolling off / walking off an edge. Game = survive longest. (writeup §2)
- North/south walls are never fixed → a worker carves a straight channel. (writeup §4)
- **Cooldown off-by-one:** observed `cd <= 1` means ready THIS turn. (writeup §5)
- An unhandled exception in `agent()` = instant episode loss → keep the try/except guard.
- `actTimeout = 3 s`/turn (generous); our agent uses ~8 ms/turn.
