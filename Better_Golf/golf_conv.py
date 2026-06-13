"""Single-Conv golf: for a task whose transform is an exact per-pixel function of
a kxk neighborhood, fit one Conv(input[1,10,30,30] -> output[1,10,30,30]).

The Conv output is named 'output' (free memory); cost = params = 10*10*k*k + 10.
k=1 -> 110 (~20.3 pts), k=3 -> 910 (~18.2), k=5 -> 2510 (~17.2). Memory-free.
Fit per-output-channel by least squares (target +1 correct / -1 else) over all
pixels of all arc-gen pairs, then VERIFY EXACT with the official oracle (>0
threshold). Only accept if oracle n_fail==0 AND cost < current. This builds the
TRUE local rule (correct on all ~250 arc-gen pairs => private-safe).
"""
from __future__ import annotations
import sys, json, math, os
from pathlib import Path
import numpy as np
import onnx
from onnx import helper as oh, TensorProto as TP, numpy_helper as onh
from engine import dataio, verify

GS=[1,10,30,30]; C=10

def onehot(grid):
    g=np.array(grid,dtype=np.int64); h,w=g.shape
    t=np.zeros((C,30,30),dtype=np.float32)
    for r in range(h):
        for c in range(w):
            v=int(g[r,c])
            if 0<=v<C: t[v,r,c]=1.0
    return t,h,w

def fit_conv(task_num, k, l2=1e-3):
    ex=dataio.load_task(task_num)
    pairs=ex['train']+ex['test']+ex['arc-gen']
    # same-shape only
    for p in pairs:
        if np.array(p['input']).shape!=np.array(p['output']).shape: return None
    pad=k//2
    feats=[]; targs=[]
    for p in pairs:
        xi,h,w=onehot(p['input']); yo,_,_=onehot(p['output'])
        xp=np.zeros((C,30+2*pad,30+2*pad),dtype=np.float32); xp[:,pad:pad+30,pad:pad+30]=xi
        # only fit over the content bounding box rows/cols 0..h-1,0..w-1 PLUS a margin
        # but to be exact everywhere we fit over ALL 30x30 (padding cells must map to all<=0)
        for r in range(30):
            for c in range(30):
                patch=xp[:,r:r+k,c:c+k].reshape(-1)   # C*k*k
                feats.append(patch); targs.append(yo[:,r,c])  # C target
    X=np.array(feats); Y=np.array(targs)  # X:[N,C*k*k]  Y:[N,C]
    Xb=np.hstack([X,np.ones((X.shape[0],1),dtype=np.float32)])  # bias col
    T=Y*2-1  # +1/-1
    # ridge solve per channel: Wb = (Xb^T Xb + l2 I)^-1 Xb^T T
    A=Xb.T@Xb + l2*np.eye(Xb.shape[1],dtype=np.float32)
    Wb=np.linalg.solve(A, Xb.T@T)   # [C*k*k+1, C]
    Wb=Wb.T  # [C, C*k*k+1]
    W=Wb[:,:-1].reshape(C,C,k,k).astype(np.float32)
    b=Wb[:,-1].astype(np.float32)
    return W,b

def build_conv_model(W,b,k):
    pad=k//2
    x=oh.make_tensor_value_info("input",TP.FLOAT,GS)
    y=oh.make_tensor_value_info("output",TP.FLOAT,GS)
    wi=onh.from_array(W,"W"); bi=onh.from_array(b,"B")
    node=oh.make_node("Conv",["input","W","B"],["output"],kernel_shape=[k,k],pads=[pad]*4)
    g=oh.make_graph([node],"g",[x],[y],[wi,bi])
    return oh.make_model(g,ir_version=10,opset_imports=[oh.make_opsetid("",10)])

def golf_task(task_num, cur_cost, ks=(1,3,5)):
    task=dataio.load_task(task_num)
    best=None
    for k in ks:
        r=fit_conv(task_num,k)
        if r is None: return None  # not same-shape
        W,b=r
        m=build_conv_model(W,b,k)
        vr=verify.verify(m,task,task_num)
        if vr["ok"]:
            cost=(vr["memory"] or 0)+(vr["params"] or 0)
            if cost<cur_cost:
                return dict(k=k,cost=cost,pts=vr["points"],model=m)
            return None  # smallest k that's exact isn't cheaper -> bigger k won't be
    return None

if __name__=="__main__":
    BASE=Path(__file__).parent
    res=json.load(open(BASE/"logs"/"blend_results.json"))
    GOUT=BASE/"out"/"golf"; os.makedirs(GOUT,exist_ok=True)
    a,bb=(int(sys.argv[1]),int(sys.argv[2])) if len(sys.argv)>2 else (1,400)
    wins=0; gain=0.0
    for t in range(a,bb+1):
        k=f"{t:03d}"
        if k not in res: continue
        cur=res[k]; cur_cost=cur["memory"]+cur["params"]; cur_pts=cur["points"]
        if cur_pts>=20.3: continue   # already at/above k=1 conv ceiling
        try: r=golf_task(t,cur_cost)
        except Exception as e: r=None
        if r:
            onnx.save(r["model"],str(GOUT/f"task{t:03d}.onnx"))
            d=r["pts"]-cur_pts; wins+=1; gain+=d
            print(f"WIN task{t:03d}: k={r['k']} cost {cur_cost}->{r['cost']} pts {cur_pts:.2f}->{r['pts']:.2f} (+{d:.2f})")
    print(f"\nconv-golf: {wins} wins, +{gain:.1f} proj over base [{a}..{bb}]")
