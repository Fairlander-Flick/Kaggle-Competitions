# Orbit Wars — Kaggle Simulation Competition

**Competition:** https://www.kaggle.com/competitions/orbit-wars ·
**Type:** 2-/4-player real-time-strategy *agent-vs-agent* simulation (TrueSkill ladder) ·
**Deadline:** 2026-06-23 23:59 UTC · **Prize:** $50,000 · **Team:** Fairlander-Flick

A reboot of the 2010 **Planet Wars** challenge in **continuous 2D space**. A sun sits
at the center of a 100×100 board; planets (some orbiting the sun, some static) produce
ships each turn; you launch fleets in straight lines to capture neutral and enemy
planets. The game lasts 500 turns and **whoever has the most total ships (on planets +
in flight) at the end wins** — or you win instantly by eliminating everyone. You submit
a `main.py` with `agent(obs, config)`; Kaggle plays it against other submissions and
ranks you by a skill rating (μ, σ).

> This folder is our full working record: the engine analysis, the strategy, the agent
> code, the local self-play league (our "CV"), and the running log. See
> [`STATE.md`](STATE.md) for "where we are right now" and [`docs/engine_notes.md`](docs/engine_notes.md)
> for the line-by-line engine reading.

---

## TL;DR — the structure that decides the game

We read the **engine source** (`kaggle_environments/envs/orbit_wars/orbit_wars.py`),
not just the rules. Five mechanics drive everything:

1. **Neutral planets do not produce.** Only *owned* planets grow (by `production`,
   1–5/turn, applied every turn before combat). So a neutral is a **fixed one-time
   cost**, while an **enemy garrison grows during your fleet's flight** — you must size
   the fleet against the garrison *at arrival* (`ships_now + production·ETA + 1`),
   not the garrison you see now. The starter/sniper bots ignore this and arrive short.

2. **Orbits are deterministic and readable.** An orbiting planet's future angle is
   `atan2(y−50, x−50) + angular_velocity·dt` (a planet orbits iff
   `dist_to_center + radius < 50`). So we **lead moving targets** (solve for the
   intercept point) instead of firing at the stale position — the naive bots miss
   orbiting planets entirely, which is why the *starter* bot only ever targets static ones.

3. **Fleet speed scales with size:** `v(n) = 1 + 5·(ln n / ln 1000)^1.5`, capped at 6;
   a 1-ship fleet crawls at speed 1. **Concentrate force** — dribbles are slow *and*
   each must independently beat the garrison.

4. **Collision is continuous (swept).** A fleet that crosses the sun (r=10) or grazes
   *any* planet mid-flight is consumed / dragged into combat there. We keep launch
   lines **clear of the sun and of unintended planets**.

5. **Capture needs a *strict* majority** (survivors `>` garrison; equal = no flip), and
   **eliminating all opponents ends the game as an instant win**. Score margin never
   affects the rating — only win/loss/draw.

The real objective reduces to an **economic growth race**: total end-ships ≈ the integral
of owned production over 500 turns. So grab high-`production`, low-garrison, nearby
planets *early* and hold them, while denying the enemy.

## The agent — "Orbiter"

[`agent/main.py`](agent/main.py) is a fast (<10 ms/turn vs a 1 s limit) heuristic with a
forward-model-correct core, wrapped so any exception degrades to "do nothing" (an
unhandled exception is an instant episode loss):

- **Interception solver** — fixed-point iterate launch-angle ↔ ETA ↔ fleet-speed so the
  fleet arrives where an orbiting target *will be*.
- **Production-aware capture sizing** — fleet size = garrison-at-arrival + margin, with
  enemy growth `production·ETA` folded in; neutrals sized at their fixed garrison.
- **EV target selection** — value `≈ production^a · hold_time / (cost + b·ETA)`, with a
  denial bonus on enemy planets and a discount on (vanishing) comets.
- **Path clearance** — reject launches whose straight line crosses the sun or grazes a
  non-target planet between the endpoints.
- **Defense reserve** — keep a fraction of each planet's ships home, raised when an
  enemy fleet is aimed at it.

Every behaviour is governed by a `PARAMS` weight vector → tuned by self-play (below).

> **Debugging note (the bug that mattered):** the first version made **zero launches**
> and lost to *every* baseline. Cause: the path-clearance check treated the fleet's own
> source planet (the segment's start point) as an obstacle, so *every* line was "blocked".
> Fix: only block planets whose closest approach is in the *middle* of the segment
> (param `t ∈ (0.02, 0.99)`), skipping source and target. Result: 2% → 90% vs the sniper.
> This is the simulation analogue of a silent CV-inflating bug — caught only because the
> league measured it.

## How we measure — the local self-play league (our "CV")

[`eval/league.py`](eval/league.py) + [`eval/baselines.py`](eval/baselines.py). A match is
N **fixed seeds**, each played **twice with seats swapped** to cancel position bias; a
draw counts 0.5; we report the **Wilson 95% lower bound** on the win-rate. A new version
is accepted only if its Wilson LB beats 0.5 (vs the fixed pool *and* the current
incumbent) by a real margin — never on a raw win-rate point estimate. The game is
CPU-bound and embarrassingly parallel, so the league fans out across the cluster's cores.

```bash
python eval/league.py --a orbiter --b pool:sniper --games 200 --procs 16
```

### Results (Orbiter v1, 100 games/opponent unless noted)

| opponent | 2-player win-rate (Wilson LB) | 4-player win-rate (vs 25% baseline) |
|----------|-------------------------------|-------------------------------------|
| random   | **1.00** (0.96) | — |
| starter  | **0.87** (0.79) | 0.73 vs 3×starter |
| sniper   | **0.90** (0.83) | 0.72 vs 3×sniper |

## The plan (using the HPC)

This is a strategy game with a known competitive lineage (Planet Wars / Galcon), run on
an NHR@FAU cluster with abundant CPU. The compute goes where it wins rank:

1. **Orbiter v1 on the ladder** (done) — a strong, robust baseline for early rating feedback.
2. **24/7 CMA-ES tuning league** — evolve the `PARAMS` vector via massive parallel
   self-play (SLURM array jobs), each candidate generation gated by the measurement
   contract. This *is* the "learning", with far better sample-efficiency than RL from
   scratch and zero timeout risk.
3. **Strategy depth** — loss-replay analysis → defense, multi-planet staging, comet
   timing, opening books; each change accepted only through the league.
4. **Escalation** — a tiny evolved-NN policy *only if* the heuristic+tuning plateaus.

Run state (data, replays, evolved params, league logs) lives on the cluster `$WORK`, not
in git. This folder tracks the code + analysis + decisions.
