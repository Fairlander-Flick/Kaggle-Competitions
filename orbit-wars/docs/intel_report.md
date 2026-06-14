# Orbit Wars - Opponent Intel Report

**Date:** 2026-06-13
**Source:** 13 episode replays from our submission 53649581 (Orbiter v1), parsed by `intel/analyze.py`.
**Leaderboard:** top team Jake Will = 1807.5; we (Ugur Tasdan / Orbiter v1) scored 497.3 - near the bottom of the rated field.

Episodes pit us against the live ladder, so opponents here (ryu_to, sawasawasawa, Jmkelliher,
Daniel Bekker, Harshavardhana, Vinit, Fujii, Saurabh, Pranav Unni, etc.) are all stronger than us.
We won 4 of 12 contested episodes (one pure self-play 4p excluded).

---

## Headline numbers (winners vs losers, all players, all episodes)

| Metric (first 30 turns unless noted) | WINNERS | LOSERS |
|---|---|---|
| First launch turn | ~5 (med 4) | ~10 (med 6) |
| Opening launches (turns 0-30) | ~11 | ~8 |
| Opening ships committed | ~115 | ~67 |
| Planets owned by turn 30 | 3.2 | 2.3 |
| **Avg fleet size (whole game)** | **44.7** | **17.0** |
| **Total launches (whole game)** | **562** | **135** |
| Opening targets = neutrals | ~10 | ~7 |
| Opening targets = enemy | ~0.25 | ~0.6 |

The two metrics separating winners from losers most sharply: **total launch volume** (continuous
reallocation) and **average fleet size** (winners send big consolidated fleets; losers dribble or hoard).

## Where WE specifically fail (us vs the opponents who beat us)

| Metric | US (avg) | OPPONENTS who beat us |
|---|---|---|
| First launch turn | ~9-13 | ~1-7 (often turn 1-2) |
| Opening launches (0-30) | 3-5 | 8-29 |
| **Total launches / game** | **~17-130** | **200-3078** |
| Mid/late launch cadence (per 25 turns) | drops to **0-2** | stays **20-180** |
| Max single-planet garrison (hoarded, idle) | 315-399 | reallocated continuously |

**Our bot expands slowly, then freezes.** In every loss our launches/25-turns collapse to near zero
mid-game while we sit on 300-400 ship garrisons. Opponents never stop moving ships.

### Concrete loss case studies
- **vs Daniel Bekker (ep 79823253, lost):** by turn 100 he had 23 planets / 394 ship-planets / 1065
  ships-in-flight; we had 3 planets / 327 ships / 0 in flight. Cadence/25t `7,34,107,168,184` vs ours
  `2,6,3,6,0`. Out-expanded us 8x while we hoarded and stalled.
- **vs sawasawasawa (ep 79820417, lost):** turn-30 6 planets vs our 3; turn-100 **25 planets / 1667
  ships** vs our 7/765. Cadence `15,45,80,83,129` vs our `6,13,17,2,10`.
- **vs ryu_to (ep 79819705, lost):** first launch turn 2 vs our 3 (close start) but he kept launching
  `15,14,30,33,30` while we dropped to `12,13,20,1,7` - we stopped acting and lost.
- **vs Jmkelliher (ep 79820881, lost, 432 turns):** he also hoarded (975 garrison) but kept steady
  12-28 launches/25t all game and out-expanded us with bigger fleets.

### Where we DO win
We win only when the opponent is even more passive than us (Adaluvu spammed 209 tiny avg-12.7 fleets;
weak 4p fields). Our wins come from larger fleet size beating fragmented dribbling, not good expansion.

---

## What the strong bots do (synthesized strategy)

1. **Launch turn 1-2.** Top bots fire their first fleet on turn 1-2; they do not scout/wait.
2. **Aggressive neutral land-grab.** Opening launches target neutrals almost exclusively
   (winners ~10 neutral / ~0 enemy in first 30 turns). Prioritize cheap high-production neutrals and
   snowball. By turn 30 they hold 3-6 planets; by turn 100, 12-25.
3. **Continuous reallocation - never idle.** Defining trait: 200-600+ launches/game (Vinit: 3078).
   Every turn they push production from safe rear planets to the frontier; garrisons never pile up.
4. **Big consolidated strike fleets.** Avg fleet 38-145 for the strongest. They mass then send one
   decisive fleet (must satisfy `survivors > garrison_at_arrival`, engine notes Combat), not many
   small fleets that each fail to flip.
5. **Economy-first, fight late.** Almost no opening enemy-targeting; build production, then the
   accumulated economy crushes opponents late (300-1000+ ships-in-flight at turn 100).

---

## Prioritized recommendations for Orbiter v2 (do X because top bots do Y)

**P0 - Eliminate the mid-game freeze (biggest single lever).**
Our launches collapse to 0-2/25t mid-game while we sit on 300+ idle garrisons; top bots sustain
20-180/25t. Rule: any owned planet whose garrison exceeds (defense reserve + capture cost of its best
target) MUST launch every turn. Never let a rear planet hold >~50-80 idle ships when a forward target
or reinforcement exists. Target: raise total launches from ~50 to 300+/game.

**P1 - Launch on turn 1-2, not turn 9-13.**
First launch median in losses is turn ~9-13; top bots launch turn 1-2. Compute opening targets at
step 0 and fire immediately. Aim for first-launch <= turn 2 and >=3 neutral-capture fleets in first 5 turns.

**P2 - Faster neutral expansion; 5-6 planets by turn 30.**
Winners reach 3-6 planets by turn 30 and 12-25 by turn 100; we plateau at 2-3 / 3-8. Queue multiple
simultaneous neutral captures (best production-per-ship; exploit low-garrison outer neutrals, start 5-30).
Don't capture one neutral at a time.

**P3 - Size capture fleets correctly and keep them big.**
To flip: `survivors > garrison_at_arrival`, and garrison grows by production each turn in flight
(engine notes Combat). Send `current_garrison + production*eta + small_buffer`. Winners avg fleet ~40-45;
ours ~17-24. Stop sending undersized fleets that bounce off.

**P4 - Forward-chain reinforcement (snowball pipeline).**
Top bots constantly push rear production to the frontier (huge ships-in-flight late). Each turn, safe
rear planets ship surplus to nearest frontier/contested planet. Solves P0 and sustains pressure.

**P5 - De-prioritize comets and early enemy rushing.**
Winners almost never target the enemy in the opening (tgt_enemy ~0.25); comets are economic/tempo only
(vanish off-board with garrison, engine notes Comets). Spend the opening on neutrals.

---

## Method notes / caveats
- Authoritative state = player-0 observation each step (owner indices and ship counts are absolute and
  identical across all per-player views; only coordinates rotate). Per-player actions read from each
  step entry's `action` field. See `analyze.py`.
- Opening target classification (neutral/enemy/own) is approximate (matches launch angle to best-aligned
  planet from source) - good for aggregate trends, not exact per-fleet truth.
- 13 replays only (all available for sub 53649581); one 4p self-play excluded. Trends are large and
  consistent across 2p and 4p, so directional confidence is high.
- Files: replays `intel/replays/`, episode list `intel/episodes_53649581.csv`, analysis `intel/analyze.py`.
