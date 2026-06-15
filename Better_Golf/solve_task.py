#!/usr/bin/env python
"""Solve ONE task with the families engine (no shared-file write — array-safe),
compare to the public base cost, and emit a per-task JSON verdict to
logs/sweep/taskNNN.json. solve_one already saves a solved graph to
out/onnx/taskNNN.onnx (unique filename => no race). A win = families graph is
strictly cheaper than the base graph for that task (true-rule => private-safe).

Usage: solve_task.py <task_num>
"""
from __future__ import annotations
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import solve

COST = json.load(open(os.path.join(os.path.dirname(__file__),
                                   "logs/vyank_costmap.json")))


def main():
    n = int(sys.argv[1])
    base = COST.get(str(n))
    base_pts = max(1.0, 25 - math.log(max(1, base))) if base else None
    out = {"task": n, "status": "unsolved", "family": None, "points": 0.0,
           "cost": None, "base_cost": base, "base_pts": base_pts,
           "win": False, "delta": 0.0}
    try:
        r = solve.solve_one(n, persist=False)
        if r["status"] == "solved":
            c = (r["memory"] or 0) + (r["params"] or 0)
            out.update(status="solved", family=r["family"],
                       points=round(r["points"], 4), cost=c)
            if base and c < base:
                out["win"] = True
                out["delta"] = round(r["points"] - base_pts, 4)
        else:
            out["note"] = r.get("note", "")[:60]
    except Exception as e:  # noqa: BLE001
        out["note"] = f"{type(e).__name__}: {e}"[:80]
    os.makedirs("logs/sweep", exist_ok=True)
    json.dump(out, open(f"logs/sweep/task{n:03d}.json", "w"))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
