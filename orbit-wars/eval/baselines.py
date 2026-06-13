"""Baseline opponents for the Orbit Wars league.

  random  : engine's random_agent (sends half-garrison in random directions)
  starter : engine's starter_agent (nearest STATIC planet, half garrison)
  sniper  : the kit's main.py "nearest planet sniper" (garrison+1 at current pos)

These define the fixed opponent pool the measurement contract scores against.
"""

import math
from kaggle_environments.envs.orbit_wars.orbit_wars import (
    Planet, random_agent, starter_agent, CENTER,
)


def sniper_agent(obs, config=None):
    moves = []
    player = obs.get("player", 0) if isinstance(obs, dict) else obs.player
    raw = obs.get("planets", []) if isinstance(obs, dict) else obs.planets
    planets = [Planet(*p) for p in raw]
    mine = [p for p in planets if p.owner == player]
    targets = [p for p in planets if p.owner != player]
    if not targets:
        return moves
    for m in mine:
        nearest = min(targets, key=lambda t: math.hypot(m.x - t.x, m.y - t.y))
        need = nearest.ships + 1
        if m.ships >= need:
            angle = math.atan2(nearest.y - m.y, nearest.x - m.x)
            moves.append([m.id, angle, need])
    return moves


def idle_agent(obs, config=None):
    return []


POOL = {
    "random": random_agent,
    "starter": starter_agent,
    "sniper": sniper_agent,
    "idle": idle_agent,
}
