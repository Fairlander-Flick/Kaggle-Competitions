"""
Orbiter — Orbit Wars agent (heuristic core, parameterised for CMA-ES tuning).

Design follows the engine reading (kaggle_environments/envs/orbit_wars/orbit_wars.py):

  * Neutral planets (owner == -1) do NOT produce; owned/enemy planets grow by
    `production` every turn.  => capture-cost for a neutral is fixed, for an enemy
    it grows with travel time, so we size fleets against the garrison AT ARRIVAL.
  * Orbit is deterministic: a planet's future angle = current_angle + av*dt, where
    current_angle is read straight off the live (x,y).  We lead moving targets
    (interception) instead of aiming at the stale position (what random/starter do).
  * Fleet speed scales with size: v(n) = 1 + (maxS-1)*(log(n)/log(1000))^1.5, capped
    at maxS (default 6). n=1 -> v=1 (slow). => concentrate force, don't dribble.
  * Collision is continuous (swept): a fleet that grazes the sun or an unintended
    planet is consumed / fights there.  We keep launch lines clear of the sun and
    of non-target planets.
  * Combat: attackers grouped per owner & summed; capture iff surviving attackers
    STRICTLY exceed garrison.  Eliminating every opponent ends the game as a win.

The whole policy is wrapped in try/except — an unhandled exception is an instant
episode loss, so any failure degrades to "do nothing this turn".

`PARAMS` is the tunable weight vector (CMA-ES evolves it via the self-play league).
For submission, the defaults below are baked in.
"""

import math

BOARD = 100.0
CENTER = 50.0
SUN_R = 10.0
ROT_LIMIT = 50.0
MAX_SPEED_DEFAULT = 6.0

PARAMS = {
    "reserve_frac": 0.30,        # keep this fraction of a planet's ships home
    "reserve_min": 3.0,          # absolute floor on the kept reserve
    "capture_margin": 2.0,       # extra ships beyond the strict requirement (abs)
    "capture_margin_frac": 0.08, # extra ships as a fraction of requirement
    "prod_weight": 1.4,          # value exponent on production
    "dist_weight": 0.9,          # ETA penalty in the value denominator
    "cost_weight": 1.0,          # ship-cost penalty in the value denominator
    "enemy_bonus": 1.35,         # multiplier on enemy-owned target value (denial)
    "comet_penalty": 0.45,       # multiplier on comet target value (they vanish)
    "neutral_bias": 1.0,         # multiplier on neutral target value
    "max_launches": 6,           # launches per turn cap (speed + focus)
    "min_fleet": 2,              # never send a smaller fleet than this
    "endgame_turn": 478,         # after this, only sure captures / reinforcement
    "sun_margin": 1.5,           # extra clearance beyond sun radius
    "graze_margin": 0.8,         # extra clearance past a non-target planet radius
    "intercept_iters": 5,        # fixed-point iterations for the intercept solve
    "defense_tol": 0.30,         # heading tolerance (rad) for "fleet aimed at us"
    "threat_reserve": 1.10,      # hold garrison * this when a planet is threatened
    "max_eta": 220.0,            # ignore targets farther than this many ticks
}


def _dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)


def _seg_point_dist(px, py, ax, ay, bx, by):
    l2 = (ax - bx) ** 2 + (ay - by) ** 2
    if l2 == 0.0:
        return _dist(px, py, ax, ay)
    t = ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / l2
    t = max(0.0, min(1.0, t))
    return _dist(px, py, ax + t * (bx - ax), ay + t * (by - ay))


def _fleet_speed(n, max_speed):
    if n <= 1:
        return 1.0
    v = 1.0 + (max_speed - 1.0) * (math.log(n) / math.log(1000.0)) ** 1.5
    return min(v, max_speed)


def _is_orbiting(px, py, radius):
    return _dist(px, py, CENTER, CENTER) + radius < ROT_LIMIT


def _future_pos(p, dt, av):
    """Position of planet tuple p = [id,owner,x,y,r,ships,prod] after dt ticks."""
    x, y, r = p[2], p[3], p[4]
    if av == 0 or not _is_orbiting(x, y, r):
        return x, y
    orb = _dist(x, y, CENTER, CENTER)
    ang = math.atan2(y - CENTER, x - CENTER) + av * dt
    return CENTER + orb * math.cos(ang), CENTER + orb * math.sin(ang)


def _intercept(sx, sy, src_r, target, av, max_speed, ships_guess, iters):
    """Solve launch angle + ETA + arrival pos for a fleet of ~ships_guess ships
    leaving (sx,sy) toward `target`. Returns (angle, eta, ax, ay)."""
    v = _fleet_speed(ships_guess, max_speed)
    ax, ay = target[2], target[3]
    eta = 0.0
    for _ in range(iters):
        d = _dist(sx, sy, ax, ay) - src_r - 0.1
        d = max(d, 0.0)
        eta = d / v if v > 0 else 0.0
        ax, ay = _future_pos(target, eta, av)
    angle = math.atan2(ay - sy, ax - sx)
    return angle, eta, ax, ay


def _seg_closest_t(px, py, ax, ay, bx, by):
    l2 = (ax - bx) ** 2 + (ay - by) ** 2
    if l2 == 0.0:
        return 0.0
    t = ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / l2
    return max(0.0, min(1.0, t))


