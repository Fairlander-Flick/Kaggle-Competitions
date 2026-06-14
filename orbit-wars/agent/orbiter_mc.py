"""
Orbiter-MC — forward-model SEARCH agent for Orbit Wars.

Strategy (per turn, inside the ~1s budget):
  1. Build candidate full-turn action lists. Sources:
       - the greedy Orbiter reference action (imported from bots.orbiter),
       - perturbations of Orbiter via param overrides (more/less reserve,
         more/fewer launches, enemy-denial vs neutral-expand, all-in, far reach),
       - do-nothing (accumulate).
  2. Evaluate each candidate by a SHORT forward simulation: apply the candidate
     this turn, then roll H turns forward where BOTH players follow the greedy
     Orbiter reference policy.  The forward model mirrors the engine EXACTLY:
        launch -> production(owned only) -> fleet move w/ continuous swept
        collision (planet first via swept_pair_hit, then OOB, then sun via
        point_to_segment_distance) -> planet rotation -> combat (sum per owner,
        top vs 2nd, survivor vs garrison, capture iff survivor STRICTLY > garr).
  3. Score the resulting state with an economic eval (my ships+production+pos
     minus opponents').
  4. Play the best candidate.

Everything is wrapped in try/except returning [] on any error (an unhandled
exception is an instant episode loss).

PARAMS is the tunable vector (rollout horizon, candidate count, eval weights,
time budget) so CMA-ES can tune it later against the self-play league.
"""

import math
import time

# Engine helpers for collision fidelity (exact match to interpreter geometry).
from kaggle_environments.envs.orbit_wars.orbit_wars import (
    point_to_segment_distance,
    swept_pair_hit,
)
from bots.orbiter import make_agent as _orbiter_make_agent

BOARD = 100.0
CENTER = 50.0
SUN_R = 10.0
ROT_LIMIT = 50.0
MAX_SPEED_DEFAULT = 6.0
LN1000 = math.log(1000.0)

PARAMS = {
    # --- search budget ---
    "horizon": 14,            # rollout depth (turns) per candidate
    "time_budget": 0.72,      # seconds/turn soft cap (lowered for ladder timeout safety)
    "overage_budget": 0.86,   # allowed when remainingOverageTime is plentiful
    "overage_plenty": 20.0,   # >this many sec of overage -> use overage_budget
    "max_candidates": 9,      # hard cap on candidates considered (== #moods+idle)
    # --- economic eval weights ---
    "prod_weight": 5.0,       # value of one unit of (owned) production
    "pos_weight": 0.04,       # small positional term (proximity-to-center bonus)
    "fleet_weight": 1.0,      # value of a ship currently in flight (== on planet)
    "win_bonus": 4000.0,      # bonus if all opponents eliminated in rollout
    "loss_penalty": 4000.0,   # penalty if we are eliminated in rollout
    # --- candidate generation ---
    "n_perturb": 0,           # (reserved) extra random perturbations; 0 = use presets
}

# Param overrides defining the candidate Orbiter "moods". Each yields one
# candidate action this turn.  Kept compact so we stay within the time budget.
_CANDIDATE_MOODS = [
    {},  # the tuned incumbent itself
    {"reserve_frac": 0.10, "reserve_min": 1.0, "max_launches": 10},   # aggressive
    {"reserve_frac": 0.02, "reserve_min": 1.0, "max_launches": 14,
     "enemy_bonus": 2.2, "capture_margin": 0.0, "min_fleet": 1},      # all-in rush
    {"reserve_frac": 0.50, "reserve_min": 8.0, "max_launches": 3,
     "threat_reserve": 1.5},                                          # turtle
    {"prod_weight": 2.6, "neutral_bias": 2.0, "enemy_bonus": 0.7,
     "max_launches": 8},                                              # expander
    {"enemy_bonus": 2.4, "max_launches": 12, "dist_weight": 0.3,
     "capture_margin": 1.0},                                          # denial
    {"reserve_frac": 0.35, "max_launches": 5, "capture_margin": 3.0,
     "capture_margin_frac": 0.12},                                    # safe/solid
    {"max_eta": 60.0, "neutral_bias": 1.6, "max_launches": 6},        # local expand
]


def _obs_get(obs):
    if isinstance(obs, dict):
        return obs.get
    return lambda k, d=None: getattr(obs, k, d)


def _fleet_speed(n, max_speed):
    if n <= 1:
        return 1.0
    v = 1.0 + (max_speed - 1.0) * (math.log(n) / LN1000) ** 1.5
    return min(v, max_speed)


