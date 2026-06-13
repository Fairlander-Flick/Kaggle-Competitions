"""Crawl agent v6 — channel-rush survival climber.

KEY INSIGHT: north/south walls are NEVER fixed (only E/W perimeter + central axis
are). So a WORKER can REMOVE_NORTH every wall in its column and carve a perfectly
straight vertical channel north forever. The factory climbs straight up that channel
at the max walk rate (0.5/turn) without ever detouring or idling in a dead-end, and
JUMPs to bypass any not-yet-punched wall. The factory TRANSFERS energy north to keep
the worker funded for punching (each REMOVE costs 100). The game reduces to factory
survival depth; this maximizes it.
"""
from collections import deque

FACTORY, SCOUT, WORKER, MINER = 0, 1, 2, 3
WALL_N, WALL_E, WALL_S, WALL_W = 1, 2, 4, 8
DIRS = {"NORTH": (0, 1, WALL_N), "SOUTH": (0, -1, WALL_S),
        "EAST": (1, 0, WALL_E), "WEST": (-1, 0, WALL_W)}

_MEM = {}
_LAST_STEP = -1


def _reset():
    global _MEM
    _MEM = {}


def _ingest(obs, width):
    walls = obs.walls
    south = obs.southBound
    for idx, v in enumerate(walls):
        if v == -1:
            continue
        _MEM[(idx % width, south + idx // width)] = v


def _wall(c, r):
    return _MEM.get((c, r), 0)


def _passable(c, r, direction, width, south, north):
    dc, dr, bit = DIRS[direction]
    nc, nr = c + dc, r + dr
    if nc < 0 or nc >= width or nr < south or nr > north:
        return False
    w = _MEM.get((c, r))
    if w is not None and (w & bit):
        return False
    return True


def _occupied_by_friend(robots, player, c, r, exclude):
    for uid, d in robots.items():
        if uid != exclude and d[4] == player and d[1] == c and d[2] == r:
            return True
    return False


def _factory_action(uid, d, obs, config, width, my_workers):
    col, row, en = d[1], d[2], d[3]
    mcd, jcd, bcd = d[5], d[6], d[7]
    south, north = obs.southBound, obs.northBound
    robots = obs.robots
    player = obs.player

    # worker directly north (our channel puncher)
    lead = None
    for w in my_workers:
        if w[1] == col and w[2] == row + 1:
            lead = w
            break

    north_open = _passable(col, row, "NORTH", width, south, north) and row < north
    worker_north = _occupied_by_friend(robots, player, col, row + 1, uid)
    worker_n2 = _occupied_by_friend(robots, player, col, row + 2, uid)
    # NOTE: engine ticks cooldowns DOWN at the start of the turn BEFORE executing,
    # so observed cd<=1 means "ready to act this turn" (off-by-one — critical).
    can_jump = (mcd <= 1 and jcd <= 1 and row <= north - 2)

    passage_open = _passable(col, row, "NORTH", width, south, north)
    n_workers = len(my_workers)

    # 1) keep a puncher alive: build one north only when we have NO worker at all.
    if (n_workers == 0 and bcd == 0 and en >= config.workerCost + 100
            and passage_open and not worker_north):
        return "BUILD_WORKER_NORTH"

    # 2) PROACTIVELY refuel the lead puncher (a funded worker clears many walls;
    #    worth the climb-turn). Only when adjacent north & passage open.
    if lead is not None and lead[3] < 150 and en >= 250 and passage_open and worker_north:
        return "TRANSFER_NORTH"

    # 3) climb: walk north behind the puncher when the channel is open.
    if north_open and not worker_north:
        return "NORTH"
    # 4) north blocked (unpunched wall / worker ahead): JUMP to bypass.
    if can_jump and not worker_n2:
        return "JUMP_NORTH"
    # 5) stuck: relay-build a puncher to a side, else sidestep, else hold.
    if lead is None and bcd == 0 and en >= config.workerCost + 100:
        for sd in ("EAST", "WEST"):
            if _passable(col, row, sd, width, south, north):
                return "BUILD_WORKER_" + sd
    for sd in ("EAST", "WEST"):
        if _passable(col, row, sd, width, south, north):
            return sd
    return "IDLE"


def _worker_action(d, obs, config, width):
    col, row, en = d[1], d[2], d[3]
    south, north = obs.southBound, obs.northBound
    if row >= north:
        return "IDLE"
    if _passable(col, row, "NORTH", width, south, north):
        return "NORTH"                          # channel open: climb
    # north walled: punch it (always allowed — N/S walls never fixed)
    if en >= config.wallRemoveCost + 1:
        return "REMOVE_NORTH"
    # too poor to punch: try to grab a nearby crystal / sidestep, else wait for refuel
    for sd in ("EAST", "WEST"):
        if _passable(col, row, sd, width, south, north):
            return sd
    return "IDLE"


def _scout_action(d, obs, width):
    col, row = d[1], d[2]
    south, north = obs.southBound, obs.northBound
    if row < north and _passable(col, row, "NORTH", width, south, north):
        return "NORTH"
    for sd in ("EAST", "WEST"):
        if _passable(col, row, sd, width, south, north):
            return sd
    return "IDLE"


def _core(obs, config):
    global _LAST_STEP
    width = config.width
    step = obs.step
    if step == 0 or step < _LAST_STEP:
        _reset()
    _LAST_STEP = step
    _ingest(obs, width)

    player = obs.player
    my_workers = [d for d in obs.robots.values() if d[4] == player and d[0] == WORKER]
    actions = {}
    for uid, d in obs.robots.items():
        if d[4] != player:
            continue
        rt = d[0]
        if rt == FACTORY:
            actions[uid] = _factory_action(uid, d, obs, config, width, my_workers)
        elif rt == WORKER:
            actions[uid] = _worker_action(d, obs, config, width)
        else:
            actions[uid] = _scout_action(d, obs, width)
    return actions


def agent(obs, config):
    try:
        return _core(obs, config)
    except Exception:
        acts = {}
        try:
            W = config.width; north = obs.northBound; south = obs.southBound
            for uid, d in obs.robots.items():
                if d[4] != obs.player:
                    continue
                col, row = d[1], d[2]
                idx = (row - south) * W + col
                w = obs.walls[idx] if 0 <= idx < len(obs.walls) and obs.walls[idx] != -1 else 0
                if d[0] == 0:
                    if row < north and not (w & 1):
                        acts[uid] = "NORTH"
                    elif d[5] == 0 and d[6] == 0 and row <= north - 2:
                        acts[uid] = "JUMP_NORTH"
                    else:
                        acts[uid] = "IDLE"
                else:
                    acts[uid] = "NORTH" if (row < north and not (w & 1)) else "IDLE"
        except Exception:
            pass
        return acts