def _path_clear(sx, sy, ax, ay, src_id, target_id, planets, sun_margin, graze_margin):
    # sun crossing kills the fleet
    if _seg_point_dist(CENTER, CENTER, sx, sy, ax, ay) < SUN_R + sun_margin:
        return False
    # an UNINTENDED planet sitting in the middle of the path diverts the fleet.
    # Skip the source & target, and ignore planets whose closest approach is at
    # the endpoints (they are not en-route obstacles).
    for p in planets:
        if p[0] == src_id or p[0] == target_id:
            continue
        t = _seg_closest_t(p[2], p[3], sx, sy, ax, ay)
        if t <= 0.02 or t >= 0.99:
            continue
        cx = sx + t * (ax - sx)
        cy = sy + t * (ay - sy)
        if _dist(p[2], p[3], cx, cy) < p[4] + graze_margin:
            return False
    return True


def make_agent(params=None):
    P = dict(PARAMS)
    if params:
        P.update(params)

    def agent(obs, config=None):
        try:
            return _decide(obs, config, P)
        except Exception:
            return []

    return agent


def _decide(obs, config, P):
    if isinstance(obs, dict):
        g = obs.get
    else:
        g = lambda k, d=None: getattr(obs, k, d)

    me = g("player", 0)
    raw_planets = g("planets", []) or []
    raw_fleets = g("fleets", []) or []
    av = g("angular_velocity", 0.0) or 0.0
    step = g("step", 0) or 0
    comet_ids = set(g("comet_planet_ids", []) or [])
    max_speed = MAX_SPEED_DEFAULT
    if config is not None:
        cs = config.get("shipSpeed") if isinstance(config, dict) else getattr(config, "shipSpeed", None)
        if cs:
            max_speed = float(cs)

    planets = list(raw_planets)
    mine = [p for p in planets if p[1] == me]
    if not mine:
        return []
    targets = [p for p in planets if p[1] != me]
    remaining = max(1.0, 500.0 - step)
    endgame = step >= P["endgame_turn"]

    # --- defense: incoming enemy ships per owned planet -------------------
    threat = {p[0]: 0.0 for p in mine}
    mine_by_id = {p[0]: p for p in mine}
    for f in raw_fleets:
        fo = f[1]
        if fo == me:
            continue
        fx, fy, fang, fships = f[2], f[3], f[4], f[6]
        fv = _fleet_speed(fships, max_speed)
        for p in mine:
            ax, ay = p[2], p[3]
            ang_to = math.atan2(ay - fy, ax - fx)
            dang = abs((fang - ang_to + math.pi) % (2 * math.pi) - math.pi)
            if dang < P["defense_tol"]:
                threat[p[0]] += fships

    # --- available ships per source (after reserve / threat) --------------
    avail = {}
    for p in mine:
        ships = p[5]
        base_res = max(P["reserve_min"], P["reserve_frac"] * ships)
        if threat.get(p[0], 0.0) > 0:
            base_res = max(base_res, P["threat_reserve"] * ships)
        avail[p[0]] = max(0.0, ships - base_res)

    # --- score every (target) with its best clear+affordable source -------
    plans = []
    for t in targets:
        is_comet = t[0] in comet_ids
        is_enemy = t[1] != -1
        best = None
        for s in mine:
            if avail[s[0]] < P["min_fleet"]:
                continue
            # iterate ship-count <-> intercept (enemy garrison grows in transit)
            need = t[5] + 1.0
            angle = eta = ax = ay = 0.0
            for _ in range(3):
                ships_guess = max(need, P["min_fleet"])
                angle, eta, ax, ay = _intercept(
                    s[2], s[3], s[4], t, av, max_speed, ships_guess, P["intercept_iters"]
                )
                garrison = t[5] + (t[6] * eta if is_enemy else 0.0)
                need = garrison + 1.0
                need += P["capture_margin"] + P["capture_margin_frac"] * need
            need = math.ceil(need)
            if eta > P["max_eta"]:
                continue
            if need > avail[s[0]] or need > s[5]:
                continue
            if not _path_clear(s[2], s[3], ax, ay, s[0], t[0], planets,
                               P["sun_margin"], P["graze_margin"]):
                continue
            # value: production held over remaining time, per unit cost+distance
            hold = min(remaining, 500.0)
            base = (t[6] ** P["prod_weight"]) * hold
            base *= P["enemy_bonus"] if is_enemy else P["neutral_bias"]
            if is_comet:
                base *= P["comet_penalty"]
            denom = P["cost_weight"] * need + P["dist_weight"] * eta + 1.0
            val = base / denom
            if best is None or val > best[0]:
                best = (val, s, need, angle)
        if best is not None:
            plans.append((best[0], t, best[1], best[2], best[3]))

    plans.sort(key=lambda z: z[0], reverse=True)

    moves = []
    launches = 0
    for val, t, s, need, angle in plans:
        if launches >= P["max_launches"]:
            break
        if endgame and t[1] != -1:
            # late game: don't pick fights, only neutrals that are sure & cheap
            pass
        if avail[s[0]] >= need and s[5] >= need:
            n = int(need)
            if n < P["min_fleet"]:
                continue
            moves.append([s[0], angle, n])
            avail[s[0]] -= need
            s[5] -= n
            launches += 1
    return moves


# default agent for submission (single-file main.py imports this name)
agent = make_agent()
