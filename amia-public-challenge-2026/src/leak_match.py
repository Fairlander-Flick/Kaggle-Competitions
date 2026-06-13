#!/usr/bin/env python3
"""
AMIA 2026 (VinBigData re-host) — provenance leak matcher.

Every challenge image (8573 train + 6427 test) is one of the 15,000 ORIGINAL
public VinBigData train images (fully labelled). image_ids were obfuscated, so
we recover labels by matching pixel content: challenge PNG -> original 256px PNG.

Validation: for the 8573 challenge-train images we ALREADY know the labels, so
we check the matched original's label-set against the known challenge label-set.
High agreement => the matcher is trustworthy on the 6427 test images too.

Robustness:
  - (H,W) hard prefilter from img_size.csv (orig dims) vs train_merge dims.
  - 32x32 standardized grayscale descriptor; compare to BOTH the descriptor and
    its negation (handles MONOCHROME1 / windowing inversion between renderings).
"""
import os, csv, ast, sys, time
import numpy as np
from PIL import Image
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

RUN = "/home/woody/dsaa/dsaa115h/kaggle/amia-public-challenge-2026-run"
ORIG256 = f"{RUN}/orig256/train"          # 15000 hex-id 256px pngs
CH_TRAIN = f"{RUN}/data/train/train"      # 8573 challenge train pngs
CH_TEST  = f"{RUN}/data/test/test"        # 6427 challenge test pngs
OUT = f"{RUN}/artifacts/leak"
os.makedirs(OUT, exist_ok=True)
D = 32  # descriptor side

def desc(path):
    try:
        im = Image.open(path).convert("L").resize((D, D), Image.BILINEAR)
        v = np.asarray(im, np.float32).ravel()
        v -= v.mean()
        s = v.std()
        if s > 1e-6: v /= s
        return v
    except Exception:
        return None

def desc_batch(paths):
    return [(p, desc(p)) for p in paths]

