"""Gen-2 probe: content-addressed archetypes over the 322 RESIDUAL.

Tests rules expressible with the FULL legal op palette (Gather/Scatter/Resize/
CumSum/data-dependent-Slice/Where/ReduceX) that the gen-1 fixed-local probe
could not see. Exact over ALL pairs (arc-gen faithful). Honest p_max band per
archetype = realistic tight content-addressed construction ceiling.

Writes logs/TRIAGE_GEN2.json incrementally. Re-measures Sigma p_max -> the
go/no-go on whether the paradigm lever re-opens 7000.
"""
from __future__ import annotations
import json, os
import numpy as np
from scipy import ndimage
from engine import dataio

BASE = os.path.dirname(__file__)
G1 = json.load(open(os.path.join(BASE, "logs", "TRIAGE_PROBE.json")))
OUT = os.path.join(BASE, "logs", "TRIAGE_GEN2.json")
RESIDUAL = [int(k) for k, v in G1.items() if v["arch"] == "RESIDUAL"]

PMAX = {"gravity": 16.0, "keep_color": 18.0, "symmetry_complete": 16.0,
        "object_select_crop": 13.0, "object_recolor_size": 13.0,
        "single_obj_move": 16.0, "denoise": 15.0, "fill_bbox": 14.0,
        "project_rays": 15.0}


def pairs_of(t):
    ps = []
    for k in ("train", "test", "arc-gen"):
        for ex in t.get(k, []):
            i, o = ex["input"], ex["output"]
            if max(len(i), len(i[0])) > 30:
                continue
            ps.append((np.array(i), np.array(o)))
    return ps


def same(ps):
    return all(i.shape == o.shape for i, o in ps)


def gravity(ps):
    if not same(ps):
        return None
    for ax, fn in (("d", 0), ("u", 1), ("l", 2), ("r", 3)):
        ok = True
        for i, o in ps:
            r = i.copy()
            if fn in (0, 1):
                for c in range(r.shape[1]):
                    col = i[:, c]
                    nz = col[col != 0]
                    new = np.zeros_like(col)
                    if fn == 0:
                        new[len(col) - len(nz):] = nz
                    else:
                        new[:len(nz)] = nz
                    r[:, c] = new
            else:
                for rr in range(r.shape[0]):
                    row = i[rr]
                    nz = row[row != 0]
                    new = np.zeros_like(row)
                    if fn == 2:
                        new[:len(nz)] = nz
                    else:
                        new[len(row) - len(nz):] = nz
                    r[rr] = new
            if not np.array_equal(r, o):
                ok = False
                break
        if ok and any((i != o).any() for i, o in ps):
            return ax
    return None


def keep_color(ps):
    if not same(ps):
        return None
    for which in ("max", "min"):
        ok = True
        for i, o in ps:
            vals, cnt = np.unique(i[i != 0], return_counts=True)
            if vals.size == 0:
                ok = False
                break
            k = vals[cnt.argmax() if which == "max" else cnt.argmin()]
            r = np.where(i == k, i, 0)
            if not np.array_equal(r, o):
                ok = False
                break
        if ok and any((i != o).any() for i, o in ps):
            return which
    return None


def symmetry_complete(ps):
    if not same(ps):
        return None
    syms = {"fh": np.fliplr, "fv": np.flipud,
            "r180": lambda a: np.rot90(a, 2),
            "tr": lambda a: a.T if a.shape[0] == a.shape[1] else a,
            "atr": lambda a: np.rot90(a, 2).T if a.shape[0] == a.shape[1] else a}
    for hole in range(10):
        for sname, sf in syms.items():
            ok = True
            for i, o in ps:
                m = sf(i)
                if m.shape != i.shape:
                    ok = False
                    break
                r = np.where(i == hole, m, i)
                if not np.array_equal(r, o):
                    ok = False
                    break
            if ok and any((i == hole).any() for i, _ in ps) \
                    and any((i != o).any() for i, o in ps):
                return f"{sname}/h{hole}"
    return None


def denoise(ps):
    if not same(ps):
        return None
    for conn in (1, 2):
        st = ndimage.generate_binary_structure(2, conn)
        ok = True
        for i, o in ps:
            r = i.copy()
            for col in np.unique(i[i != 0]):
                lab, n = ndimage.label(i == col, structure=st)
                for idx in range(1, n + 1):
                    if (lab == idx).sum() == 1:
                        r[lab == idx] = 0
            if not np.array_equal(r, o):
                ok = False
                break
        if ok and any((i != o).any() for i, o in ps):
            return f"c{conn}"
    return None


