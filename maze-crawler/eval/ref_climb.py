"""Reference baseline: greedy north-climber, no pathfinding (the 'smart_climb' floor)."""
WALL_N, WALL_E, WALL_W = 1, 2, 8


def agent(obs, config):
    acts = {}
    W = config.width
    north = obs.northBound
    south = obs.southBound
    for uid, d in obs.robots.items():
        rt, col, row, en, owner = d[0], d[1], d[2], d[3], d[4]
        if owner != obs.player:
            continue
        mcd, jcd = d[5], d[6]
        idx = (row - south) * W + col
        w = obs.walls[idx] if 0 <= idx < len(obs.walls) and obs.walls[idx] != -1 else 0
        if rt == 0:
            can_jump = (mcd == 0 and jcd == 0 and row <= north - 2)
            if row < north and not (w & WALL_N):
                acts[uid] = "NORTH"
            elif can_jump:
                acts[uid] = "JUMP_NORTH"
            elif row < north:
                if not (w & WALL_E):
                    acts[uid] = "EAST"
                elif not (w & WALL_W):
                    acts[uid] = "WEST"
                else:
                    acts[uid] = "IDLE"
            else:
                acts[uid] = "IDLE"
        else:
            acts[uid] = "NORTH" if (row < north and not (w & WALL_N)) else "IDLE"
    return acts