# ----------------------------------------------------------------------------
# Compact forward model
# ----------------------------------------------------------------------------
# State is a plain dict of mutable lists matching the engine's layout so we can
# call the greedy reference policy on a synthesized obs each rollout step.
#   planets[i] = [id, owner, x, y, radius, ships, production]
#   fleets[i]  = [id, owner, x, y, angle, from_planet_id, ships]
# We track absolute `step` (planet rotation uses initial_angle + av*step) and an
# `initial` map id -> (init_angle, orbital_r, radius, is_orbiting) for rotation.
# Comets are intentionally ignored in the rollout (hidden schedule; they are
# economic noise) — this keeps the model deterministic & fast.

def _build_initial(planets):
    """Precompute rotation data per planet id from current positions.

    The engine rotates planets from their *initial_planets* angle using the
    absolute step.  We don't have initial_planets reliably aligned to our
    rollout, so we re-derive each planet's orbit from its current (x,y) and
    advance it relative to the rollout start (dt), which is mathematically
    identical: angle(step0+dt) = angle(step0) + av*dt.
    """
    info = {}
    for p in planets:
        dx = p[2] - CENTER
        dy = p[3] - CENTER
        orb_r = math.hypot(dx, dy)
        is_orb = (orb_r + p[4]) < ROT_LIMIT
        info[p[0]] = (math.atan2(dy, dx), orb_r, p[4], is_orb)
    return info


def _planet_pos_at(info_entry, dt, av):
    init_ang, orb_r, radius, is_orb = info_entry
    if not is_orb or av == 0.0:
        return None  # static -> caller keeps current pos
    ang = init_ang + av * dt
    return (CENTER + orb_r * math.cos(ang), CENTER + orb_r * math.sin(ang))


def _make_obs(planets, fleets, player, av, step):
    return {
        "player": player,
        "planets": [list(p) for p in planets],
        "fleets": [list(f) for f in fleets],
        "angular_velocity": av,
        "step": step,
        "comets": [],
        "comet_planet_ids": [],
        "initial_planets": [list(p) for p in planets],
        "next_fleet_id": 0,
    }


def _apply_launch(planets, fleets, next_fid, action, player):
    """Engine step: fleet launch.  Mutates planets/fleets; returns next_fid."""
    if not action or not isinstance(action, (list, tuple)):
        return next_fid
    pmap = {p[0]: p for p in planets}
    for move in action:
        if len(move) != 3:
            continue
        from_id, angle, ships = move[0], move[1], int(move[2])
        fp = pmap.get(from_id)
        if fp is not None and fp[1] == player and fp[5] >= ships and ships > 0:
            fp[5] -= ships
            sx = fp[2] + math.cos(angle) * (fp[4] + 0.1)
            sy = fp[3] + math.sin(angle) * (fp[4] + 0.1)
            fleets.append([next_fid, player, sx, sy, angle, from_id, ships])
            next_fid += 1
    return next_fid


