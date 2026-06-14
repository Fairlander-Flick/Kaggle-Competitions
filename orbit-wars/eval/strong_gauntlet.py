"""STRONG, transfer-relevant opponent gauntlet for Orbit Wars offline tuning.

Motivation
----------
Our home gauntlet (sniper / starter / simple archetypes) is WEAK, so offline
winrates don't predict real-ladder strength (top ladder ~1700, us ~600). This
module builds opponents that MIMIC the strong playstyles observed in our rated
replays (intel/replays2/, characterized by intel/analyze2.py).

Replay-derived strong playstyles (per-opponent profiles; see intel/STRONG_GAUNTLET.md)
--------------------------------------------------------------------------------
  1. SNOWBALL  (Vinit): first launch ~turn 7, then HUGE sustained throughput
     (3078 launches/game, cadence ramps 5 -> ~194/25-turns), avg fleet ~145,
     reinforce-heavy (~64%). Masses production into giant consolidated strike
     fleets while continuously pushing rear -> front. Economy crushes late.
  2. BLITZ     (Daniel Bekker / Tuncay / sawasawasawa): first launch turn 1-2,
     heavy opening neutral land-grab (12-42 opening launches), high early
     cadence (34-139 by window 2), moderate fleets (10-29), 23-25 planets by
     turn 100. Aggressive expander that keeps pressure on AND defends.
  3. BIGFLEET  (Pranav Unni / Jmkelliher / ryu_to / Arya Arun): very large avg
     fleets (38-57), moderate launch count, high reinforce%, hoards then sends
     decisive over-sized fleets that reliably flip. Quality over quantity.
  4. SWARM     (洛kkkkk / mohamedgamal): tiny fleets (avg 3-11, median 1),
     enormous launch count, near-pure neutral targeting, never idle. Floods the
     board with cheap captures and constant micro-reallocation.
  5. ECONDEF   (Shota Shibata / Valentin Best / Saurabh): balanced economic
     expander that sustains mid/late cadence AND defends/reinforces hard.

Implementation
--------------
These are LOCAL test opponents (NOT submissions) so local imports are fine.

They are built on ``bots.orbiter2`` (NOT the simpler bots.orbiter): orbiter2 is
the high-throughput rewrite that already has the two properties EVERY strong
opponent in the replays shows and that the base Orbiter lacks --
  (a) it never freezes: it deploys surplus from every planet every turn instead
      of capping launches and hoarding idle garrisons, and
  (b) it has threat-based DEFENSE (reserve >= incoming threat) so it isn't a
      glass cannon.
orbiter2 also keeps the correct mechanics (deterministic intercept lead,
production-aware capture sizing at arrival, continuous swept-collision path
clearance). We just push its PARAMS to the extreme of each replay cluster, and
enable its built-in forward-push reinforcement for the styles whose replay
reinforce-fraction is high (snowball/bigfleet/econdef).

Public API:  get_strong_pool() -> {name: agent_callable}
Names:       snowball, blitz, bigfleet, swarm, econdef
"""

from bots.orbiter2 import make_agent


# Per-playstyle PARAMS (overrides on bots.orbiter2.PARAMS). Tuned to the cluster
# centroids observed in the replays. orbiter2 keeps strong defense via
# threat_cover/home_reserve, so these stay robust (not glass cannons).
STRONG_PARAMS = {
    # 1. SNOWBALL: huge throughput, big fleets, far reach, forward reinforcement.
    #    Big capture margins so the masses land as decisive flips; reinforce rear
    #    -> frontier so production never sits idle (Vinit's ~64% reinforce).
    "snowball": {
        "home_reserve": 3.0, "threat_cover": 1.25,
        "prod_weight": 2.2, "neutral_bias": 1.7, "enemy_bonus": 1.2,
        "cost_weight": 0.7, "dist_weight": 0.6, "max_eta": 280.0,
        "max_launches": 40, "capture_margin": 2.0, "capture_margin_frac": 0.10,
        "min_fleet": 4, "forward_push": 1.0, "min_leftover": 8.0,
    },
    # 2. BLITZ: launch turn 1, grab neutrals fast, deny enemy, sustain pressure.
    #    Low reserve but defense still covers real threats; short reach early.
    "blitz": {
        "home_reserve": 2.0, "threat_cover": 1.2,
        "prod_weight": 1.5, "neutral_bias": 1.5, "enemy_bonus": 1.7,
        "cost_weight": 0.7, "dist_weight": 0.5, "max_eta": 230.0,
        "max_launches": 40, "capture_margin": 1.0, "capture_margin_frac": 0.05,
        "min_fleet": 2, "forward_push": 0.0,
    },
    # 3. BIGFLEET: fewer, larger, decisive fleets; reliable flips; consolidate
    #    rear ships forward first. Strong defensive reserve (it can afford to).
    "bigfleet": {
        "home_reserve": 5.0, "threat_cover": 1.4,
        "prod_weight": 1.8, "neutral_bias": 1.3, "enemy_bonus": 1.4,
        "cost_weight": 0.5, "dist_weight": 0.7, "max_eta": 240.0,
        "max_launches": 6, "capture_margin": 4.0, "capture_margin_frac": 0.16,
        "min_fleet": 10, "forward_push": 1.0, "min_leftover": 14.0,
    },
    # 4. SWARM: flood with cheap captures; tiny fleets, enormous count, pure
    #    neutral focus. No reinforcement (it never has a rear hoard).
    "swarm": {
        "home_reserve": 1.0, "threat_cover": 1.15,
        "prod_weight": 2.0, "neutral_bias": 2.2, "enemy_bonus": 0.9,
        "cost_weight": 1.2, "dist_weight": 0.8, "max_eta": 220.0,
        "max_launches": 40, "capture_margin": 0.0, "capture_margin_frac": 0.02,
        "min_fleet": 1, "forward_push": 0.0,
    },
    # 5. ECONDEF: balanced economic expander; sustained cadence + hard defense
    #    and forward reinforcement. The "grind you out economically" bot.
    "econdef": {
        "home_reserve": 4.0, "threat_cover": 1.5,
        "prod_weight": 2.0, "neutral_bias": 1.6, "enemy_bonus": 1.1,
        "cost_weight": 1.0, "dist_weight": 0.8, "max_eta": 220.0,
        "max_launches": 14, "capture_margin": 2.0, "capture_margin_frac": 0.08,
        "min_fleet": 3, "forward_push": 1.0, "min_leftover": 6.0,
    },
}

STRONG_NAMES = list(STRONG_PARAMS.keys())


def get_strong(name):
    """Build a single strong-gauntlet opponent by name (used by league resolve)."""
    if name not in STRONG_PARAMS:
        raise ValueError(f"unknown strong-gauntlet opponent: {name}")
    return make_agent(STRONG_PARAMS[name])


def get_strong_pool():
    """name -> agent callable, for all strong-gauntlet opponents."""
    return {name: get_strong(name) for name in STRONG_NAMES}
