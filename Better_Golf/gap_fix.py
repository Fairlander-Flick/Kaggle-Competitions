"""Paradigm A remediation — swap the 23 grader-DQ-leaking tasks for the
cheapest candidate that is BOTH engine.verify-ok/measurable AND passes the
strict grader-DQ probe (gap_diagnose.dq_flags == clean).

Leak (gap_diagnose.py): 23 tasks engine.verify scores 13-17 but the real
grader scores 0 (`noshape`:20 / `unused_init`:3) = 339.6 LB = 76% of the
+445 projected<->actual gap. Fix only those tasks (A/B minimal; the other
377 files are untouched). A task with no DQ-clean candidate in any source
is left as-is (already ~0 on grader; no loss).

Honest accounting: a DQ-flagged file's REAL contribution is ~0, so we
report `dq_honest` = sum of points over DQ-clean files only (the realistic
actual estimate), alongside the naive engine.verify projected.

Run:  python gap_fix.py
Out:  out/submission.gapfix.zip + logs/gap_fix.json
"""
from __future__ import annotations
import json, zipfile
from pathlib import Path

import onnx

from engine import dataio, verify as bgverify
from blend import gather
from gap_diagnose import dq_flags

BASE = Path(__file__).parent
CUR_ZIP = BASE / "out" / "submission.zip"          # current best (fusion)
OUT_ZIP = BASE / "out" / "submission.gapfix.zip"
REPORT = BASE / "logs" / "gap_fix.json"
GAP_REPORT = BASE / "logs" / "gap_report.json"


def measurable(vr):
    return (vr.get("ok") and vr.get("n_fail") == 0
            and vr.get("memory") is not None
            and vr.get("params") is not None
            and vr.get("points", 0) > 1.0)


def main():
    gap = json.load(open(GAP_REPORT))
    leaking = [r["task"] for r in gap["rows"] if r["lb_at_risk"] > 0]
    print(f"leaking tasks (grader-DQ while engine ok): {len(leaking)} "
          f"-> {leaking}")
    z = zipfile.ZipFile(CUR_ZIP)
    blob = {nm: z.read(nm) for nm in z.namelist() if nm.endswith(".onnx")}
    cand = gather(include_ours=True)            # all sources/** + out/onnx

    fixed = {}
    still = {}
    for n in leaking:
        nm = f"task{n:03d}.onnx"
        task = dataio.load_task(n)
        lst = sorted(cand.get(n, []), key=lambda x: x[0])   # cheapest first
        chosen = None
        scanned = 0
        for fc, raw, src in lst:
            scanned += 1
            if dq_flags(raw):                   # still grader-DQ -> skip
                continue
            try:
                vr = bgverify.verify(onnx.load_from_string(raw), task, n)
            except Exception:
                continue
            if measurable(vr):
                chosen = (raw, src, vr["points"], vr["memory"],
                          vr["params"])
                break
        if chosen:
            blob[nm] = chosen[0]
            fixed[f"{n:03d}"] = {
                "task": n, "src": chosen[1],
                "new_points": round(chosen[2], 3),
                "mem": chosen[3], "par": chosen[4],
                "cands_scanned": scanned, "n_cands": len(lst)}
        else:
            still[f"{n:03d}"] = {"task": n, "n_cands": len(lst),
                                 "reason": "no DQ-clean valid candidate"}

    # write fixed bundle
    OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for nm, b in sorted(blob.items()):
            zf.writestr(nm, b)

    # honest accounting over the whole new bundle
    naive = dq_honest = 0.0
    still_flagged = []
    for nm, b in blob.items():
        n = int(nm[4:7])
        task = dataio.load_task(n)
        try:
            vr = bgverify.verify(onnx.load_from_string(b), task, n)
            p = vr["points"] if vr.get("ok") else 0.0
        except Exception:
            p = 0.0
        naive += p
        if dq_flags(b):
            still_flagged.append(n)
        else:
            dq_honest += p
    out = {
        "leaking_input": len(leaking),
        "fixed": len(fixed), "unfixable": len(still),
        "still_flagged_after": sorted(still_flagged),
        "naive_projected": round(naive, 2),
        "dq_honest_projected": round(dq_honest, 2),
        "prev_actual_ref": 5706.97,
        "fixed_detail": fixed, "unfixable_detail": still}
    json.dump(out, open(REPORT, "w"), indent=1, sort_keys=True)
    print(f"\nfixed={len(fixed)}  unfixable={len(still)}  "
          f"still_flagged_after={len(still_flagged)}")
    print(f"naive_projected={naive:.2f}  "
          f"dq_honest_projected={dq_honest:.2f}  "
          f"(prev actual 5706.97)")
    for k, v in sorted(fixed.items()):
        print(f"  task{k} <- {v['src'][:18]:18} {v['new_points']:.2f}pts "
              f"(mem {v['mem']} par {v['par']})")
    if still:
        print(f"unfixable (left as-is, ~0 on grader): "
              f"{sorted(int(k) for k in still)}")


if __name__ == "__main__":
    main()
