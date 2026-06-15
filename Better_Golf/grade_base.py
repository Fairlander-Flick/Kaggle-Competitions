#!/usr/bin/env python
"""Grade ONE task's ACTUAL base-submission graph with the official verifier ->
true current points. Array-safe (per-task json). Usage: grade_base.py <n> [zip]"""
import sys, os, json, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import onnx
from engine import dataio
from engine.verify import verify

ZIP = sys.argv[2] if len(sys.argv) > 2 else "out/submission.best-6373.zip"


def main():
    n = int(sys.argv[1])
    out = {"task": n, "pts": 0.0, "cost": None, "ok": False, "note": ""}
    try:
        z = zipfile.ZipFile(ZIP)
        nm = f"task{n:03d}.onnx"
        if nm not in z.namelist():
            out["note"] = "absent in base zip"
        else:
            r = verify(onnx.load_model_from_string(z.read(nm)),
                       dataio.load_task(n), n)
            out["ok"] = bool(r["ok"])
            if r["ok"]:
                out["pts"] = round(r["points"], 3)
                out["cost"] = (r["memory"] or 0) + (r["params"] or 0)
            else:
                out["note"] = (f"FAIL n_fail={r['n_fail']} dq={r['disqualified']} "
                               f"{r['err'][:30]}")
    except Exception as e:  # noqa: BLE001
        out["note"] = f"{type(e).__name__}: {e}"[:60]
    os.makedirs("logs/basescore", exist_ok=True)
    json.dump(out, open(f"logs/basescore/task{n:03d}.json", "w"))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
