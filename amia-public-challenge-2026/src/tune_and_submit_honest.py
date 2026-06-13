"""Offline PASCAL-VOC mAP@0.4 tuning of the honest blend on the held-out val fold,
then write the tuned test submission. Burns no Kaggle submissions to tune.

Uses artifacts/honest/{val_preds,val_nf,val_labels,test_preds,test_nf}.csv +
data/train.csv (raw GT) + data/img_size.csv. Grid-searches DET_THR x NF_POW.
"""
import numpy as np, pandas as pd, csv
from pathlib import Path
from collections import defaultdict
RUN=Path("/home/woody/dsaa/dsaa115h/kaggle/amia-public-challenge-2026-run")
OUT=RUN/"artifacts"/"honest"; DATA=RUN/"data"
NC=14; IOU_THR=0.4

def voc_ap(rec, prec):  # VOC2010 (all-points)
    mrec=np.concatenate(([0.],rec,[1.])); mpre=np.concatenate(([0.],prec,[0.]))
    for i in range(len(mpre)-1,0,-1): mpre[i-1]=max(mpre[i-1],mpre[i])
    i=np.where(mrec[1:]!=mrec[:-1])[0]
    return float(np.sum((mrec[i+1]-mrec[i])*mpre[i+1]))

def iou(a,B):
    ix1=np.maximum(a[0],B[:,0]); iy1=np.maximum(a[1],B[:,1])
    ix2=np.minimum(a[2],B[:,2]); iy2=np.minimum(a[3],B[:,3])
    iw=np.clip(ix2-ix1,0,None); ih=np.clip(iy2-iy1,0,None); inter=iw*ih
    aa=(a[2]-a[0])*(a[3]-a[1]); ab=(B[:,2]-B[:,0])*(B[:,3]-B[:,1])
    return inter/(aa+ab-inter+1e-9)

def map40(gt, preds, ids):
    """gt[id][cls]=list[box]; preds[id]=list[(cls,conf,box)] ; mean AP over classes 0..14."""
    aps=[]
    for c in range(NC+1):
        npos=sum(len(gt.get(i,{}).get(c,[])) for i in ids)
        dets=[]
        for i in ids:
            for (cl,cf,bx) in preds.get(i,[]):
                if cl==c: dets.append((cf,i,bx))
        if npos==0:
            continue
        dets.sort(key=lambda x:-x[0])
        tp=np.zeros(len(dets)); fp=np.zeros(len(dets)); used=defaultdict(set)
        for k,(cf,i,bx) in enumerate(dets):
            G=gt.get(i,{}).get(c,[])
            if not G: fp[k]=1; continue
            B=np.array(G,float); o=iou(np.array(bx,float),B); j=int(np.argmax(o))
            if o[j]>=IOU_THR and j not in used[i]: tp[k]=1; used[i].add(j)
            else: fp[k]=1
        tpc=np.cumsum(tp); fpc=np.cumsum(fp)
        rec=tpc/(npos+1e-9); prec=tpc/(tpc+fpc+1e-9)
        aps.append(voc_ap(rec,prec))
    return float(np.mean(aps)) if aps else 0.0

# GT for val from raw train.csv
sizes={r['image_id']:(float(r['dim0']),float(r['dim1'])) for r in csv.DictReader(open(DATA/"img_size.csv"))}
tr=pd.read_csv(DATA/"train.csv")
val_lab=pd.read_csv(OUT/"val_labels.csv"); val_ids=list(val_lab.image_id)
gt=defaultdict(lambda:defaultdict(list))
sub=tr[tr.image_id.isin(set(val_ids))]
for r in sub.itertuples():
    if r.class_id==14 or pd.isna(r.x_min): gt[r.image_id][14].append([0,0,1,1])
    else: gt[r.image_id][int(r.class_id)].append([r.x_min,r.y_min,r.x_max,r.y_max])

vp=pd.read_csv(OUT/"val_preds.csv"); vnf=dict(zip(*[pd.read_csv(OUT/"val_nf.csv")[c] for c in ["image_id","p_nofinding"]]))
vp_by=defaultdict(list)
for r in vp.itertuples(): vp_by[r.image_id].append((int(r.class_id),float(r.conf),[r.x_min,r.y_min,r.x_max,r.y_max]))

def build_preds(by,nf,ids,det_thr,nf_pow):
    P={}
    for i in ids:
        lst=[(c,cf,bx) for (c,cf,bx) in by.get(i,[]) if cf>=det_thr]
        lst.append((14, float(nf.get(i,0.5))**nf_pow, [0,0,1,1]))
        P[i]=lst
    return P

best=(-1,None)
for det_thr in [0.001,0.01,0.05,0.1,0.15]:
    for nf_pow in [0.5,1.0,1.5,2.0]:
        P=build_preds(vp_by,vnf,val_ids,det_thr,nf_pow)
        m=map40(gt,P,val_ids)
        if m>best[0]: best=(m,(det_thr,nf_pow))
        print(f"det_thr={det_thr:<5} nf_pow={nf_pow:<4} val_mAP@0.4={m:.4f}")
print("BEST val mAP@0.4 =",round(best[0],4),"params",best[1])

# write tuned test submission
det_thr,nf_pow=best[1]
tp=pd.read_csv(OUT/"test_preds.csv"); tnf=dict(zip(*[pd.read_csv(OUT/"test_nf.csv")[c] for c in ["image_id","p_nofinding"]]))
tby=defaultdict(list)
for r in tp.itertuples(): tby[r.image_id].append((int(r.class_id),float(r.conf),[int(round(r.x_min)),int(round(r.y_min)),int(round(r.x_max)),int(round(r.y_max))]))
ss=[r['image_id'] for r in csv.DictReader(open(DATA/"sample_submission.csv"))]
rows=[]
for i in ss:
    parts=[]
    for (c,cf,bx) in [x for x in tby.get(i,[]) if x[1]>=det_thr]:
        parts+=[str(c),f"{cf:.4f}",str(bx[0]),str(bx[1]),str(bx[2]),str(bx[3])]
    parts+=["14",f"{float(tnf.get(i,0.5))**nf_pow:.4f}","0","0","1","1"]
    rows.append((i," ".join(parts)))
pd.DataFrame(rows,columns=["image_id","PredictionString"]).to_csv(OUT/"submission_tuned.csv",index=False)
open(OUT/"tune_report.txt","w").write(f"best val mAP@0.4={best[0]:.4f} det_thr={det_thr} nf_pow={nf_pow}\n")
print("wrote",OUT/"submission_tuned.csv")
