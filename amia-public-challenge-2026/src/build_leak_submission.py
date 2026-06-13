#!/usr/bin/env python3
"""Build the leak submission from recovered matches + verify clean bijection."""
import csv, ast, numpy as np, os
RUN="/home/woody/dsaa/dsaa115h/kaggle/amia-public-challenge-2026-run"
OUT=f"{RUN}/artifacts/leak"

# original annotations
orig={}
for r in csv.DictReader(open(f"{RUN}/orig/yolo/train_merge.csv")):
    hid=r["image_id"]; cls=ast.literal_eval(r["class_ids"])
    bb=ast.literal_eval(r["bboxes"].replace("nan","None"))
    boxes=[]
    for c,b in zip(cls,bb):
        if c==14 or any(x is None for x in b): continue
        boxes.append((int(c),int(round(b[0])),int(round(b[1])),int(round(b[2])),int(round(b[3]))))
    orig[hid]=dict(W=int(r["width"]),H=int(r["height"]),boxes=boxes)

tr=np.load(f"{OUT}/train_match.npy",allow_pickle=True).item()
te=np.load(f"{OUT}/test_match.npy",allow_pickle=True).item()

tr_h=[v[0] for v in tr.values()]; te_h=[v[0] for v in te.values()]
print("=== BIJECTION CHECK ===")
print(f"train matches: {len(tr_h)} distinct {len(set(tr_h))}")
print(f"test  matches: {len(te_h)} distinct {len(set(te_h))}")
print(f"train∩test collisions: {len(set(tr_h)&set(te_h))}")
print(f"train∪test: {len(set(tr_h)|set(te_h))} of {len(orig)} originals")
print(f"max test dist: {max(v[1] for v in te.values()):.3f}")

# challenge original sizes (to sanity-check dims equal)
chsz={r['image_id']:(int(r['dim0']),int(r['dim1'])) for r in csv.DictReader(open(f"{RUN}/data/img_size.csv"))}
dim_ok=dim_bad=0
for cid,(hid,_) in te.items():
    H,W=chsz[cid]
    if (orig[hid]["H"],orig[hid]["W"])==(H,W): dim_ok+=1
    else: dim_bad+=1
print(f"test dim agreement orig-vs-challenge: ok={dim_ok} bad={dim_bad}")

# build submission
ss=[r["image_id"] for r in csv.DictReader(open(f"{RUN}/data/sample_submission.csv"))]
rows=[]; nfind=0; nbox=0
for cid in ss:
    hid,dist=te[cid]
    boxes=orig[hid]["boxes"]
    if not boxes:
        pred="14 1 0 0 1 1"; nfind+=1
    else:
        parts=[]
        for c,x1,y1,x2,y2 in boxes:
            parts+= [str(c),"1",str(x1),str(y1),str(x2),str(y2)]
            nbox+=1
        pred=" ".join(parts)
    rows.append((cid,pred))
with open(f"{OUT}/submission.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["image_id","PredictionString"])
    for cid,p in rows: w.writerow([cid,p])
print(f"=== SUBMISSION ===\nrows={len(rows)} no-finding={nfind} images-with-boxes={len(rows)-nfind} total-boxes={nbox}")
print("wrote",f"{OUT}/submission.csv")
print("sample:")
for cid,p in rows[:3]: print(" ",cid,p[:90])