def _step_forward(planets, fleets, next_fid, actions, info, av, dt_next, max_speed):
    """Advance the rollout one engine tick.

    `actions` is a list (per player) of action lists for THIS tick.
    `dt_next` is the rotation offset (relative to rollout start) that planets
    will occupy AFTER this tick's movement — matches engine using post-increment
    step for rotation.  Returns next_fid.
    """
    # 0. Launch (all players, in seat order)
    for player, act in enumerate(actions):
        next_fid = _apply_launch(planets, fleets, next_fid, act, player)

    # 1. Production (owned planets only)
    for p in planets:
        if p[1] != -1:
            p[5] += p[6]

    # 2. Planet end-of-tick positions (for swept collision + final placement)
    planet_paths = {}
    for p in planets:
        old_pos = (p[2], p[3])
        new_pos = _planet_pos_at(info[p[0]], dt_next, av)
        if new_pos is None:
            new_pos = old_pos
        planet_paths[p[0]] = (old_pos, new_pos)

    # 3. Fleet movement w/ continuous swept collision (planet -> OOB -> sun)
    combat = {p[0]: [] for p in planets}
    survivors = []
    for f in fleets:
        angle = f[4]
        ships = f[6]
        speed = _fleet_speed(ships, max_speed)
        old_pos = (f[2], f[3])
        nx = f[2] + math.cos(angle) * speed
        ny = f[3] + math.sin(angle) * speed
        new_pos = (nx, ny)
        f[2], f[3] = nx, ny

        hit = False
        # Broad-phase: a hit requires the planet's (old) center to be within
        # roughly (speed + radius + slack) of the fleet's old position. Skip the
        # exact swept test for clearly-distant planets. Cheap squared-dist gate.
        # reach = fleet travel + max planet travel (av*orb_r <= 0.05*50=2.5) + slack
        reach = speed + 3.0
        for p in planets:
            p_old, p_new = planet_paths[p[0]]
            ddx = p_old[0] - old_pos[0]
            ddy = p_old[1] - old_pos[1]
            rr = reach + p[4]
            if ddx * ddx + ddy * ddy > rr * rr:
                continue
            if swept_pair_hit(old_pos, new_pos, p_old, p_new, p[4]):
                combat[p[0]].append(f)
                hit = True
                break
        if hit:
            continue
        if not (0 <= nx <= BOARD and 0 <= ny <= BOARD):
            continue
        if point_to_segment_distance((CENTER, CENTER), old_pos, new_pos) < SUN_R:
            continue
        survivors.append(f)

    # 4. Apply planet movement
    for p in planets:
        p[2], p[3] = planet_paths[p[0]][1]

    fleets[:] = survivors

    # 5. Combat resolution
    pmap = {p[0]: p for p in planets}
    for pid, plist in combat.items():
        if not plist:
            continue
        planet = pmap.get(pid)
        if planet is None:
            continue
        ps = {}
        for f in plist:
            ps[f[1]] = ps.get(f[1], 0) + f[6]
        if not ps:
            continue
        sorted_p = sorted(ps.items(), key=lambda kv: kv[1], reverse=True)
        top_owner, top_ships = sorted_p[0]
        if len(sorted_p) > 1:
            second = sorted_p[1][1]
            surv = top_ships - second
            if top_ships == second:
                surv = 0
            surv_owner = top_owner if surv > 0 else -1
        else:
            surv_owner = top_owner
            surv = top_ships
        if surv > 0:
            if planet[1] == surv_owner:
                planet[5] += surv
            else:
                planet[5] -= surv
                if planet[5] < 0:
                    planet[1] = surv_owner
                    planet[5] = -planet[5]
    return next_fid


def _evaluate_state(planets, fleets, me, n_players, P):
    """Economic eval: my (ships + prod*w + pos) minus best opponent's."""
    score = [0.0] * n_players
    prod = [0.0] * n_players
    pos = [0.0] * n_players
    alive = [False] * n_players
    for p in planets:
        o = p[1]
        if 0 <= o < n_players:
            score[o] += p[5]
            prod[o] += p[6]
            # positional: closer to center is slightly better (central control)
            d = math.hypot(p[2] - CENTER, p[3] - CENTER)
            pos[o] += max(0.0, (BOARD - d))
            alive[o] = True
    for f in fleets:
        o = f[1]
        if 0 <= o < n_players:
            score[o] += f[6] * P["fleet_weight"]
            alive[o] = True

    def total(i):
        return score[i] + P["prod_weight"] * prod[i] + P["pos_weight"] * pos[i]

    my = total(me)
    opp = [total(i) for i in range(n_players) if i != me]
    best_opp = max(opp) if opp else 0.0
    val = my - best_opp

    # terminal bonuses (eliminate opponents / avoid being eliminated)
    opp_alive = any(alive[i] for i in range(n_players) if i != me)
    if not opp_alive:
        val += P["win_bonus"]
    if not alive[me]:
        val -= P["loss_penalty"]
    return val


def _rollout(planets0, fleets0, my_action, me, n_players, ref_policies,
             info, av, max_speed, horizon, start_step, P):
    """Apply my_action this turn (opponents use ref policy), then roll H turns
    with BOTH players following the greedy Orbiter reference policy."""
    planets = [list(p) for p in planets0]
    fleets = [list(f) for f in fleets0]
    next_fid = (max((f[0] for f in fleets), default=-1)) + 1

    # First tick: me plays my_action, opponents play reference.
    actions = [None] * n_players
    for pl in range(n_players):
        if pl == me:
            actions[pl] = my_action
        else:
            obs = _make_obs(planets, fleets, pl, av, start_step)
            actions[pl] = ref_policies[pl](obs, None)
    dt = 1
    next_fid = _step_forward(planets, fleets, next_fid, actions, info, av,
                             dt, max_speed)

    # Remaining ticks: everyone plays reference policy.
    for h in range(1, horizon):
        # Early exit if game effectively decided.
        owners = set(p[1] for p in planets if p[1] != -1)
        owners.update(f[1] for f in fleets)
        if len(owners) <= 1:
            break
        actions = [None] * n_players
        for pl in range(n_players):
            obs = _make_obs(planets, fleets, pl, av, start_step + h)
            actions[pl] = ref_policies[pl](obs, None)
        dt = h + 1
        next_fid = _step_forward(planets, fleets, next_fid, actions, info, av,
                                 dt, max_speed)

    return _evaluate_state(planets, fleets, me, n_players, P)


