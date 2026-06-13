#!/usr/bin/env python3
"""Emit the public Kaggle notebook (.ipynb) for the HONEST detector solution.
Inference-only: loads HPC-trained weights from the Kaggle dataset
`fairlanderflick/amia-honest-weights` and reproduces the blended submission.
Usage: make_honest_notebook.py out.ipynb DET_THR NF_POW
"""
import json, sys
DET_THR = sys.argv[2] if len(sys.argv)>2 else "0.05"
NF_POW  = sys.argv[3] if len(sys.argv)>3 else "1.0"

def md(*l): return {"cell_type":"markdown","metadata":{},"source":[x if x.endswith("\n") else x+"\n" for x in l]}
def code(*l): return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":[x if x.endswith("\n") else x+"\n" for x in l]}

cells=[]
cells.append(md(
"# AMIA 2026 — Honest Detector (no leakage)",
"",
"A legitimate object-detection pipeline trained **only on the 8,573 train images** (the 6,427 test "
"images are never seen): **YOLO11-L @ 1024 px** on Weighted-Boxes-Fusion-merged multi-radiologist "
"labels, plus an **EfficientNet-B3 *No-finding* classifier**, blended with the standard VinBigData "
"2-class trick. Weights were trained on an NHR@FAU A100; this notebook runs **inference only**.",
"",
f"Tuned on a 15% held-out fold (PASCAL-VOC mAP@0.4): `det_thr={DET_THR}`, `nf_pow={NF_POW}`.",
"",
"> A separate notebook documents the *provenance-recovery* solution that tops the leaderboard. This "
"one is the honest model that transfers to any rules-bound competition.",
))
cells.append(code(
"import subprocess, sys",
"# Kaggle P100 (sm_60): install a torch build with sm_60 kernels, then libs --no-deps",
"subprocess.run([sys.executable,'-m','pip','install','-q','torch==2.5.1','torchvision==0.20.1',",
"                '--index-url','https://download.pytorch.org/whl/cu121'],check=True)",
"subprocess.run([sys.executable,'-m','pip','install','-q','--no-deps','ultralytics==8.4.66',",
"                'ultralytics-thop','py-cpuinfo','timm'],check=True)",
))
cells.append(code(
"import os, glob, csv",
"import numpy as np, pandas as pd, torch",
"from pathlib import Path; from PIL import Image",
"if not hasattr(np,'trapz'): np.trapz=np.trapezoid",
"def find(name): h=glob.glob(f'/kaggle/input/**/{name}',recursive=True); assert h,name; return h[0]",
"COMP=os.path.dirname(find('sample_submission.csv')); WROOT=os.path.dirname(find('best.pt'))",
"TEST=f'{COMP}/test/test'",
f"DET_THR={DET_THR}; NF_POW={NF_POW}; IMGSZ=1024; CLS_IMG=512",
"sizes={r['image_id']:(float(r['dim0']),float(r['dim1'])) for r in csv.DictReader(open(f'{COMP}/img_size.csv'))}",
"sample=pd.read_csv(f'{COMP}/sample_submission.csv')",
"print('COMP',COMP,'WEIGHTS',WROOT,'GPU',torch.cuda.is_available())",
))
cells.append(md("### Detector inference (YOLO11-L @1024, conf≥0.01, boxes → original resolution)"))
cells.append(code(
"from ultralytics import YOLO",
"det=YOLO(f'{WROOT}/best.pt')",
"items=sorted(Path(TEST).glob('*.png')); rows=[]",
"for i in range(0,len(items),64):",
"    batch=[str(p) for p in items[i:i+64]]",
"    for p,r in zip(batch,det.predict(batch,imgsz=IMGSZ,conf=0.01,iou=0.5,verbose=False,half=True)):",
"        iid=Path(p).stem; h,w=sizes.get(iid,(None,None)); iw,ih=Image.open(p).size",
"        if h is None: h,w=ih,iw",
"        if r.boxes is None: continue",
"        xy=r.boxes.xyxy.cpu().numpy(); cf=r.boxes.conf.cpu().numpy(); cl=r.boxes.cls.cpu().numpy().astype(int)",
"        for (x1,y1,x2,y2),c,k in zip(xy,cf,cl):",
"            rows.append((iid,int(k),float(c),x1*w/iw,y1*h/ih,x2*w/iw,y2*h/ih))",
"tp=pd.DataFrame(rows,columns=['image_id','class_id','conf','x_min','y_min','x_max','y_max'])",
"print('detections',len(tp),'images',tp.image_id.nunique())",
))
cells.append(md("### No-finding classifier (EfficientNet-B3 @512, hflip-TTA)"))
cells.append(code(
"import timm, torch.nn as nn, torchvision.transforms as T",
"from torch.utils.data import Dataset, DataLoader",
"cls=timm.create_model('tf_efficientnet_b3.ns_jft_in1k',pretrained=False,num_classes=1)",
"cls.load_state_dict(torch.load(f'{WROOT}/cls_best.pt',map_location='cpu')); cls=cls.cuda().eval()",
"mean=[0.485,0.456,0.406];std=[0.229,0.224,0.225]",
"tf=T.Compose([T.Resize((CLS_IMG,CLS_IMG)),T.ToTensor(),T.Normalize(mean,std)])",
"class DS(Dataset):",
"    def __init__(s,d): s.items=sorted(Path(d).glob('*.png'))",
"    def __len__(s): return len(s.items)",
"    def __getitem__(s,i): p=s.items[i]; return tf(Image.open(p).convert('RGB')), p.stem",
"dl=DataLoader(DS(TEST),batch_size=48,num_workers=4); nf={}",
"with torch.no_grad(), torch.cuda.amp.autocast():",
"    for x,ids in dl:",
"        x=x.cuda(); p=torch.sigmoid(cls(x).squeeze(1)); p2=torch.sigmoid(cls(torch.flip(x,[3])).squeeze(1)); p=(p+p2)/2",
"        for j,k in enumerate(ids): nf[k]=float(p[j])",
"print('classifier done', len(nf))",
))
cells.append(md("### Blend → submission (detector boxes + class-14 `P(no-finding)^pow` lever)"))
cells.append(code(
"g_by=dict(tuple(tp.groupby('image_id'))); out=[]",
"for iid in sample.image_id:",
"    g=g_by.get(iid); parts=[]",
"    if g is not None:",
"        for r in g[g.conf>=DET_THR].itertuples():",
"            parts+=[str(int(r.class_id)),f'{r.conf:.4f}',str(int(round(r.x_min))),str(int(round(r.y_min))),str(int(round(r.x_max))),str(int(round(r.y_max)))]",
"    parts+=['14',f'{nf.get(iid,0.5)**NF_POW:.4f}','0','0','1','1']",
"    out.append((iid,' '.join(parts)))",
"pd.DataFrame(out,columns=['image_id','PredictionString']).to_csv('submission.csv',index=False)",
"print('submission.csv written; honest blend (det_thr=%s nf_pow=%s)'%(DET_THR,NF_POW))",
))
nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
out=sys.argv[1] if len(sys.argv)>1 else "amia_honest.ipynb"
json.dump(nb,open(out,"w"),indent=1); print("wrote",out,"cells",len(cells))