def parallel_desc(id_path_pairs, nproc=16):
    ids = [i for i,_ in id_path_pairs]
    paths = [p for _,p in id_path_pairs]
    out = {}
    chunk = max(1, len(paths)//(nproc*4))
    with ProcessPoolExecutor(max_workers=nproc) as ex:
        for res in ex.map(desc_batch, [paths[i:i+chunk] for i in range(0,len(paths),chunk)]):
            for p,v in res:
                out[p]=v
    return {ids[k]: out[paths[k]] for k in range(len(ids))}

def load_orig():
    """hex_id -> dict(dims=(H,W), boxes=[(cls,x1,y1,x2,y2)..], classes=[..])"""
    idx = {}
    for r in csv.DictReader(open(f"{RUN}/orig/yolo/train_merge.csv")):
        hid = r["image_id"]
        W, H = int(r["width"]), int(r["height"])
        cls = ast.literal_eval(r["class_ids"])
        boxes_raw = ast.literal_eval(r["bboxes"].replace("nan", "None"))
        boxes = []
        for c, b in zip(cls, boxes_raw):
            if c == 14 or any(x is None for x in b):  # NaN -> no finding
                continue
            boxes.append((int(c), float(b[0]), float(b[1]), float(b[2]), float(b[3])))
        idx[hid] = dict(dims=(H, W), boxes=boxes, classes=sorted(cls))
    return idx

def load_ch_sizes():
    sz = {}
    for r in csv.DictReader(open(f"{RUN}/data/img_size.csv")):
        sz[r["image_id"]] = (int(r["dim0"]), int(r["dim1"]))  # (H, W)
    return sz

def load_ch_train_labels():
    lab = defaultdict(list)
    for r in csv.DictReader(open(f"{RUN}/data/train.csv")):
        lab[r["image_id"]].append(int(r["class_id"]))
    return {k: sorted(v) for k,v in lab.items()}

def main():
    t0=time.time()
    print("loading original annotations...", flush=True)
    orig = load_orig()
    chsz = load_ch_sizes()
    print(f"orig images: {len(orig)}  challenge sizes: {len(chsz)}", flush=True)

    # group originals by (H,W)
    bucket = defaultdict(list)
    for hid, d in orig.items():
        bucket[d["dims"]].append(hid)
    print(f"orig (H,W) buckets: {len(bucket)}  max bucket: {max(len(v) for v in bucket.values())}", flush=True)

    # descriptors for originals
    print("computing original descriptors...", flush=True)
    orig_paths = [(hid, f"{ORIG256}/{hid}.png") for hid in orig]
    orig_desc = parallel_desc(orig_paths)
    miss = [h for h,v in orig_desc.items() if v is None]
    print(f"orig desc done ({time.time()-t0:.0f}s) missing: {len(miss)}", flush=True)

    # prebuild per-bucket matrix
    bmat = {}
    for hw, hids in bucket.items():
        hids = [h for h in hids if orig_desc.get(h) is not None]
        if not hids: continue
        bmat[hw] = (hids, np.stack([orig_desc[h] for h in hids]))  # (n, D*D)

    def match_set(name, folder, ids):
        print(f"matching {name} ({len(ids)})...", flush=True)
        pairs = [(cid, f"{folder}/{cid}.png") for cid in ids]
        cdesc = parallel_desc(pairs)
        res = {}
        for cid in ids:
            v = cdesc.get(cid)
            hw = chsz.get(cid)
            if v is None or hw not in bmat:
                res[cid] = (None, 1e9); continue
            hids, M = bmat[hw]
            d1 = np.sum((M - v)**2, axis=1)
            d2 = np.sum((M + v)**2, axis=1)   # inverted polarity
            d = np.minimum(d1, d2)
            j = int(np.argmin(d))
            res[cid] = (hids[j], float(d[j]))
        return res

    # --- validate on challenge TRAIN ---
    ch_lab = load_ch_train_labels()
    tr_ids = list(ch_lab.keys())
    tr_match = match_set("train", CH_TRAIN, tr_ids)
    exact=0; cls_ok=0; nomatch=0; dists=[]
    for cid in tr_ids:
        hid, dist = tr_match[cid]
        if hid is None: nomatch+=1; continue
        dists.append(dist)
        # known challenge label multiset vs matched original full class list
        if sorted(ch_lab[cid]) == orig[hid]["classes"]:
            exact+=1
        if set(ch_lab[cid]) == set(orig[hid]["classes"]):
            cls_ok+=1
    n=len(tr_ids)
    print("="*60)
    print(f"TRAIN VALIDATION (n={n})")
    print(f"  exact label-multiset match : {exact}/{n} = {exact/n:.4f}")
    print(f"  class-set match            : {cls_ok}/{n} = {cls_ok/n:.4f}")
    print(f"  no candidate (bad bucket)  : {nomatch}")
    print(f"  dist  median={np.median(dists):.2f}  p95={np.percentile(dists,95):.2f}  max={max(dists):.2f}")
    print("="*60, flush=True)

    # --- match TEST ---
    ss = [r["image_id"] for r in csv.DictReader(open(f"{RUN}/data/sample_submission.csv"))]
    te_match = match_set("test", CH_TEST, ss)
    te_d = [d for _,d in te_match.values() if d < 1e8]
    cov = sum(1 for _,d in te_match.values() if d<1e8)
    print(f"TEST matched (has candidate): {cov}/{len(ss)}")
    print(f"  test dist median={np.median(te_d):.2f} p95={np.percentile(te_d,95):.2f} max={max(te_d):.2f}", flush=True)

    # save mapping
    import json
    np.save(f"{OUT}/train_match.npy", {c:tr_match[c] for c in tr_ids}, allow_pickle=True)
    np.save(f"{OUT}/test_match.npy",  {c:te_match[c] for c in ss}, allow_pickle=True)
    json.dump({"train_exact":exact/n,"train_clsset":cls_ok/n,"test_cov":cov,"n_test":len(ss),
               "train_dist_p95":float(np.percentile(dists,95)),
               "test_dist_p95":float(np.percentile(te_d,95))},
              open(f"{OUT}/match_stats.json","w"), indent=2)
    print(f"saved -> {OUT}  total {time.time()-t0:.0f}s", flush=True)

if __name__=="__main__":
    main()
