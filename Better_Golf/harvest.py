#!/usr/bin/env python
"""Overlay out/search/* onto the base zip (re-graded, only if strictly cheaper),
write out/submission.zip, optionally submit + log LB.

Usage: harvest.py [--base out/submission.best-6373.zip] [--submit "msg"]
"""
from __future__ import annotations
import argparse, glob, io, json, math, os, subprocess, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import onnx
from engine import dataio
from engine.verify import verify

BASE_ZIP = "out/submission.best-6373.zip"
OUT_ZIP = "out/submission.zip"
BASE_LB = 6373.63


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_ZIP)
    ap.add_argument("--submit", default=None)
    a = ap.parse_args()

    with zipfile.ZipFile(a.base) as z:
        files = {n: z.read(n) for n in z.namelist()}

    overlaid, gain = [], 0.0
    for fp in sorted(glob.glob("out/search/task*.onnx")):
        n = int(os.path.basename(fp)[4:7])
        name = f"task{n:03d}.onnx"
        if name not in files:
            continue
        task = dataio.load_task(n)
        ours = onnx.load(fp)
        ro = verify(ours, task, n)
        if not ro.get("ok"):
            continue
        bc = verify(onnx.load_model_from_string(files[name]), task, n)
        if not bc.get("ok"):
            continue
        oc = ro["memory"] + ro["params"]
        bcost = bc["memory"] + bc["params"]
        if oc < bcost:
            files[name] = open(fp, "rb").read()
            gain += (25 - math.log(max(1, oc))) - (25 - math.log(max(1, bcost)))
            overlaid.append((n, bcost, oc))

    os.makedirs("out", exist_ok=True)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(files):
            z.writestr(n, files[n])
    proj = BASE_LB + gain
    print(f"overlaid {len(overlaid)} tasks | projected {proj:.2f} (+{gain:.2f}) "
          f"| {OUT_ZIP} {os.path.getsize(OUT_ZIP)}B")
    for n, b, o in sorted(overlaid, key=lambda x: (x[2] - x[1]))[:15]:
        print(f"  task{n:03d}: {b} -> {o}")

    if a.submit:
        r = subprocess.run(["kaggle", "competitions", "submit", "-c",
                            "neurogolf-2026", "-f", OUT_ZIP, "-m", a.submit],
                           capture_output=True, text=True)
        print(r.stdout, r.stderr)
        hist = []
        if os.path.exists("logs/lb_history.json"):
            try:
                hist = json.load(open("logs/lb_history.json"))
            except Exception:
                hist = []
        import datetime
        hist.append({"date": datetime.datetime.utcnow().isoformat(),
                     "msg": a.submit, "projected": round(proj, 2),
                     "n_overlaid": len(overlaid)})
        json.dump(hist, open("logs/lb_history.json", "w"), indent=2)


if __name__ == "__main__":
    main()
