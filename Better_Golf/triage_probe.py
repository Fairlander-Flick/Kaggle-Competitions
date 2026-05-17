"""Rigorous per-task rule prober for the go/no-go on the 7000 thesis.

For EVERY task it tests a battery of EXACT rule predicates over ALL pairs
(train+test+arc-gen, grader-identical, >30 grids skipped like the grader).
A predicate is a match only if it holds on 100% of pairs -> it is the true
generalizing rule -> a real, honest p_max can be attached.

Writes logs/TRIAGE_PROBE.json incrementally (one task at a time) so a timeout
still yields partial truth. Prints a Sigma p_max projection at the end.

p_max = realistic tight-golf ceiling of the cheapest correct construction for
that archetype (honest: capped families stay capped). Unmatched -> 0 (the
conservative residual; its real value is the open question this measures).
"""
from __future__ import annotations
import json, math, os, sys
import numpy as np
from engine import dataio

BASE = os.path.dirname(__file__)
OUT = os.path.join(BASE, "logs", "TRIAGE_PROBE.json")

# realistic tight-golf p_max per archetype (see reasoning in chat)
PMAX = {
    "identity": 25.0, "transpose": 25.0, "geom": 24.0,
    "color_permute": 22.7, "color_lut": 20.4,
    "nbhd_k3": None, "nbhd_k5": None,   # computed from pattern count P
    "flood_fill": 13.0, "crop_bbox": 14.0, "int_scale": 14.0,
    "tiling": 14.0, "mirror_double": 14.0, "symmetry_fill": 14.0,
}


def pairs_of(t):
    ps = []
    for k in ("train", "test", "arc-gen"):
        for ex in t.get(k, []):
            i, o = ex["input"], ex["output"]
            if max(len(i), len(i[0])) > 30:
                continue
            ps.append((np.array(i), np.array(o)))
    return ps


def all_same_shape(ps):
    return all(i.shape == o.shape for i, o in ps)


# ---- exact predicates over ALL pairs --------------------------------------
def is_identity(ps):
    return all_same_shape(ps) and all(np.array_equal(i, o) for i, o in ps)


def geom_kind(ps):
    cands = {
        "transpose": lambda a: a.T,
        "flip_h": np.fliplr, "flip_v": np.flipud,
        "rot90": lambda a: np.rot90(a, 1),
        "rot180": lambda a: np.rot90(a, 2),
        "rot270": lambda a: np.rot90(a, 3),
    }
    for name, fn in cands.items():
        if all(i.shape[::-1] == o.shape or i.shape == o.shape for i, o in ps) \
                and all(np.array_equal(fn(i), o) for i, o in ps):
            return name
    return None


def color_map(ps):
    """Cellwise consistent color->color over all pairs (same shape)."""
    if not all_same_shape(ps):
        return None
    m = {}
    for i, o in ps:
        for a, b in zip(i.flatten(), o.flatten()):
            a, b = int(a), int(b)
            if a in m and m[a] != b:
                return None
            m[a] = b
    return m


def window_lut(ps, K):
    """Single-valued K x K window -> out-cell over all pairs. Returns #patterns
    or None if not single-valued / shapes differ."""
    if not all_same_shape(ps):
        return None
    rad = K // 2
    lut = {}
    for i, o in ps:
        H, W = i.shape
        ip = np.full((H + 2 * rad, W + 2 * rad), -1, dtype=int)
        ip[rad:rad + H, rad:rad + W] = i
        for r in range(H):
            for c in range(W):
                key = tuple(ip[r:r + 2 * rad + 1, c:c + 2 * rad + 1].flatten())
                v = int(o[r, c])
                if key in lut and lut[key] != v:
                    return None
                lut[key] = v
    return len(lut)


def flood_enclosed(ps):
    """0-cells not 4-connected to border -> single consistent fill color."""
    if not all_same_shape(ps):
        return None
    fills = set()
    for i, o in ps:
        ch = i != o
        if ch.any():
            if (i[ch] != 0).any():
                return None
            fills |= set(o[ch].tolist())
    if len(fills) != 1:
        return None
    fill = fills.pop()
    for i, o in ps:
        a = i
        H, W = a.shape
        free = (a == 0)
        R = np.zeros_like(free)
        st = [(r, c) for r in range(H) for c in range(W)
              if (r in (0, H - 1) or c in (0, W - 1)) and free[r, c]]
        for s in st:
            R[s] = True
        st = list(st)
        while st:
            r, c = st.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < H and 0 <= nc < W and free[nr, nc] and not R[nr, nc]:
                    R[nr, nc] = True
                    st.append((nr, nc))
        out = a.copy()
        out[(a == 0) & (~R)] = fill
        if not np.array_equal(out, o):
            return None
    return fill


def crop_bbox(ps):
    for i, o in ps:
        nz = np.argwhere(i != 0)
        if nz.size == 0:
            return False
        r0, c0 = nz.min(0)
        r1, c1 = nz.max(0)
        if not np.array_equal(i[r0:r1 + 1, c0:c1 + 1], o):
            return False
    return True


def int_scale(ps):
    ks = set()
    for i, o in ps:
        if o.shape[0] % i.shape[0] or o.shape[1] % i.shape[1]:
            return None
        ky, kx = o.shape[0] // i.shape[0], o.shape[1] // i.shape[1]
        if ky != kx or ky < 2:
            return None
        if not np.array_equal(np.kron(i, np.ones((ky, kx), int)), o):
            return None
        ks.add(ky)
    return ks.pop() if len(ks) == 1 else None