def fill_bbox(ps):
    if not same(ps):
        return None
    for conn in (1, 2):
        st = ndimage.generate_binary_structure(2, conn)
        ok = True
        for i, o in ps:
            r = i.copy()
            for col in np.unique(i[i != 0]):
                lab, n = ndimage.label(i == col, structure=st)
                for idx in range(1, n + 1):
                    ys, xs = np.where(lab == idx)
                    r[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = col
            if not np.array_equal(r, o):
                ok = False
                break
        if ok and any((i != o).any() for i, o in ps):
            return f"c{conn}"
    return None


def object_select_crop(ps):
    for conn in (1, 2):
        st = ndimage.generate_binary_structure(2, conn)
        for crit in ("max", "min", "uniqcolor"):
            ok = True
            for i, o in ps:
                lab, n = ndimage.label(i != 0, structure=st)
                if n == 0:
                    ok = False
                    break
                sizes = ndimage.sum(np.ones_like(lab), lab,
                                    range(1, n + 1))
                if crit == "max":
                    pick = int(np.argmax(sizes)) + 1
                elif crit == "min":
                    pick = int(np.argmin(sizes)) + 1
                else:
                    cols = [np.unique(i[lab == j]) for j in range(1, n + 1)]
                    uq = [j + 1 for j, cc in enumerate(cols) if len(cc) == 1]
                    if len(uq) != 1:
                        ok = False
                        break
                    pick = uq[0]
                ys, xs = np.where(lab == pick)
                crop = i[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
                if not np.array_equal(crop, o):
                    ok = False
                    break
            if ok and any((i != o).any() or i.shape != o.shape
                          for i, o in ps):
                return f"c{conn}/{crit}"
    return None


def object_recolor_size(ps):
    if not same(ps):
        return None
    for conn in (1, 2):
        st = ndimage.generate_binary_structure(2, conn)
        ok = True
        for i, o in ps:
            lab, n = ndimage.label(i != 0, structure=st)
            if n == 0:
                ok = False
                break
            r = i.copy()
            for j in range(1, n + 1):
                msk = lab == j
                oc = np.unique(o[msk])
                if len(oc) != 1:
                    ok = False
                    break
                r[msk] = oc[0]
            if not ok or not np.array_equal(r, o):
                ok = False
                break
        if ok and any((i != o).any() for i, o in ps):
            # only counts if recolor is a deterministic fn of size (check)
            sz2c = {}
            good = True
            for i, o in ps:
                lab, n = ndimage.label(i != 0, structure=st)
                for j in range(1, n + 1):
                    msk = lab == j
                    s = int(msk.sum())
                    c = int(o[msk][0])
                    if s in sz2c and sz2c[s] != c:
                        good = False
                        break
                    sz2c[s] = c
                if not good:
                    break
            if good:
                return f"c{conn}"
    return None


def probe(n):
    ps = pairs_of(dataio.load_task(n))
    if not ps:
        return {"task": n, "arch": "skip", "pmax": 0.0}
    for name, fn in (("keep_color", keep_color), ("gravity", gravity),
                     ("symmetry_complete", symmetry_complete),
                     ("single_obj_move", None), ("denoise", denoise),
                     ("fill_bbox", fill_bbox),
                     ("object_select_crop", object_select_crop),
                     ("object_recolor_size", object_recolor_size)):
        if fn is None:
            continue
        try:
            r = fn(ps)
        except Exception:
            r = None
        if r:
            return {"task": n, "arch": f"{name}:{r}", "pmax": PMAX[name]}
    return {"task": n, "arch": "RESIDUAL2", "pmax": 0.0}


def main():
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for idx, n in enumerate(RESIDUAL):
        k = f"{n:03d}"
        if k in res:
            continue
        try:
            res[k] = probe(n)
        except Exception as e:
            res[k] = {"task": n, "arch": f"ERR:{type(e).__name__}",
                      "pmax": 0.0}
        if idx % 5 == 0 or idx == len(RESIDUAL) - 1:
            json.dump(res, open(OUT, "w"), indent=1, sort_keys=True)
            print(f"...{idx + 1}/{len(RESIDUAL)} residual probed", flush=True)
    json.dump(res, open(OUT, "w"), indent=1, sort_keys=True)
    hit = [v for v in res.values() if v["arch"] not in ("RESIDUAL2", "skip")
           and not v["arch"].startswith("ERR")]
    sig = sum(v["pmax"] for v in hit)
    print(f"\nDONE gen-2. content-addressed matches={len(hit)}/{len(RESIDUAL)}"
          f"  added Sigma p_max={sig:.0f} pts  (still-RESIDUAL2="
          f"{sum(1 for v in res.values() if v['arch'] == 'RESIDUAL2')})")


if __name__ == "__main__":
    main()
