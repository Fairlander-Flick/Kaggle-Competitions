"""Archetype opponents for a STRONG + DIVERSE gauntlet (anti-overfit).

These reuse Orbiter's correct mechanics (intercept lead, production-aware capture
sizing, path clearance) but with distinct playstyles via extreme PARAMS — so tuning
optimizes against varied strategies instead of overfitting to the weak sniper/starter.
Genuinely-distinct architectures (search bot, defense/turtle family) are added by the
parallel subagent families and frozen into the pool as they are CONFIRMED.
"""

from bots.orbiter import make_agent

ARCHETYPE_PARAMS = {
    # all-in early aggression: no reserve, big enemy denial, many launches, far reach
    "rusher": {
        "reserve_frac": 0.02, "reserve_min": 1.0, "enemy_bonus": 2.4,
        "max_launches": 14, "capture_margin": 0.0, "capture_margin_frac": 0.03,
        "dist_weight": 0.3, "max_eta": 300.0, "min_fleet": 1,
    },
    # turtle: hoard ships, only grab close cheap neutrals, defend hard
    "turtle": {
        "reserve_frac": 0.55, "reserve_min": 8.0, "enemy_bonus": 0.6,
        "max_launches": 3, "max_eta": 45.0, "threat_reserve": 1.5,
        "neutral_bias": 1.4, "prod_weight": 1.2,
    },
    # economic expander: maximise production captured per ship, ignore enemies early
    "expander": {
        "reserve_frac": 0.25, "prod_weight": 2.6, "enemy_bonus": 0.7,
        "neutral_bias": 2.0, "cost_weight": 1.4, "dist_weight": 1.2,
        "max_launches": 8,
    },
    # comet-greedy: chase comets + high production for tempo
    "comet": {
        "comet_penalty": 1.3, "prod_weight": 2.2, "enemy_bonus": 1.0,
        "reserve_frac": 0.15, "max_launches": 8, "max_eta": 220.0,
    },
    # balanced strong default (a second copy of the tuned incumbent style)
    "balanced": {
        "reserve_frac": 0.22, "enemy_bonus": 1.4, "prod_weight": 1.6,
        "max_launches": 7,
    },
}


def get_archetypes():
    return {name: make_agent(p) for name, p in ARCHETYPE_PARAMS.items()}
