"""Overlay NN-golfed per-task ONNX onto the 6373 base zip, gated by the OFFICIAL
grader. For each out/nn/task*.onnx: re-verify with engine.verify (n_fail==0 +
measurable), compare cost to the base graph for that task; keep ours only if
STRICTLY cheaper. Write out/submission.zip. Optionally submit.

Usage: overlay_nn.py [--base out/submission.best-6373.zip] [--submit "msg"]
"""
import argparse, glob, io, json, math, os, sys, zipfile
sys.path.insert(0, ".")
import onnx
from engine.verify import verify
from engine import dataio

BASE_DEFAULT = "out/submission.best-6373.zip"
OUT_ZIP = "out/submission.zip"


def base_cost(task_num, base_bytes):
    """Cost of the base graph for this task (memory+params) via official grader."""
    name = f"task{task_num:03d}.onnx"
    with zipfile.ZipFile(io.BytesIO(base_bytes)) as z:
        if name not in z.namelist():
            return None, None
        m = onnx.load_model_from_string(z.read(name))
    task = dataio.load_task(task_num)
    r = verify(m, task, task_num)
    if not r.get("ok"):
        return None, r
    return r["memory"] + r["params"], r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_DEFAULT)
    ap.add_argument("--submit", default=None, help="submit with this message")
    ap.add_argument("--reverify-base", action="store_true",
                    help="re-grade base graph per overlaid task (slow, safe)")
    args = ap.parse_args()

    base_bytes = open(args.base, "rb").read()
    with zipfile.ZipFile(io.BytesIO(base_bytes)) as z:
        base_names = set(z.namelist())
        base_files = {n: z.read(n) for n in base_names}

    cand = sorted(glob.glob("out/nn/task*.onnx"))
    cost = json.load(open("logs/vyank_costmap.json"))
    overlaid, skipped = [], []
    for fp in cand:
        tn = int(os.path.basename(fp)[4:7])
        m = onnx.load(fp)
        task = dataio.load_task(tn)
        r = verify(m, task, tn)
        if not r.get("ok"):
            skipped.append((tn, "ours not ok: " + r.get("err", "")[:30]))
            continue
        ours = r["memory"] + r["params"]
        if args.reverify_base:
            bc, _ = base_cost(tn, base_bytes)
        else:
            bc = cost.get(str(tn))
        if bc is None or ours < bc:
            base_files[f"task{tn:03d}.onnx"] = open(fp, "rb").read()
            overlaid.append((tn, bc, ours))
        else:
            skipped.append((tn, f"not cheaper ({ours} >= base {bc})"))

    os.makedirs("out", exist_ok=True)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(base_files):
            z.writestr(n, base_files[n])

    gain = sum(max(1, 25 - math.log(max(1, b))) * 0 for _, b, _ in overlaid)
    gain = 0.0
    for tn, b, ours in overlaid:
        if b:
            gain += (25 - math.log(max(1, ours))) - (25 - math.log(max(1, b)))
    print(f"overlaid {len(overlaid)} tasks, projected gain +{gain:.2f} "
          f"=> ~{6373.63 + gain:.1f}. skipped {len(skipped)}.")
    for tn, b, ours in sorted(overlaid, key=lambda x: x[2] - (x[1] or 0)):
        print(f"  task{tn:03d}: base {b} -> ours {ours}")
    print(f"wrote {OUT_ZIP} ({os.path.getsize(OUT_ZIP)} bytes)")

    if args.submit:
        import subprocess
        out = subprocess.run(["kaggle", "competitions", "submit", "-c",
                              "neurogolf-2026", "-f", OUT_ZIP, "-m", args.submit],
                             capture_output=True, text=True)
        print(out.stdout, out.stderr)


if __name__ == "__main__":
    main()
