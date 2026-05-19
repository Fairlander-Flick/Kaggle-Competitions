"""Reproduce Octaviograu's grader-VALIDATED 5744.52 pipeline verbatim.

His notebook (intel/octaviograu_5743-35-canonical-onnx-fusions):
  BASE  = afr1ste/neurogolf-5689-51 for all tasks EXCEPT
          {205,308,370,382} -> konbu17/neurogolf-2026-blend-source-v3-6-0
          (this base = his grader-confirmed 5740.30)
  + 3 fusion patterns (P1 ReduceSum-chain, P2 Cast-chain, P3 bool dtype
    narrow) where they verify correct AND are strictly cheaper
          (-> his grader-confirmed 5744.52, +4.22)

Base is taken VERBATIM (he submitted it and got 5740.30 — no re-gating).
Fusion is applied only to tasks that have a candidate, gated by our
trusted engine.verify (correctness + cost) as a faithful proxy for his
accept rule. Target: ~5744 actual (+37 vs our genuine 5706.97). One
submit validates (his number is author-grader-confirmed, not a fake
name nor our static theory).

Run:  python repro_octavia.py
Out:  out/submission.octavia.zip + logs/repro_octavia.json
"""
from __future__ import annotations
import json, zipfile
from pathlib import Path

import onnx

from engine import dataio, verify as bgverify
from fusion_rewrite import candidates_for

BASE = Path(__file__).parent
AFR_ZIP = BASE / "sources" / "afr5689" / "submission.zip"
KONBU_DIR = BASE / "sources" / "hunt" / "konbu17"
OUT_ZIP = BASE / "out" / "submission.octavia.zip"
REPORT = BASE / "logs" / "repro_octavia.json"
KONBU_TASKS = {205, 308, 370, 382}
EPS = 1e-9


def main():
    az = zipfile.ZipFile(AFR_ZIP)
    afr = {}
    for nm in az.namelist():
        if nm.endswith(".onnx"):
            base = nm.split("/")[-1]
            afr[base] = az.read(nm)
    base_bytes = {}
    for n in range(1, 401):
        nm = f"task{n:03d}.onnx"
        if n in KONBU_TASKS:
            p = KONBU_DIR / nm
            base_bytes[nm] = p.read_bytes()
        else:
            base_bytes[nm] = afr[nm]
    print(f"base assembled: {len(base_bytes)} tasks "
          f"(konbu17 for {sorted(KONBU_TASKS)}, afr1ste-5689 else)")

    final = dict(base_bytes)
    fused = {}
    n_fused = 0
    for n in range(1, 401):
        nm = f"task{n:03d}.onnx"
        ob = base_bytes[nm]
        cands = list(candidates_for(ob))
        if not cands:
            continue
        task = dataio.load_task(n)
        try:
            bvr = bgverify.verify(onnx.load_from_string(ob), task, n)
            base_pts = bvr["points"] if bvr.get("ok") else 0.0
        except Exception:
            base_pts = 0.0
        best_b, best_p, best_l = ob, base_pts, "base"
        for lab, cand in cands:
            try:
                onnx.checker.check_model(cand, full_check=True)
            except Exception:
                continue
            try:
                vr = bgverify.verify(cand, task, n)
            except Exception:
                continue
            if (vr.get("ok") and vr.get("n_fail") == 0
                    and vr["points"] > best_p + EPS):
                best_b, best_p, best_l = (
                    cand.SerializeToString(), vr["points"], lab)
        if best_l != "base":
            final[nm] = best_b
            n_fused += 1
            fused[f"{n:03d}"] = {"task": n, "pattern": best_l,
                                 "base_pts": round(base_pts, 3),
                                 "new_pts": round(best_p, 3)}

    OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for nm, b in sorted(final.items()):
            zf.writestr(nm, b)
    sz = OUT_ZIP.stat().st_size
    big = [nm for nm, b in final.items() if len(b) > 1_440_000]
    out = {"base": "afr1ste-5689 + konbu17{205,308,370,382}",
           "his_base_lb": 5740.30, "his_target_lb": 5744.52,
           "our_prev_best": 5706.97,
           "tasks": len(final), "fused": n_fused,
           "zip_kb": round(sz / 1024), "files>1.44MB": big,
           "fused_detail": fused}
    json.dump(out, open(REPORT, "w"), indent=1, sort_keys=True)
    print(f"\nDONE. tasks={len(final)}/400 fused={n_fused} "
          f"zip={sz/1024:.0f}KB big={len(big)}")
    print(f"target: his base 5740.30 / +fusion 5744.52  "
          f"(our prev best 5706.97) -> {OUT_ZIP}")


if __name__ == "__main__":
    main()
