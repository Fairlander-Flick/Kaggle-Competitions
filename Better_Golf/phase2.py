"""Phase-2 loop: data-driven cheap recompile, official-verify, A/B vs blend.

For every task: run the static-shape detector cascade (engine.scalar_onnx),
official-verify the candidate (engine.verify = neurogolf_utils path verbatim),
and if it passes ALL train+test+arc-gen AND is strictly cheaper than the
current blend pick, write it to out/onnx/taskNNN.onnx. A later `python
blend.py` then auto-merges (cheapest-valid-wins) into out/submission.zip.

Run: python phase2.py [--limit N]
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path

from engine import dataio, scalar_onnx, verify

BASE = Path(__file__).parent
ONNX = BASE / "out" / "onnx"
BR = BASE / "logs" / "blend_results.json"


def pts(cost):
    return max(1.0, 25.0 - math.log(max(1.0, cost)))


def main(limit=400):
    blend = json.load(open(BR)) if BR.exists() else {}
    ONNX.mkdir(parents=True, exist_ok=True)
    found = passed = won = 0
    gain = 0.0
    rows = []
    for n in range(1, limit + 1):
        try:
            d = scalar_onnx.detect(n)
        except Exception as e:  # noqa: BLE001
            d = None
        if not d:
            continue
        found += 1
        label, model, est = d
        task = dataio.load_task(n)
        vr = verify.verify(model, task, n)
        if not vr["ok"]:
            rows.append(f"  task{n:03d} {label:14s} FAIL "
                        f"(nfail={vr['n_fail']} {vr['err'][:40]})")
            continue
        passed += 1
        new_pts = vr["points"]
        cur = blend.get(f"{n:03d}")
        cur_pts = cur["points"] if cur else 0.0
        mark = ""
        if new_pts > cur_pts + 1e-6:
            won += 1
            gain += new_pts - cur_pts
            onnx_path = ONNX / f"task{n:03d}.onnx"
            import onnx as _o
            _o.save(model, str(onnx_path))
            mark = f"  WIN +{new_pts - cur_pts:5.2f} (was {cur_pts:.2f})"
        rows.append(f"  task{n:03d} {label:14s} ok {new_pts:6.2f}"
                    f" mem={vr['memory']} par={vr['params']}{mark}")
    for r in rows:
        print(r)
    print(f"\ndetected={found} verified_ok={passed} improved={won} "
          f"projected_gain=+{gain:.1f} pts")
    print("next: python blend.py  (auto-merges cheapest-valid)")


if __name__ == "__main__":
    lim = 400
    if "--limit" in sys.argv:
        lim = int(sys.argv[sys.argv.index("--limit") + 1])
    main(lim)
