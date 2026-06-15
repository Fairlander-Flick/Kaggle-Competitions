#!/usr/bin/env python
"""Per-task symbolic superoptimizer for NeuroGolf-2026.

For one task: take the base graph, apply a registry of SEMANTICS-PRESERVING
rewrites (and combinations), grade every variant with the OFFICIAL verifier,
and keep the cheapest variant that is exact (n_fail==0, measurable) AND strictly
cheaper than the base graph's own verified cost. Lossless rewrites of an
already-correct graph pass the private holdout iff the base does => they realize
1:1 on the leaderboard (the safe lever). New constructors can be added to
REWRITERS later; harvest gates risky ones behind LB confirmation.

Usage: superopt.py <task> [--base out/submission.best-6373.zip]
"""
from __future__ import annotations
import argparse, copy, io, json, math, os, sys, tempfile, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, onnx
from onnx import TensorProto
from engine import dataio
from engine.verify import verify

BASE_ZIP = "out/submission.best-6373.zip"
SEARCH_DIR = "out/search"
BEST = "logs/best.json"


def load_base_model(zip_path, n):
    with zipfile.ZipFile(zip_path) as z:
        name = f"task{n:03d}.onnx"
        if name not in z.namelist():
            return None
        return onnx.load_model_from_string(z.read(name))


# --- rewriters: each takes a ModelProto, returns a new ModelProto or None ----
def rw_simplify(m):
    try:
        from onnxsim import simplify
        sm, ok = simplify(m)
        return sm if ok else None
    except Exception:
        return None


def rw_optimizer(m):
    try:
        import onnxoptimizer
        passes = ["eliminate_deadend", "eliminate_identity",
                  "eliminate_nop_cast", "eliminate_nop_transpose",
                  "eliminate_unused_initializer", "fuse_consecutive_squeezes",
                  "fuse_consecutive_transposes", "eliminate_duplicate_initializer"]
        return onnxoptimizer.optimize(m, passes)
    except Exception:
        return None


def rw_drop_unused_init(m):
    """Remove initializers/constants no node consumes."""
    try:
        m = copy.deepcopy(m)
        used = set()
        for node in m.graph.node:
            used.update(node.input)
        keep = [i for i in m.graph.initializer if i.name in used]
        if len(keep) == len(m.graph.initializer):
            return None
        del m.graph.initializer[:]
        m.graph.initializer.extend(keep)
        return m
    except Exception:
        return None


REWRITERS = [rw_simplify, rw_optimizer, rw_drop_unused_init]


def cost_of(m, task, n):
    r = verify(m, task, n)
    if not r.get("ok"):
        return None, r
    return r["memory"] + r["params"], r


def superopt(n, base_zip):
    task = dataio.load_task(n)
    base = load_base_model(base_zip, n)
    if base is None:
        return {"task": n, "kept": False, "err": "no base graph"}
    base_cost, br = cost_of(base, task, n)
    if base_cost is None:
        return {"task": n, "kept": False, "err": "base not gradable: " + br.get("err", "")}

    best_m, best_cost = None, base_cost
    # try each rewriter alone and chained (simplify -> optimizer -> drop)
    chains = [[r] for r in REWRITERS] + [[rw_simplify, rw_optimizer, rw_drop_unused_init]]
    for chain in chains:
        m = base
        ok_chain = True
        for rw in chain:
            nm = rw(m)
            if nm is None:
                ok_chain = (rw is not chain[0])  # a no-op mid-chain is fine
                if nm is None and rw is chain[0]:
                    ok_chain = False
                    break
                continue
            m = nm
        if not ok_chain or m is base:
            continue
        c, r = cost_of(m, task, n)
        if c is not None and c < best_cost:
            best_cost, best_m = c, m

    res = {"task": n, "base_cost": base_cost, "new_cost": best_cost,
           "kept": best_m is not None}
    if best_m is not None:
        os.makedirs(SEARCH_DIR, exist_ok=True)
        onnx.save(best_m, os.path.join(SEARCH_DIR, f"task{n:03d}.onnx"))
        res["delta_pts"] = round((25 - math.log(max(1, best_cost)))
                                 - (25 - math.log(max(1, base_cost))), 4)
        _update_best(n, best_cost, res["delta_pts"], "rewrite")
    return res


def _update_best(n, cost, dpts, source):
    os.makedirs("logs", exist_ok=True)
    cur = {}
    if os.path.exists(BEST):
        try:
            cur = json.load(open(BEST))
        except Exception:
            cur = {}
    key = f"{n:03d}"
    if key not in cur or cost < cur[key]["cost"]:
        cur[key] = {"cost": int(cost), "delta_pts": dpts, "source": source}
        tmp = BEST + f".tmp{os.getpid()}"
        json.dump(cur, open(tmp, "w"), indent=0, sort_keys=True)
        os.replace(tmp, BEST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", type=int)
    ap.add_argument("--base", default=BASE_ZIP)
    a = ap.parse_args()
    print(json.dumps(superopt(a.task, a.base)))


if __name__ == "__main__":
    main()
