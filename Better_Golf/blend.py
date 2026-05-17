"""Phase-1 BASE blend: official-grader-validated cheapest-valid-per-task.

Gathers every taskNNN.onnx candidate from Better_Golf/sources/** (zips or
loose) plus our own out/onnx/*.onnx, ranks candidates per task by a fast
static cost estimate, then runs the OFFICIAL verifier (engine.verify.verify
= neurogolf_utils path verbatim) cheapest-first and accepts the first that
passes ALL train+test+arc-gen and is measurable. This auto-rejects loophole
/ dynamic-shape / banned-op / >1.44MB models (they disqualify officially) →
the result is refresh-durable and legitimate.

Outputs: out/submission.zip (exact name) + logs/blend_results.json.
Run: python blend.py [--limit N]
"""
from __future__ import annotations
import io, json, math, os, re, sys, zipfile
from pathlib import Path

import onnx

from engine import dataio, verify

BASE = Path(__file__).parent
SRC = BASE / "sources"
ONNX_OURS = BASE / "out" / "onnx"
OUT_ZIP = BASE / "out" / "submission.zip"
RESJSON = BASE / "logs" / "blend_results.json"
TASK_RE = re.compile(r"task0*(\d{1,3})\.onnx$", re.I)
BANNED = {"Loop", "Scan", "NonZero", "Unique", "Script", "Function", "Compress"}
MAXB = 1_440_000
_TB = {1: 4, 2: 1, 3: 1, 4: 2, 5: 2, 6: 4, 7: 8, 9: 1, 10: 2, 11: 8, 16: 2}


def fast_cost(raw: bytes):
    """Cheap static rank metric (params + tensor bytes); None if obviously
    invalid. Real acceptance is the official verifier, not this."""
    if len(raw) > MAXB:
        return None
    try:
        m = onnx.load_from_string(raw)
        m = onnx.shape_inference.infer_shapes(m)
    except Exception:
        return None
    p = nb = 0
    sh = {}
    for init in m.graph.initializer:
        n = math.prod(init.dims) if init.dims else 1
        p += n
        nb += n * _TB.get(init.data_type, 4)
        sh[init.name] = init.dims
    for vi in list(m.graph.value_info) + list(m.graph.output):
        s = []
        for d in vi.type.tensor_type.shape.dim:
            if d.HasField("dim_value"):
                s.append(d.dim_value)
            else:
                return None  # dynamic -> officially invalid
        if s and vi.name not in ("input", "output"):
            nb += math.prod(s) * _TB.get(vi.type.tensor_type.elem_type, 4)
    for node in m.graph.node:
        if node.op_type in BANNED:
            return None
        if node.op_type == "Constant":
            for a in node.attribute:
                if a.name == "value":
                    p += math.prod(a.t.dims) if a.t.dims else 1
    return p + nb


def gather():
    """task_num -> list[(fast_cost, raw_bytes, source_label)]"""
    cand = {}
    files = []
    if SRC.exists():
        files += list(SRC.rglob("*"))
    if ONNX_OURS.exists():
        files += [(p) for p in ONNX_OURS.glob("task*.onnx")]
    for f in files:
        f = Path(f)
        if f.is_dir():
            continue
        if f.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(f) as zf:
                    for nm in zf.namelist():
                        mm = TASK_RE.search(os.path.basename(nm))
                        if not mm:
                            continue
                        raw = zf.read(nm)
                        fc = fast_cost(raw)
                        if fc is None:
                            continue
                        cand.setdefault(int(mm.group(1)), []).append(
                            (fc, raw, f.name))
            except Exception:
                pass
        elif f.suffix.lower() == ".onnx":
            mm = TASK_RE.search(f.name)
            if not mm:
                continue
            raw = f.read_bytes()
            fc = fast_cost(raw)
            if fc is None:
                continue
            cand.setdefault(int(mm.group(1)), []).append(
                (fc, raw, f.parent.name))
    return cand


def main(limit=400):
    cand = gather()
    print(f"sources: {sum(len(v) for v in cand.values())} candidate ONNX "
          f"across {len(cand)} tasks")
    results = {}
    picked = {}
    total = 0.0
    for n in range(1, limit + 1):
        lst = sorted(cand.get(n, []), key=lambda x: x[0])
        if not lst:
            continue
        task = dataio.load_task(n)
        for fc, raw, srclabel in lst:
            try:
                model = onnx.load_from_string(raw)
            except Exception:
                continue
            vr = verify.verify(model, task, n)
            if vr["ok"]:
                picked[n] = raw
                total += vr["points"]
                results[f"{n:03d}"] = {
                    "task": n, "points": round(vr["points"], 3),
                    "memory": vr["memory"], "params": vr["params"],
                    "source": srclabel, "n_cand": len(lst)}
                break
        done = len(picked)
        if n % 25 == 0:
            print(f"  ..task{n:03d}  picked={done}  proj={total:.1f}")
    OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for n, raw in sorted(picked.items()):
            zf.writestr(f"task{n:03d}.onnx", raw)
    RESJSON.parent.mkdir(parents=True, exist_ok=True)
    json.dump(results, open(RESJSON, "w"), indent=1, sort_keys=True)
    print(f"\nDONE. valid picks={len(picked)}/400  projected={total:.2f} pts"
          f"  -> {OUT_ZIP}  ({OUT_ZIP.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    lim = 400
    if "--limit" in sys.argv:
        lim = int(sys.argv[sys.argv.index("--limit") + 1])
    main(lim)
