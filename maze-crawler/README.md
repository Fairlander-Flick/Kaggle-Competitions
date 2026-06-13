# Maze Crawler ("Crawl") — Kaggle Simulation Competition

**Competition:** https://www.kaggle.com/competitions/maze-crawler ·
**Type:** 2-player real-time-strategy *agent-vs-agent* simulation (episode skill-rating leaderboard) ·
**Deadline:** 2026-06-16 23:59 UTC · **Team:** Fairlander-Flick

A two-player maze game with fog of war. Each player starts with one indestructible
**Factory** in a 20-wide maze that **scrolls northward** over time, destroying anything
left behind the southern boundary. You submit a `main.py` containing `agent(obs, config)`;
Kaggle plays your agent against other submissions and ranks you by a skill rating.

> This folder is our full working record for the competition: the game analysis, the
> winning strategy, the agent code, the local evaluation harness (our "CV"), and the
> running log of what we tried. See [`STATE.md`](STATE.md) for "where we are right now".

---

## TL;DR — the one insight that decides the game

We read the **engine source** (`kaggle_environments/envs/crawl/crawl.py`) rather than just
the rules, and it collapses the whole game to a single objective:

> **The factory is indestructible against every non-factory unit. It dies *only* by
> scrolling off the southern boundary. So the entire competition reduces to
> _maximising how many steps your factory survives_ — whoever's factory scrolls off
> *later* wins the episode.**

Energy, robots, combat, mining — all secondary. They only matter for the tiebreak when
*both* factories survive to step 500 (or die on the same step), which is rare.

And surviving is a **razor's edge**: over 500 steps the maze scrolls ≈ **276 rows**, while
a factory climbs at most ≈ **275 rows** (it moves once every 2 turns = 0.5 rows/turn, plus
JUMP). So *near-perfect* climbing just barely survives; **every wasted turn ≈ one row of
deficit** and brings death forward by the endgame.

## The winning strategy — "channel rush"

Three mechanical facts from the engine drive our agent:

1. **North/south walls are *never* fixed** (only the E/W perimeter and the central mirror
   axis are). So a **Worker** can `REMOVE_NORTH` *every* wall in its column and carve a
   **perfectly straight vertical channel north, forever.**
2. **JUMP strictly dominates walking for climbing:** it moves 2 cells for the *same*
   move-cooldown as a 1-cell walk, and it **ignores walls**. (20-turn cooldown.)
3. **Cooldown off-by-one:** the engine *decrements* cooldowns at the start of a turn
   *before* executing, so an observed cooldown of `1` means **"ready to act this turn."**
   Gating jumps on `cd == 0` makes the factory *never jump when it actually could* — the
   single most damaging bug we found.

Our agent (`agent/main.py`, version **v6**):

- The **Factory** climbs straight north up the channel; **JUMPs to bypass** any wall the
  worker hasn't punched yet (using the correct `cd <= 1` readiness test); never steps off
  the north board edge; and spends *forced* non-climb turns on economy.
- A **Worker** is built leading the factory north and `REMOVE_NORTH`s walls to keep the
  channel open; the factory **TRANSFERs energy** north to keep the puncher funded.
- A **defensive wrapper** guarantees that any unexpected exception falls back to a safe
  greedy-north climb — *an unhandled exception is an instant episode loss.*

## How we measure (our "CV") — the measurement contract

Simulation has no train/test split, so [`eval/harness.py`](eval/harness.py) is our paired,
variance-aware evidence standard (§12.2 of the pipeline contract):

- play a candidate vs a **fixed opponent pool** over a **fixed seed set**, in **both**
  player slots (mirror-fair);
- report **win-rate**, `W-D-L`, a one-sided **z-score**, **mean survival depth**, and
  **reach-500 rate**;
- a change is accepted only if the win-rate delta clears significance **and** survival
  depth doesn't regress.

Opponent pool: `random` (the kaggle_environments built-in, a surprisingly decent
wall-punching climber), `starter` (the competition's `main.py`), and our own earlier
reference climbers.

## Results so far

| Version | Idea | Mirror survival depth (median) | vs `random` win-rate |
|---|---|---:|---:|
| `ref_climb` | greedy north + jump-when-blocked | 85 | — |
| `v5` | BFS pathfinding (detour around walls) | 205 | 0.40 |
| **`v6`** | **channel-rush + cooldown fix** | **342** | **0.79** |

(Local numbers; live leaderboard score is updated as games are played — see `STATE.md`.)

## Layout

```
maze-crawler/
  README.md          this file
  STATE.md           "where we are" — live progress / next steps / submission log
  writeup.md         full game analysis + strategy derivation
  agent/main.py      the submitted agent (v6)
  agent/v5.py        earlier BFS climber (kept as a pool baseline / for diffs)
  eval/harness.py    the measurement-contract evaluator
  eval/ref_climb.py  reference baseline opponent
  docs/              engine notes
```
