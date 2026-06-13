"""AMIA honest pipeline on HPC A100 (no leakage): WBF-fused YOLO11 detector +
No-finding classifier, blended into a submission. Adapted from the proven Kaggle
kernels (amia-train-yolo / amia-train-cls) for the conda `kaggle` env + $TMPDIR.

Trains on the 8,573 challenge-train images ONLY (the 6,427 'test' are held out).
Outputs to artifacts/honest/: best.pt, cls_best.pt, val_preds.csv, test_preds.csv,
val_nf.csv, test_nf.csv, val_labels.csv, submission.csv, and a tuned-threshold report.
"""
import os, sys, time, shutil
from pathlib import Path
import numpy as np, pandas as pd
t0=time.time()
def log(*a): print(f"[{time.time()-t0:7.1f}s]",*a); sys.stdout.flush()

RUN   = Path("/home/woody/dsaa/dsaa115h/kaggle/amia-public-challenge-2026-run")
DATA_SRC = Path(os.environ.get("DATA_DIR", RUN/"data"))   # staged $TMPDIR or $WORK/data
TRAIN_IMG = DATA_SRC/"train"/"train"; TEST_IMG = DATA_SRC/"test"/"test"
OUT = RUN/"artifacts"/"honest"; OUT.mkdir(parents=True, exist_ok=True)
WORK = Path(os.environ.get("JOB_TMP", "/tmp"))/"honest"; WORK.mkdir(parents=True, exist_ok=True)

IMGSZ=int(os.environ.get("IMGSZ",1024)); EPOCHS=int(os.environ.get("EPOCHS",60))
BATCH=int(os.environ.get("BATCH",16)); MODEL=os.environ.get("MODEL","yolo11l.pt")
WBF_IOU=0.45; VAL_FRAC=0.15; NC=14; SEED=42
CLS_ARCH=os.environ.get("CLS_ARCH","tf_efficientnet_b3.ns_jft_in1k")
CLS_IMG=int(os.environ.get("CLS_IMG",512)); CLS_EP=int(os.environ.get("CLS_EP",12)); CLS_BS=int(os.environ.get("CLS_BS",48))

import torch
if not hasattr(np,"trapz"): np.trapz=np.trapezoid
log("torch",torch.__version__,"cuda",torch.cuda.is_available(),"dev",torch.cuda.get_device_name(0) if torch.cuda.is_available() else "-")
assert torch.cuda.is_available()

train=pd.read_csv(DATA_SRC/"train.csv"); sizes=pd.read_csv(DATA_SRC/"img_size.csv"); sample=pd.read_csv(DATA_SRC/"sample_submission.csv")
size_lookup={r.image_id:(float(r.dim0),float(r.dim1)) for r in sizes.itertuples()}  # (h,w)
all_ids=sorted(p.stem for p in TRAIN_IMG.glob("*.png"))
rng=np.random.RandomState(SEED); ids=all_ids[:]; rng.shuffle(ids)
n_val=int(len(ids)*VAL_FRAC); val_ids=set(ids[:n_val]); train_ids=set(ids[n_val:])
log(f"images total={len(all_ids)} train={len(train_ids)} val={len(val_ids)}")
(OUT/"val_ids.txt").write_text("\n".join(sorted(val_ids)))

# ---------------- WBF labels ----------------
from ensemble_boxes import weighted_boxes_fusion
fnd=train[train.class_id!=14].dropna(subset=["x_min","y_min","x_max","y_max"]).copy()
by_img={iid:g for iid,g in fnd.groupby("image_id")}
def fused(iid):
    if iid not in by_img: return []
    g=by_img[iid]; h,w=size_lookup[iid]; boxes=[];scores=[];labels=[]
    for r in g.itertuples():
        x1=max(0,min(r.x_min,w-1))/w; y1=max(0,min(r.y_min,h-1))/h
        x2=max(0,min(r.x_max,w-1))/w; y2=max(0,min(r.y_max,h-1))/h
        if x2<=x1 or y2<=y1: continue
        boxes.append([x1,y1,x2,y2]); scores.append(1.0); labels.append(int(r.class_id))
    if not boxes: return []
    fb,fs,fl=weighted_boxes_fusion([boxes],[scores],[labels],iou_thr=WBF_IOU,skip_box_thr=0.0)
    out=[]
    for (x1,y1,x2,y2),c in zip(fb,fl):
        xc=(x1+x2)/2;yc=(y1+y2)/2;bw=x2-x1;bh=y2-y1
        if bw>0 and bh>0: out.append((int(c),xc,yc,bw,bh))
    return out
