"""Crawl agent v5 — BFS-pathfinding survival climber.

Game model (from engine source): the factory is indestructible vs non-factory units
and dies only by scrolling off the south boundary. The maze scrolls north ~276 rows
over 500 steps; a factory climbs at most ~275. So the game reduces to MAXIMIZING
FACTORY SURVIVAL DEPTH. Whoever's factory scrolls off later wins.

Strategy:
  * Maintain a persistent memory of discovered walls (remembered permanently in-game).
  * Each turn, BFS through the remembered maze (unknown = optimistically passable) to
    find the highest-row reachable cell; step the factory one cell along the shortest
    path toward it. This avoids the dead-end trap that idles a naive climber.
  * JUMP (2 cells, ignores walls, same move-cooldown as a walk, 20-turn CD) is used to
    escape when walking cannot increase the factory's row this turn.
  * Never step off the north board edge (row must stay <= northBound).
  * Piggyback economy on FORCED-IDLE turns only (when blocked & jump on cooldown):
    build a scout to reveal the maze ahead so future BFS sees dead-ends early.
"""

from collections import deque

FACTORY, SCOUT, WORKER, MINER = 0, 1, 2, 3
WALL_N, WALL_E, WALL_S, WALL_W = 1, 2, 4, 8
# direction -> (dcol, drow, wallbit)
DIRS = {
    "NORTH": (0, 1, WALL_N),
    "SOUTH": (0, -1, WALL_S),
    "EAST": (1, 0, WALL_E),
    "WEST": (-1, 0, WALL_W),
}

# ---- persistent per-episode memory (module globals survive across turns) ----
_MEM = {}          # (col,row) -> wall bitfield (accumulated, permanent)
_LAST_STEP = -1
_BUILT_SCOUTS = 0
_BUILT_WORKERS = 0


def _reset():
    global _MEM, _BUILT_SCOUTS, _BUILT_WORKERS
    _MEM = {}
    _BUILT_SCOUTS = 0
    _BUILT_WORKERS = 0


def _ingest(obs, width):
    """Merge the visible window walls into permanent memory."""
    walls = obs.walls
    south = obs.southBound
    n = len(walls)
    for idx in range(n):
        v = walls[idx]
        if v == -1:
            continue
        r = south + idx // width
        c = idx % width
        _MEM[(c, r)] = v


def _passable(c, r, direction, width, south, north_cap):
    """Can a unit walk from (c,r) in `direction` given memory? Unknown = optimistic."""
    dc, dr, bit = DIRS[direction]
    nc, nr = c + dc, r + dr
    if nc < 0 or nc >= width:
        return False
    if nr < south or nr > north_cap:
        return False
    w = _MEM.get((c, r))
    if w is not None and (w & bit):
        return False
    return True


def _reach_row(cell, width, south, north_cap):
    """Max row reachable from `cell` using ONLY N/E/W moves (never south).

    Unknown cells are optimistically passable. This is the climb potential of a
    cell: how high the factory can eventually get if it starts here.
    """
    c0, r0 = cell
    if not (0 <= c0 < width) or r0 < south or r0 > north_cap:
        return -1
    seen = {cell}
    q = deque([cell])
    best = r0
    while q:
        c, r = q.popleft()
        if r > best:
            best = r
            if best >= north_cap:
                return best
        for d in ("NORTH", "EAST", "WEST"):
            if _passable(c, r, d, width, south, north_cap):
                dc, dr, _ = DIRS[d]
                nxt = (c + dc, r + dr)
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
    return best


def _best_climb_dir(col, row, width, south, north, horizon):
    """BFS (N/E/W only, never south) to the best reachable cell; return first step.

    Best cell = max row, tie -> fewest moves, tie -> most central. Returns
    (first_dir or None, best_row). None => no upward progress reachable by walking.
    """
    north_cap = min(north, south + horizon)
    start = (col, row)
    came = {start: None}
    dist = {start: 0}
    q = deque([start])
    best = start
    best_key = (row, 0, -abs(col - width / 2.0))   # (row, -dist, -|center|)
    while q:
        c, r = q.popleft()
        k = (r, -dist[(c, r)], -abs(c - width / 2.0))
        if k > best_key:
            best_key = k
            best = (c, r)
        for d in ("NORTH", "EAST", "WEST"):
            if _passable(c, r, d, width, south, north_cap):
                dc, dr, _ = DIRS[d]
                nc, nr = c + dc, r + dr
                if nr > north:
                    continue
                nxt = (nc, nr)
                if nxt not in came:
                    came[nxt] = ((c, r), d)
                    dist[nxt] = dist[(c, r)] + 1
                    q.append(nxt)
    if best == start or best[1] <= row:
        return None, best[1]
    cur = best
    first = None
    while came[cur] is not None:
        prev, d = came[cur]
        first = d
        cur = prev
    return first, best[1]