def tiling(ps):
    for i, o in ps:
        if o.shape[0] % i.shape[0] or o.shape[1] % i.shape[1]:
            return False
        my, mx = o.shape[0] // i.shape[0], o.shape[1] // i.shape[1]
        if (my, mx) == (1, 1):
            return False
        if not np.array_equal(np.tile(i, (my, mx)), o):
            return False
    return True


def mirror_double(ps):
    fns = {
        "v_mir_down": lambda a: np.vstack([a, np.flipud(a)]),
        "v_mir_up": lambda a: np.vstack([np.flipud(a), a]),
        "v_tile": lambda a: np.vstack([a, a]),
        "h_mir_right": lambda a: np.hstack([a, np.fliplr(a)]),
        "h_mir_left": lambda a: np.hstack([np.fliplr(a), a]),
        "h_tile": lambda a: np.hstack([a, a]),
    }
    for name, fn in fns.items():
        if all(np.array_equal(fn(i), o) for i, o in ps):
            return name
    return None


def symmetry_fill(ps):
    """Output = input with 0s filled by a global mirror (h or v)."""
    if not all_same_shape(ps):
        return None
    for ax in ("v", "h"):
        ok = True
        for i, o in ps:
            mir = np.flipud(i) if ax == "v" else np.fliplr(i)
            f = i.copy()
            z = f == 0
            f[z] = mir[z]
            if not np.array_equal(f, o):
                ok = False
                break
        if ok and any((i == 0).any() for i, _ in ps):
            return ax
    return None


def nbhd_pmax(P, K):
    # LocalNeighborhood: W1[P,10,K,K]+b[P]+W2[10,P,1,1]; relu/conv tensors
    params = P * 10 * K * K + P + 10 * P
    memory = P * 3600 + 36000
    return max(1.0, 25.0 - math.log(max(1.0, memory + params)))


def probe_task(n):
    t = dataio.load_task(n)
    ps = pairs_of(t)
    if not ps:
        return {"task": n, "arch": "skip_big", "pmax": 0.0}
    if is_identity(ps):
        return {"task": n, "arch": "identity", "pmax": 25.0}
    g = geom_kind(ps)
    if g:
        return {"task": n, "arch": f"geom:{g}",
                "pmax": 25.0 if g == "transpose" else 24.0}
    cm = color_map(ps)
    if cm is not None:
        vals = set(cm.values())
        perm = (set(cm.keys()) == vals and len(cm) == len(vals))
        return {"task": n, "arch": "color_permute" if perm else "color_lut",
                "pmax": 22.7 if perm else 20.4}
    fl = flood_enclosed(ps)
    if fl is not None:
        return {"task": n, "arch": f"flood_fill:{fl}", "pmax": 13.0}
    if crop_bbox(ps):
        return {"task": n, "arch": "crop_bbox", "pmax": 14.0}
    k = int_scale(ps)
    if k:
        return {"task": n, "arch": f"int_scale:{k}", "pmax": 14.0}
    if tiling(ps):
        return {"task": n, "arch": "tiling", "pmax": 14.0}
    md = mirror_double(ps)
    if md:
        return {"task": n, "arch": f"mirror_double:{md}", "pmax": 14.0}
    sf = symmetry_fill(ps)
    if sf:
        return {"task": n, "arch": f"symmetry_fill:{sf}", "pmax": 14.0}
    for K in (3, 5):
        P = window_lut(ps, K)
        if P is not None:
            return {"task": n, "arch": f"nbhd_k{K}:P={P}",
                    "pmax": round(nbhd_pmax(P, K), 2)}
    # unmatched residual: record weak structural signal for the discussion
    ss = all_same_shape(ps)
    ic = sorted({int(c) for i, _ in ps for c in i.flatten()})
    oc = sorted({int(c) for _, o in ps for c in o.flatten()})
    return {"task": n, "arch": "RESIDUAL", "pmax": 0.0,
            "same_shape": ss, "in_colors": ic, "out_colors": oc}


def main():
    res = {}
    if os.path.exists(OUT):
        res = json.load(open(OUT))
    for n in range(1, 401):
        k = f"{n:03d}"
        if k in res:
            continue
        try:
            res[k] = probe_task(n)
        except Exception as e:
            res[k] = {"task": n, "arch": f"ERR:{type(e).__name__}", "pmax": 0.0}
        if n % 5 == 0 or n == 400:
            json.dump(res, open(OUT, "w"), indent=1, sort_keys=True)
            print(f"...probed {n}/400", flush=True)
    json.dump(res, open(OUT, "w"), indent=1, sort_keys=True)
    sig = sum(v["pmax"] for v in res.values())
    nres = sum(1 for v in res.values() if v["arch"] == "RESIDUAL")
    feas = sum(1 for v in res.values()
               if v["arch"] not in ("RESIDUAL",) and not v["arch"].startswith("ERR")
               and not v["arch"].startswith("skip"))
    print(f"\nDONE. matched={feas}/400  RESIDUAL={nres}  "
          f"Sigma p_max(matched-only, conservative)={sig:.0f} pts")


if __name__ == "__main__":
    main()