# ----------------------------------------------------------------------------
# Candidate generation
# ----------------------------------------------------------------------------

def _gen_candidates(obs, config, me, n_players, av, step, max_speed, P):
    """Return list of (label, action) candidate full-turn action lists."""
    cands = []
    seen = set()

    def add(label, action):
        # de-dup identical action lists (cheap canonicalisation)
        key = tuple(sorted(
            (m[0], round(m[1], 4), int(m[2])) for m in action
            if isinstance(m, (list, tuple)) and len(m) == 3
        ))
        if key in seen:
            return
        seen.add(key)
        cands.append((label, action))

    # do-nothing / accumulate
    add("idle", [])

    moods = _CANDIDATE_MOODS[: max(1, P["max_candidates"] - 1)]
    for i, ov in enumerate(moods):
        try:
            ag = _orbiter_make_agent(ov)
            action = ag(obs, config) or []
        except Exception:
            action = []
        add("mood%d" % i, action)

    return cands[: P["max_candidates"]]


# ----------------------------------------------------------------------------
# Main decision
# ----------------------------------------------------------------------------

def _decide(obs, config, P, ref_default):
    t0 = time.time()
    g = _obs_get(obs)
    me = g("player", 0) or 0
    raw_planets = g("planets", []) or []
    raw_fleets = g("fleets", []) or []
    av = g("angular_velocity", 0.0) or 0.0
    step = g("step", 0) or 0
    overage = g("remainingOverageTime", 0.0) or 0.0

    max_speed = MAX_SPEED_DEFAULT
    if config is not None:
        cs = config.get("shipSpeed") if isinstance(config, dict) \
            else getattr(config, "shipSpeed", None)
        if cs:
            max_speed = float(cs)

    planets = [list(p) for p in raw_planets]
    fleets = [list(f) for f in raw_fleets]
    mine = [p for p in planets if p[1] == me]
    if not mine:
        return []

    # Determine player count from owners present (2 in our matches; supports 4).
    owners = set(p[1] for p in planets if p[1] != -1)
    owners.update(f[1] for f in fleets)
    owners.add(me)
    n_players = max(2, max(owners) + 1)

    # Reference policies for the rollout: greedy Orbiter for every seat.
    ref_policies = [ref_default] * n_players

    # Time budget (dip into overage only when plentiful).
    budget = P["time_budget"]
    if overage > P["overage_plenty"]:
        budget = max(budget, P["overage_budget"])

    info = _build_initial(planets)
    horizon = int(P["horizon"])
    # Adaptive horizon: a single rollout costs ~ horizon * fleets * planets.
    # Keep even the first (worst) rollout bounded in the crowded mid-game.
    work = max(1, len(planets)) * max(1, len(fleets))
    if work > 1200:
        horizon = max(6, int(horizon * 1200.0 / work))

    candidates = _gen_candidates(obs, config, me, n_players, av, step,
                                 max_speed, P)
    if not candidates:
        return []

    best_action = candidates[0][1]
    best_val = -float("inf")

    # Cost guard: track worst observed rollout time; stop before any rollout
    # that would risk overrunning the budget. Always evaluate >=1 candidate
    # (the greedy mood at index 1) so we never regress to idle on a slow turn.
    n_done = 0
    per_rollout = 0.0
    for label, action in candidates:
        elapsed = time.time() - t0
        if n_done > 0 and elapsed + per_rollout * 1.15 > budget:
            break
        r0 = time.time()
        try:
            val = _rollout(planets, fleets, action, me, n_players,
                           ref_policies, info, av, max_speed, horizon,
                           step, P)
        except Exception:
            val = -float("inf")
        rt = time.time() - r0
        per_rollout = rt if per_rollout == 0.0 else max(per_rollout, rt)
        n_done += 1
        if val > best_val:
            best_val = val
            best_action = action

    return best_action


def make_agent(params=None):
    P = dict(PARAMS)
    if params:
        P.update(params)
    # one shared reference policy instance (greedy Orbiter, baked params)
    ref_default = _orbiter_make_agent()

    def agent(obs, config=None):
        try:
            return _decide(obs, config, P, ref_default)
        except Exception:
            return []

    return agent


# module-level default agent (league.py loads `mod.agent` for file: specs)
agent = make_agent()
