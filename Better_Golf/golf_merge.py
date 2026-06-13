"""Merge golf2 per-task wins onto the current base submission.zip (fast, json-based).

The array run already oracle-verified each win (cost+points in out/golf2/taskNNN.json,
winning graph in out/golf2/taskNNN.onnx). We trust those, assemble the zip, and
compute totals from the recorded verified costs. Writes out/submission.golf.zip,
logs/vyank_costmap.json (authoritative base cost map), and prints the top wins.

Usage: python golf_merge.py
"""
from __future__ import annotations
import json, zipfile, re, os, math
from pathlib import Path

BASE=Path(__file__).parent
GOUT=BASE/"out"/"golf2"
SUBZIP=BASE/"out"/"submission.zip"
OUTZIP=BASE/"out"/"submission.golf.zip"
def pts(c): return max(1.0,25-math.log(max(1,c)))

basez={}
with zipfile.ZipFile(SUBZIP) as zf:
    for nm in zf.namelist():
        mm=re.match(r"task(\d{3})\.onnx$",os.path.basename(nm))
        if mm: basez[int(mm.group(1))]=zf.read(nm)

recs={}
for jf in sorted(GOUT.glob("task*.json")):
    r=json.load(open(jf)); recs[r["task"]]=r

base_total=new_total=0.0; wins=[]; final={}; costmap={}
for t in range(1,401):
    if t not in basez: continue
    final[t]=basez[t]
    r=recs.get(t)
    bc = r["base_cost"] if (r and r.get("base_cost")) else None
    if bc is None:
        # no record (e.g. missing task) -> keep base, unknown cost; skip from totals
        continue
    costmap[t]=bc
    base_total+=pts(bc); contrib=pts(bc)
    if r.get("win"):
        op=GOUT/f"task{t:03d}.onnx"
        w=r["win"]
        if op.exists() and w["cost"]<bc:
            final[t]=open(op,'rb').read()
            wins.append((t,bc,w["cost"],round(w["pts"]-pts(bc),3),w["gen"]))
            contrib=w["pts"]
    new_total+=contrib

with zipfile.ZipFile(OUTZIP,"w",zipfile.ZIP_DEFLATED) as zf:
    for t in sorted(final): zf.writestr(f"task{t:03d}.onnx",final[t])
json.dump(costmap,open(BASE/"logs"/"vyank_costmap.json","w"),indent=0)
print(f"tasks={len(final)} replaced={len(wins)}  base_total={base_total:.2f} -> golf_total={new_total:.2f} (+{new_total-base_total:.2f})")
print(f"-> {OUTZIP} ({OUTZIP.stat().st_size/1024:.0f} KB); costmap -> logs/vyank_costmap.json ({len(costmap)} tasks)")
for t,bc,nc,d,g in sorted(wins,key=lambda x:-x[3])[:15]:
    print(f"  task{t:03d}: {g} cost {bc}->{nc} (+{d})")
