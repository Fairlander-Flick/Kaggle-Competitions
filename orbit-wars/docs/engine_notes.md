# Engine notes — `kaggle_environments/envs/orbit_wars/orbit_wars.py`

Line-by-line reading of the interpreter + its test suite (`test_orbit_wars.py`).
These are the facts the agent is built on; verified against the engine's own tests.

## Turn order (per `interpreter`)
1. Expire comets that left the board (removed *before* launches — can't act on them).
2. Spawn comet groups at steps 50/150/250/350/450 (schedule seeded & **hidden** from agents).
3. **Fleet launch** — process every player's actions.
4. **Production** — every *owned* planet (incl. owned comets) `+= production`.
   **Neutral planets (owner −1) do NOT produce.**
5. **Fleet movement** — straight line at `v(n)`; continuous swept-collision check:
   planet first, then out-of-bounds, then sun. A fast fleet that would overshoot still
   resolves combat at a planet its segment crosses.
6. Planet rotation / comet advance (a moving body can sweep a fleet into combat).
7. **Combat resolution.**

## Combat (tests `test_combat_*`)
- All fleets arriving at a planet this tick are grouped by owner and **summed**.
- Largest force fights the second-largest: `survivors = top − second` (exact tie → all
  attackers destroyed, `survivors = 0`).
- Surviving attacker vs the planet garrison (which already grew by production this turn
  if owned/enemy):
  - same owner → **reinforce** (`garrison += survivors`);
  - different owner → `garrison −= survivors`; if it goes **strictly below 0**, the
    planet **flips** and the new garrison is the surplus. Sending *exactly* the garrison
    → garrison 0, **no flip**. ⇒ need `survivors > garrison_at_arrival`.

## Movement / geometry
- `v(n) = 1 + (shipSpeed−1)·(ln n / ln 1000)^1.5`, capped at `shipSpeed` (default 6);
  `n=1 → v=1`. Fleet `angle` fixed at launch; spawns just outside the source radius.
- Orbiting iff `dist_to_center(x,y) + radius < ROTATION_RADIUS_LIMIT (50)`.
  Future position: `angle_now = atan2(y−50, x−50)`, `angle(dt) = angle_now + av·dt`,
  on the same orbital radius. `av ∈ [0.025, 0.05]`, constant per game, in the obs.
- Sun at (50,50) r=10: a fleet whose segment passes within 10 of center is destroyed
  (unless it hit a planet earlier on the segment).
- Swept-pair collision (`swept_pair_hit`) treats both fleet and planet as linear over
  the tick — a fleet can be caught by a rotating planet even on a near-miss snapshot.

## Map generation
- 5–10 symmetric **groups of 4** (20–40 planets), 4-fold mirror about center; ≥3 groups
  guaranteed static, ≥1 guaranteed orbiting. `production ∈ [1,5]`, `radius = 1 + ln(prod)`.
- Neutral starting ships 5–99 skewed low (`min` of two rolls; outer groups 5–30).
- Home group chosen at random; 2p → diagonal seats (Q1 vs Q4); 4p → one seat each.
  Home planets start with **10 ships**. Every player's view is the same map rotated.

## Comets
- Groups of 4 (one/quadrant), elliptical, +1 production, radius 1.0, speed 4.0/turn.
- Appear in `planets` and `comets` (full `paths` + `path_index` → predictable once
  visible). They **vanish** off-board, taking their garrison with them ⇒ economic/tempo
  play only; capturing one late is wasted ships.

## Termination & reward
- Ends at step ≥ 498 (interpreter sees `episodeSteps − 2`) **or** ≤ 1 player alive
  (a player with no planets but a fleet still in flight is *not yet* eliminated).
- `reward = +1` if your score == max and max > 0, else −1; ties → all tied get +1.
  **Score = total ships on owned planets + ships in owned fleets.** Margin is irrelevant
  to the rating (win/loss/draw only).

## Agent I/O
- Called `agent(obs, config)`. `obs` keys: `player, planets, fleets, angular_velocity,
  initial_planets, comets, comet_planet_ids, next_fleet_id, step, remainingOverageTime`.
  `planets[i] = [id, owner, x, y, radius, ships, production]` (owner −1 = neutral).
  `fleets[i] = [id, owner, x, y, angle, from_planet_id, ships]`.
- Action: list of `[from_planet_id, angle_radians, num_ships]`; only from owned planets,
  `0 < ships ≤ garrison`; invalid moves silently dropped; **`actTimeout = 1 s`/turn**,
  with a `remainingOverageTime` bank (~60 s) for occasional overruns.
- The episode **seed is scrubbed** from the config agents see (so the comet schedule and
  exact map RNG can't be reconstructed), but is recorded in the replay.
