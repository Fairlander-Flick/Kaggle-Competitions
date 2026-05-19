"""Paradigm A — diagnose the ~7% projected<->actual gap (441 LB locked:
proj ~6149 vs actual 5706.97 on our genuine bundle).

The gap on a public-bundle blend is almost certainly the DISQUALIFICATION
class: files engine.verify accepts ("ok, N pts") that the REAL Kaggle
grader scores 0 because its stricter `check_network` / strict-mode shape
inference / banned-op / name rules trip. That divergence is detectable
STATICALLY (no ORT) — a second ORT-profiling oracle just re-derives
engine.verify's own cost (redundant) and segfaults under double profiling.

So: oracle#1 = engine.verify (trusted, mirrors neurogolf_utils) + a
pure-static grader-DQ probe stricter than engine.verify. A task that
engine.verify scores N but the DQ probe flags = LEAK candidate worth N LB.

Run:  python gap_diagnose.py [--limit N]
Out:  logs/gap_report.json (+ console top leaks)
"""
from __future__ import annotations
import json, sys, zipfile
from pathlib import Path

import onnx

from engine import dataio, verify as bgverify

BASE = Path(__file__).parent
SRC_ZIP = BASE / "out" / "submission.zip"          # current best bundle
REPORT = BASE / "logs" / "gap_report.json"
BANNED = {"Loop", "Scan", "NonZero", "Unique", "Script", "Function",
          "Compress"}


def dq_flags(model_bytes):
    """Reasons the REAL grader could score 0 even if engine.verify accepts.
    Empty list = clean (no static disqualification risk)."""
    flags = []
    if len(model_bytes) > 1_440_000:
        flags.append("filesize>1.44MB")
    m = onnx.load_from_string(model_bytes)
    if len(m.graph.input) != 1 or len(m.graph.output) != 1:
        flags.append(f"io={len(m.graph.input)}/{len(m.graph.output)}")
    in_names = {v.name for v in m.graph.input}
    out_names = {v.name for v in m.graph.output}
    init_names = {i.name for i in m.graph.initializer}
    used = set()
    for nd in m.graph.node:
        if nd.op_type in BANNED:
            flags.append(f"banned:{nd.op_type}")
        if nd.domain not in ("", "ai.onnx"):
            flags.append(f"domain:{nd.domain}")
        for inp in nd.input:
            if inp:
                used.add(inp)
        for o in nd.output:
            if "kernel_time" in o:
                flags.append("name:kernel_time")
    unused = [n for n in init_names if n not in used]
    if unused:
        flags.append(f"unused_init:{len(unused)}({unused[0][:16]})")
    if (init_names & in_names) or (init_names & out_names):
        flags.append("init/io_name_collision")
    if m.opset_import and m.opset_import[0].version < 7:
        flags.append(f"opset<{m.opset_import[0].version}")
    if m.functions:
        flags.append("graph_functions")
    # strict static-shape: any non-static intermediate dim under strict_mode
    # -> grader infer returns None -> 0 points (engine.verify uses a looser
    # path on some ORT versions).
    try:
        inf = onnx.shape_inference.infer_shapes(m, strict_mode=True,
                                                check_type=True)
        for vi in list(inf.graph.value_info) + list(inf.graph.output):
            if vi.name in ("input", "output"):
                continue
            sh = vi.type.tensor_type.shape
            if not sh.dim:
                flags.append(f"noshape:{vi.name[:16]}")
                break
            bad = False
            for d in sh.dim:
                if not d.HasField("dim_value") or d.dim_value <= 0:
                    bad = True
                    break
            if bad:
                flags.append(f"dyn_dim:{vi.name[:16]}")
                break
    except Exception as e:
        flags.append(f"shapeinfer_exc:{str(e)[:24]}")
    return flags


def main(limit=400):
    z = zipfile.ZipFile(SRC_ZIP)
    blob = {nm: z.read(nm) for nm in z.namelist() if nm.endswith(".onnx")}
    rows = []
    o1_total = 0.0
    for n in range(1, limit + 1):
        nm = f"task{n:03d}.onnx"
        if nm not in blob:
            continue
        b = blob[nm]
        task = dataio.load_task(n)
        try:
            v1 = bgverify.verify(onnx.load_from_string(b), task, n)
            ok = bool(v1.get("ok"))
            o1 = v1["points"] if ok else 0.0
        except Exception as e:
            v1 = {"ok": False, "err": str(e)[:30]}
            ok, o1 = False, 0.0
        try:
            fl = dq_flags(b)
        except Exception as e:
            fl = [f"dqprobe_exc:{str(e)[:24]}"]
        o1_total += o1
        rows.append({
            "task": n, "ok": ok, "points": round(o1, 3),
            "memory": v1.get("memory"), "params": v1.get("params"),
            "dq_flags": fl,
            "lb_at_risk": round(o1, 3) if (ok and fl) else 0.0})
        if n % 25 == 0:
            print(f"  ..task{n:03d}  o1_total={o1_total:.1f}")
    rows.sort(key=lambda r: -r["lb_at_risk"])
    flagged = [r for r in rows if r["lb_at_risk"] > 0]
    by_flag = {}
    for r in flagged:
        for f in r["dq_flags"]:
            key = f.split(":")[0]
            by_flag[key] = by_flag.get(key, 0) + 1
    out = {
        "bundle": SRC_ZIP.name,
        "o1_total_projected": round(o1_total, 3),
        "actual_lb_reference": 5706.97,
        "n_tasks": len(rows),
        "n_dq_flagged_while_ok": len(flagged),
        "lb_at_risk_total": round(sum(r["lb_at_risk"] for r in flagged), 2),
        "flag_histogram": dict(sorted(by_flag.items(),
                                      key=lambda kv: -kv[1])),
        "rows": rows}
    json.dump(out, open(REPORT, "w"), indent=1)
    print(f"\nprojected o1_total={o1_total:.2f}  (actual ref 5706.97; "
          f"gap~{o1_total-5706.97:+.1f})")
    print(f"DQ-flagged while engine.verify=ok: {len(flagged)} tasks  "
          f"LB-at-risk={sum(r['lb_at_risk'] for r in flagged):.1f}")
    print(f"flag histogram: {out['flag_histogram']}")
    print("--- top-25 leak candidates (engine ok but grader-DQ risk) ---")
    for r in flagged[:25]:
        print(f"  task{r['task']:03d} pts={r['points']:6.2f} "
              f"{r['dq_flags']}")


if __name__ == "__main__":
    lim = 400
    if "--limit" in sys.argv:
        lim = int(sys.argv[sys.argv.index("--limit") + 1])
    main(lim)