def _factory_action(uid, d, obs, config, width):
    rt, col, row, en = d[0], d[1], d[2], d[3]
    mcd, jcd = d[5], d[6]
    south, north = obs.southBound, obs.northBound

    can_jump = (mcd == 0 and jcd == 0 and row <= north - 2)
    north_walk = _passable(col, row, "NORTH", width, south, north) and row < north

    # Seed a wall-puncher worker at the very start (big buffer -> cheap), spawning
    # NORTH so it leads the factory and carves a channel. Costs ONE early turn.
    global _BUILT_WORKERS
    if (obs.step <= 1 and _BUILT_WORKERS == 0 and d[7] == 0
            and en >= config.workerCost + 50
            and _passable(col, row, "NORTH", width, south, north)):
        _BUILT_WORKERS += 1
        return "BUILD_WORKER_NORTH"

    if row >= north:                    # already at the top: hold (can't go higher)
        bd = None
    else:
        bd, _ = _best_climb_dir(col, row, width, south, north, horizon=60)

    # Prefer JUMP to bypass a wall-shelf: if we can't simply walk north but the
    # best walking route is lateral (a detour), a ready jump leaps 2 rows past the
    # wall immediately — usually faster than walking around.
    if not north_walk and can_jump:
        return "JUMP_NORTH"

    if bd is not None:
        return bd                       # walk along the shortest climbing route

    # Stuck and jump on cooldown: FREE turn. Build a scout to scout the maze ahead.
    global _BUILT_SCOUTS
    if (jcd > 0 and en >= config.scoutCost + 50 and _BUILT_SCOUTS < 2 and d[7] == 0):
        for udir in ("NORTH", "EAST", "WEST"):
            if _passable(col, row, udir, width, south, north):
                _BUILT_SCOUTS += 1
                return "BUILD_SCOUT_" + udir
    # else sidestep to maybe open a new northward route, or hold
    for udir in ("EAST", "WEST"):
        if _passable(col, row, udir, width, south, north):
            return udir
    return "IDLE"


def _scout_action(col, row, obs, width):
    """Scouts explore north to reveal walls ahead; sidestep when blocked."""
    south, north = obs.southBound, obs.northBound
    if row < north and _passable(col, row, "NORTH", width, south, north):
        return "NORTH"
    # spread out to reveal more
    for d in ("EAST", "WEST"):
        if _passable(col, row, d, width, south, north):
            return d
    if row < north:
        return "NORTH"
    return "IDLE"


def _worker_action(d, obs, config, width):
    """Worker = wall-puncher: climb north, REMOVE the north wall when blocked.

    This carves a straight vertical channel the factory follows -> the factory
    climbs in a straight line instead of detouring around shelves.
    """
    col, row, en = d[1], d[2], d[3]
    south, north = obs.southBound, obs.northBound
    w = _MEM.get((col, row), 0)
    if row >= north:
        return "IDLE"
    if not (w & WALL_N):                       # north open: climb
        return "NORTH"
    # north wall: punch it (if affordable) so the factory can pass
    if en >= config.wallRemoveCost + 1:
        return "REMOVE_NORTH"
    # too poor to punch: sidestep to find an opening / collect a crystal
    for sd in ("EAST", "WEST"):
        if _passable(col, row, sd, width, south, north):
            return sd
    return "IDLE"


def _agent_core(obs, config):
    global _LAST_STEP
    width = config.width
    step = obs.step
    if step == 0 or step < _LAST_STEP:
        _reset()
    _LAST_STEP = step
    _ingest(obs, width)

    actions = {}
    for uid, d in obs.robots.items():
        if d[4] != obs.player:
            continue
        rt = d[0]
        if rt == FACTORY:
            actions[uid] = _factory_action(uid, d, obs, config, width)
        elif rt == WORKER:
            actions[uid] = _worker_action(d, obs, config, width)
        else:
            actions[uid] = _scout_action(d[1], d[2], obs, width)
    return actions


def agent(obs, config):
    """Defensive wrapper: an unhandled exception = instant loss, so on ANY error
    fall back to a safe greedy-north climb that never steps off the north edge."""
    try:
        return _agent_core(obs, config)
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
                if d[0] == 0:  # factory
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