YD=WORK/"yolo"
for split,sids in [("train",train_ids),("val",val_ids)]:
    (YD/"images"/split).mkdir(parents=True,exist_ok=True); (YD/"labels"/split).mkdir(parents=True,exist_ok=True)
    for iid in sids:
        dst=YD/"images"/split/f"{iid}.png"
        if not dst.exists():
            try: os.symlink(TRAIN_IMG/f"{iid}.png",dst)
            except FileExistsError: pass
        (YD/"labels"/split/f"{iid}.txt").write_text("\n".join(f"{c} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}" for (c,xc,yc,bw,bh) in fused(iid)))
(YD/"data.yaml").write_text(f"path: {YD}\ntrain: images/train\nval: images/val\nnames:\n"+"\n".join(f"  {i}: c{i}" for i in range(NC))+"\n")
log("WBF dataset built")

# ---------------- train detector ----------------
from ultralytics import RTDETR, YOLO
Net=RTDETR if "detr" in MODEL else YOLO
model=Net(MODEL)
log(f"detector train {MODEL} imgsz={IMGSZ} ep={EPOCHS} batch={BATCH}")
model.train(data=str(YD/"data.yaml"),epochs=EPOCHS,imgsz=IMGSZ,batch=BATCH,
            project=str(WORK/"runs"),name="det",exist_ok=True,patience=15,workers=8,
            device=0,cache=False,plots=False,seed=SEED,half=True)
best=WORK/"runs"/"det"/"weights"/"best.pt"; shutil.copy2(best,OUT/"best.pt"); log("detector done")

from PIL import Image
infer=Net(str(best))
def infer_dir(items):
    rows=[];B=64
    for i in range(0,len(items),B):
        batch=[str(p) for p in items[i:i+B] if p.exists()]
        if not batch: continue
        res=infer.predict(batch,imgsz=IMGSZ,conf=0.01,iou=0.5,verbose=False,half=True)
        for p,r in zip(batch,res):
            iid=Path(p).stem; h,w=size_lookup.get(iid,(None,None)); iw,ih=Image.open(p).size
            if h is None: h,w=ih,iw
            if r.boxes is None: continue
            xy=r.boxes.xyxy.cpu().numpy();cf=r.boxes.conf.cpu().numpy();cl=r.boxes.cls.cpu().numpy().astype(int)
            for (x1,y1,x2,y2),c,k in zip(xy,cf,cl):
                rows.append((iid,int(k),float(c),x1*w/iw,y1*h/ih,x2*w/iw,y2*h/ih))
        if i%2048==0: log(f"  infer {i}/{len(items)}")
    return pd.DataFrame(rows,columns=["image_id","class_id","conf","x_min","y_min","x_max","y_max"])
vp=infer_dir([TRAIN_IMG/f"{i}.png" for i in sorted(val_ids)]); vp.to_csv(OUT/"val_preds.csv",index=False); log(f"val_preds={len(vp)}")
tp=infer_dir(sorted(TEST_IMG.glob("*.png"))); tp.to_csv(OUT/"test_preds.csv",index=False); log(f"test_preds={len(tp)} imgs={tp.image_id.nunique()}")

# ---------------- no-finding classifier ----------------
import torch.nn as nn, timm, torchvision.transforms as T
from torch.utils.data import Dataset, DataLoader
nofind=train.groupby("image_id").class_id.apply(lambda s:int(set(s)=={14}))
y={i:int(nofind.get(i,1)) for i in all_ids}
tr_ids=[i for i in ids[n_val:]]; va_ids=[i for i in ids[:n_val]]
mean=[0.485,0.456,0.406];std=[0.229,0.224,0.225]
aug=T.Compose([T.Resize((CLS_IMG,CLS_IMG)),T.RandomHorizontalFlip(),T.RandomAffine(7,(0.05,0.05),(0.95,1.05)),T.ColorJitter(0.15,0.15),T.ToTensor(),T.Normalize(mean,std)])
noaug=T.Compose([T.Resize((CLS_IMG,CLS_IMG)),T.ToTensor(),T.Normalize(mean,std)])
class DS(Dataset):
    def __init__(s,ii,d,tf,lab=True):s.ii=list(ii);s.d=d;s.tf=tf;s.lab=lab
    def __len__(s):return len(s.ii)
    def __getitem__(s,i):
        iid=s.ii[i];x=s.tf(Image.open(s.d/f"{iid}.png").convert("RGB"))
        return (x,torch.tensor(y[iid],dtype=torch.float32)) if s.lab else (x,iid)
