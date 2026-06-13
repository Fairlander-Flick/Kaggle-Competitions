# Maze Crawler — full game analysis & strategy derivation

This is the reasoning trail behind the agent, derived by reading the **engine source**
(`kaggle_environments/envs/crawl/crawl.py`), not just the published rules.

## 1. What kind of game is this, really?

Two players, a 20-wide maze with **east/west mirror symmetry** and a central wall axis
(occasional doors). Each starts with one **Factory**. The maze **scrolls north**: the
southern boundary advances over time and destroys everything below it. Fog of war.

Submission = a `main.py` with `agent(obs, config)` returning `{robot_uid: action}`.
Kaggle plays your agent against the field; the leaderboard is a skill rating.

## 2. The decisive structural facts (from the engine)

1. **The factory is indestructible** against every non-factory unit (crush table: Factory >
   Miner > Worker > Scout; the factory simply survives and crushes anything it meets). The
   *only* ways a factory dies are: (a) it scrolls below the southern boundary, or (b) it
   walks/jumps off the north or south board edge. Enemy units **cannot kill your factory.**
2. **Reward / win:** an *eliminated* player gets `step_eliminated − 502` (very negative); the
   survivor gets its total energy (positive). So **dying later wins.** If both survive to
   step 500, or both die the same step, a tiebreak cascades **total energy → unit count →
   draw**.
3. **The scroll vs the climb is a near-tie.** `get_scroll_interval` ramps the scroll from
   1-per-4-turns to 1-per-turn by step 400. Integrating it, the south boundary advances
   ≈ **276 rows** over 500 steps. A factory moves once every **2** turns (0.5 rows/turn) and
   can **JUMP** (+2, 20-turn cooldown), for a max climb ≈ **275 rows**. So **surviving to
   step 500 is a razor's edge** — near-perfect climbing barely makes it, and every wasted
   turn brings death forward.

**Conclusion:** energy, mining, combat, scouting are *secondary*. The game is, to first
order, **a solo northward-survival race**: maximise the step at which your factory finally
scrolls off. The symmetric maze means both players face equivalent terrain, so it comes
down to pure climbing efficiency.

## 3. Why naive climbers die

- **Greedy "always go north"** walks the factory **off the north board edge** the moment it
  reaches the top of the window → instant death. Fix: only move north while
  `row < northBound`.
- **Greedy north then idle** gets **trapped in maze dead-ends**: a cell walled on N/E/W
  (`wall == 11`) forces the factory to sit idle for up to 20 turns waiting for JUMP, while
  the scroll eats its buffer.
- **BFS detour around walls** (our `v5`) avoids dead-ends but **loses the race to lateral
  drift** — wandering sideways along a wall-shelf to find a gap costs rows.

## 4. The winning primitive: a worker-carved channel

The key engine detail: **`is_fixed_wall` only protects E/W walls** (the perimeter and the
central mirror axis). **North/south walls are never fixed.** Therefore a **Worker** can
`REMOVE_NORTH` *every* wall in its column and carve a **dead-straight vertical channel
north, indefinitely.** The factory then climbs that channel at the full walk rate without
ever detouring or idling in a dead-end — optimal walking climb — and **JUMPs to leap over
any wall the worker hasn't punched yet** (jump ignores walls).

This is strictly better than detouring, and it's exactly why the built-in `random` agent
(which builds one wall-removing worker) out-climbs a pure greedy climber.

### Funding the channel
`REMOVE_NORTH` costs 100 energy; a worker spawns with only 200. So a lone worker punches
~1–2 walls and stalls. The factory (1000 starting energy, unlimited cap, +crystals along
the way) **`TRANSFER_NORTH`s energy** to the lead worker to keep it punching. Economy
actions are taken preferentially on turns the factory *couldn't climb anyway*.

## 5. The single most damaging bug — cooldown off-by-one

The engine's **Phase 0 decrements move/jump/build cooldowns at the start of every turn,
before actions execute.** So the cooldown values in the *observation* are **pre-tick**: an
observed cooldown of `1` becomes `0` and the unit **can act this turn**.

Gating the factory's JUMP on `move_cd == 0 and jump_cd == 0` therefore makes it **miss
every turn where it was actually ready** — the factory ends up pinned against a wall,
oscillating east/west, never jumping free, and the scroll kills it. Correct readiness test:

```python
can_jump = (move_cd <= 1) and (jump_cd <= 1) and (row <= northBound - 2)
```

Fixing this alone lifted mirror-match survival depth from **~199 → ~342** and the win-rate
vs `random` from ~0.45 → **0.835**.

## 6. Robustness: an exception is an instant loss

Kaggle scores a turn that raises as a forfeit. The agent wraps its logic in a `try/except`
that falls back to a **safe greedy-north + jump** climb on any error, so a latent bug can
never hand away an episode. (We were bitten once by a `NameError` that lost every game at a
fixed step — hence the guard.)

## 7. How we evaluate — the measurement contract

No train/test split exists, so our "CV" is a paired, variance-aware match protocol
(`eval/harness.py`): candidate vs a **fixed opponent pool** over a **fixed seed set**, in
**both** player slots, reporting win-rate, `W-D-L`, a one-sided z-score, mean survival
depth, and reach-500 rate. A change ships only if the win-rate delta clears significance
and survival depth doesn't regress — never on a single lucky seed.

### v6 vs pool (50 seeds × 2 slots = 100 games each)

| opponent | win-rate | W-D-L | z |
|---|---:|---:|---:|
| `random` (built-in) | 0.835 | 83-1-16 | 6.70 |
| `starter` (comp main.py) | 0.835 | 83-1-16 | 6.70 |
| `ref_climb` (greedy) | 0.980 | 98-0-2 | 9.60 |
| `v5` (BFS detour) | 0.860 | 85-2-13 | 7.20 |
| **pool mean** | **0.877** | | |

## 8. Open levers (next versions)

- **Energy economy:** a **Miner** → **Mine** (50 energy/turn) early would fund *continuous*
  punching, keeping the channel perfectly straight deeper into the game (the current channel
  starves ~step 300 once the factory's 1000-energy bankroll is spent on transfers).
- **Endgame (steps 400–500, scroll 1/turn):** squeeze every jump; reach-500 is still 0, so
  the survival ceiling is the main prize.
- **Tiebreak insurance:** bank energy for the rare both-survive case.
