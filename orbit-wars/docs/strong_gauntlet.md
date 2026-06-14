# Strong Gauntlet — transfer-relevant opponents for offline tuning

**Date:** 2026-06-14
**Author:** analysis+codegen subagent
**Goal:** replace the WEAK home gauntlet (sniper/starter + simple `arch:` bots)
with opponents that mimic the STRONG real-ladder playstyles, so offline winrates
predict real-ladder strength.

## Data
- 37 rated replays in `intel/replays2/` (24 freshly pulled from subs 53649581
  v1 + 53666356 Orbiter-MC; 13 carried over). Most are LOSSES vs distinct strong
  opponents — exactly the bots we need to learn from.
- Characterized per-opponent in `intel/analyze2.py` (run it to regenerate the
  table). Authoritative state = player-0 obs (owners/ships absolute).

## Strong playstyles found (clusters)
Metrics: 1stL = first-launch turn; L/t = launches per turn (throughput); avgF =
avg fleet size; reinf% = launches that reinforce own planets; p100 = planets at
turn 100.

| # | Playstyle | Exemplars | Signature |
|---|-----------|-----------|-----------|
| 1 | **SNOWBALL** | Vinit | 1stL~7, L/t 6.2 (3078 launches!), avgF ~145, reinf 64%, cadence ramps 5->194/25t, p100 8 then explodes. Mass + relentless rear->front reallocation; economy crushes late. |
| 2 | **BLITZ** | Daniel Bekker, Tuncay Aydın, sawasawasawa | 1stL 1-2, 12-42 opening launches, early cadence 34-139/25t, avgF 10-29, p100 14-25. Early neutral land-grab + sustained pressure + defense. |
| 3 | **BIGFLEET** | Pranav Unni, Jmkelliher, ryu_to, Arya Arun | avgF 38-57, fewer launches (200-550), reinf 40-70%, big decisive flips, hoards then strikes. Quality over quantity. |
| 4 | **SWARM** | 洛kkkkk, mohamedgamal | avgF 3-11 (median 1!), huge launch count (1500+), near-pure neutral targeting, never idle. Floods board with cheap captures. |
| 5 | **ECONDEF** | Shota Shibata, Valentin Best, Saurabh Kumar234 | balanced, sustained mid/late cadence, defends + reinforces, grinds out economic win. |

The two metrics that separate winners from losers most (confirms prior REPORT.md):
**total launch throughput** and **avg fleet size** — winners never freeze and
send correctly-sized fleets; our bot freezes mid-game on idle 300-400 garrisons.

## Opponents built (`eval/strong_gauntlet.py`)
Each is `bots.orbiter2.make_agent(<tuned params>)`. orbiter2 (not the simpler
orbiter) is the base because it ALREADY has the two traits every strong opponent
shows and base Orbiter lacks: (a) never freezes — deploys surplus from every
planet every turn, (b) threat-based DEFENSE so it isn't a glass cannon. Correct
mechanics (intercept lead, production-aware capture sizing, swept-collision path
clearance) are inherited. We push PARAMS to each cluster centroid; forward_push
reinforcement is enabled for the high-reinforce styles (snowball/bigfleet/econdef).

- `sg:snowball` — huge throughput, big fleets (min_fleet 4, margins high), far
  reach, forward reinforcement.
- `sg:blitz` — launch turn 1, low reserve, enemy-denial bonus, short reach, high
  launch cap, sustained.
- `sg:bigfleet` — few large fleets (min_fleet 10, big margins), consolidates rear
  -> front, strong defensive reserve.
- `sg:swarm` — min_fleet 1, neutral_bias 2.2, zero capture margin, max launches.
- `sg:econdef` — balanced, high threat_cover defense, forward reinforcement,
  moderate launch cap.

## League integration
Registered in `eval/league.py` `resolve()` under prefix `sg:<name>` (mirrors
`arch:`). Usage:

    python eval/league.py --a file:bots/orbiter_mc.py --b sg:snowball --games 30 --procs 4

## Validation — champion orbiter_mc winrate vs each strong opponent
(2p, 30 games, procs 4; `python eval/validate_strong.py 30 4`)

<!-- RESULTS -->

## Recommendation
Add the `sg:*` opponents to the CMA-ES tuner opponent set
(`eval/cmaes_tune.py` OPP_2P / OPP_4P) in place of (or alongside) the weak
`arch:*` bots, so tuning optimizes against transfer-relevant strength.