trdl=DataLoader(DS(tr_ids,TRAIN_IMG,aug),batch_size=CLS_BS,shuffle=True,num_workers=8,pin_memory=True,drop_last=True)
vadl=DataLoader(DS(va_ids,TRAIN_IMG,noaug),batch_size=CLS_BS,shuffle=False,num_workers=8,pin_memory=True)
cls=timm.create_model(CLS_ARCH,pretrained=True,num_classes=1).cuda()
opt=torch.optim.AdamW(cls.parameters(),lr=3e-4,weight_decay=1e-4); sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=CLS_EP)
scaler=torch.cuda.amp.GradScaler(); lossf=nn.BCEWithLogitsLoss()
def auc(yt,yp):
    yt=np.asarray(yt);yp=np.asarray(yp);o=np.argsort(yp);yt=yt[o];r=np.arange(1,len(yt)+1);npos=yt.sum();nneg=len(yt)-npos
    return 0.5 if npos==0 or nneg==0 else float((r[yt==1].sum()-npos*(npos+1)/2)/(npos*nneg))
best_auc=0;best_state=None
for ep in range(CLS_EP):
    cls.train()
    for x,t in trdl:
        x=x.cuda(non_blocking=True);t=t.cuda(non_blocking=True);opt.zero_grad()
        with torch.cuda.amp.autocast(): loss=lossf(cls(x).squeeze(1),t)
        scaler.scale(loss).backward();scaler.step(opt);scaler.update()
    sched.step();cls.eval();ys=[];ps=[]
    with torch.no_grad(),torch.cuda.amp.autocast():
        for x,t in vadl:
            p=torch.sigmoid(cls(x.cuda()).squeeze(1)).float().cpu().numpy();ps+=p.tolist();ys+=t.numpy().tolist()
    a=auc(ys,ps);log(f"cls ep{ep} val_auc={a:.4f}")
    if a>best_auc:best_auc=a;best_state={k:v.cpu().clone() for k,v in cls.state_dict().items()}
log(f"cls best auc={best_auc:.4f}");cls.load_state_dict(best_state);torch.save(best_state,OUT/"cls_best.pt")
@torch.no_grad()
def predict_nf(ii,d):
    cls.eval();dl=DataLoader(DS(ii,d,noaug,lab=False),batch_size=CLS_BS,shuffle=False,num_workers=8);out={}
    with torch.cuda.amp.autocast():
        for x,iid in dl:
            x=x.cuda();p=torch.sigmoid(cls(x).squeeze(1));p2=torch.sigmoid(cls(torch.flip(x,dims=[3])).squeeze(1));p=(p+p2)/2
            for j,k in enumerate(iid):out[k]=float(p[j])
    return out
vnf=predict_nf(va_ids,TRAIN_IMG);pd.DataFrame({"image_id":list(vnf),"p_nofinding":list(vnf.values())}).to_csv(OUT/"val_nf.csv",index=False)
test_ids=[p.stem for p in TEST_IMG.glob("*.png")];tnf=predict_nf(test_ids,TEST_IMG)
pd.DataFrame({"image_id":list(tnf),"p_nofinding":list(tnf.values())}).to_csv(OUT/"test_nf.csv",index=False)
pd.DataFrame({"image_id":va_ids,"y_nofinding":[y[i] for i in va_ids]}).to_csv(OUT/"val_labels.csv",index=False)
log(f"classifier auc={best_auc:.4f} done")

# ---------------- blend -> submission (standard VinBigData 2-class trick) ----------------
DET_THR=float(os.environ.get("DET_THR",0.05)); NF_POW=float(os.environ.get("NF_POW",1.0))
g_by=dict(tuple(tp.groupby("image_id")))
rows=[]
for iid in sample.image_id:
    g=g_by.get(iid); pnf=tnf.get(iid,0.5)
    parts=[]
    if g is not None:
        gg=g[g.conf>=DET_THR]
        for r in gg.itertuples():
            parts+= [str(int(r.class_id)),f"{r.conf:.4f}",str(int(round(r.x_min))),str(int(round(r.y_min))),str(int(round(r.x_max))),str(int(round(r.y_max)))]
    # class-14 lever: confidence = p_nofinding^pow
    parts+=["14",f"{pnf**NF_POW:.4f}","0","0","1","1"]
    rows.append((iid," ".join(parts)))
pd.DataFrame(rows,columns=["image_id","PredictionString"]).to_csv(OUT/"submission.csv",index=False)
log(f"submission written -> {OUT/'submission.csv'} (det_thr={DET_THR} nf_pow={NF_POW}) DONE total={time.time()-t0:.0f}s")
