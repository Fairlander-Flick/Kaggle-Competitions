"""Parallel per-task ONNX golf engine.

For one task, generate MANY candidate ONNX graphs from a library of generators,
official-verify each (engine.verify == grader), and keep the CHEAPEST valid one
that beats the current base cost. Designed to run massively parallel as a SLURM
array (one task-chunk per array element); results merged later.

Generators must emit only grader-faithful op vocabularies and build the TRUE rule
(correct on ALL arc-gen pairs => private-safe). Acceptance is the official oracle,
never a heuristic. Add new generators (incl. subagent-built family solvers) to
GENERATORS; the driver picks up everything.

Usage:
  python golf2.py <task_a> <task_b>     # golf tasks a..b, write out/golf2/taskNNN.{onnx,json}
"""
from __future__ import annotations
import sys, json, math, os, itertools
from pathlib import Path
import numpy as np
import onnx
from onnx import helper as oh, TensorProto as TP, numpy_helper as onh
from engine import dataio, verify

BASE = Path(__file__).parent
GS=[1,10,30,30]; C=10
GOUT = BASE/"out"/"golf2"

# ---- helpers ----
def onehot(grid):
    g=np.array(grid,dtype=np.int64); h,w=g.shape
    t=np.zeros((C,30,30),dtype=np.float32)
    for r in range(h):
        for c in range(w):
            v=int(g[r,c])
            if 0<=v<C: t[v,r,c]=1.0
    return t,h,w

def model_from(nodes, inits, opset=10):
    x=oh.make_tensor_value_info("input",TP.FLOAT,GS)
    y=oh.make_tensor_value_info("output",TP.FLOAT,GS)
    g=oh.make_graph(nodes,"g",[x],[y],inits)
    return oh.make_model(g,ir_version=10,opset_imports=[oh.make_opsetid("",opset)])

def cost_of(vr): return (vr["memory"] or 0)+(vr["params"] or 0)

# ---- generators: each yields (label, onnx.ModelProto) ----
def gen_base(task_num, base_bytes):
    if base_bytes is not None:
        try: yield ("base", onnx.load_from_string(base_bytes))
        except Exception: pass

def _pairs(task_num):
    ex=dataio.load_task(task_num); return ex['train']+ex['test']+ex['arc-gen']

def gen_conv(task_num, base_bytes):
    pairs=_pairs(task_num)
    if any(np.array(p['input']).shape!=np.array(p['output']).shape for p in pairs): return
    for k in (1,3):
        pad=k//2; feats=[]; targs=[]
        for p in pairs:
            xi,h,w=onehot(p['input']); yo,_,_=onehot(p['output'])
            xp=np.zeros((C,30+2*pad,30+2*pad),dtype=np.float32); xp[:,pad:pad+30,pad:pad+30]=xi
            for r in range(30):
                for c in range(30):
                    feats.append(xp[:,r:r+k,c:c+k].reshape(-1)); targs.append(yo[:,r,c])
        X=np.array(feats); Y=np.array(targs); Xb=np.hstack([X,np.ones((X.shape[0],1),np.float32)])
        T=Y*2-1
        try: Wb=np.linalg.solve(Xb.T@Xb+1e-3*np.eye(Xb.shape[1],dtype=np.float32), Xb.T@T).T
        except Exception: continue
        W=Wb[:,:-1].reshape(C,C,k,k).astype(np.float32); b=Wb[:,-1].astype(np.float32)
        node=oh.make_node("Conv",["input","W","B"],["output"],kernel_shape=[k,k],pads=[pad]*4)
        yield (f"conv{k}", model_from([node],[onh.from_array(W,"W"),onh.from_array(b,"B")]))

def gen_rewrite(task_num, base_bytes):
    """Lossless rewrites of the base graph: onnxoptimizer passes + onnxsim const-fold.
    Each result is oracle-gated downstream; only accepted if cost< and n_fail==0."""
    if base_bytes is None: return
    try:
        import onnxoptimizer
        m=onnx.load_from_string(base_bytes)
        passes=["eliminate_deadend","eliminate_identity","eliminate_nop_transpose",
                "eliminate_nop_pad","eliminate_unused_initializer","extract_constant_to_initializer",
                "fuse_consecutive_squeezes","fuse_consecutive_transposes","fuse_add_bias_into_conv",
                "fuse_bn_into_conv","fuse_consecutive_concats"]
        opt=onnxoptimizer.optimize(m, passes)
        yield ("opt", opt)
    except Exception: pass
    try:
        import onnxsim
        m=onnx.load_from_string(base_bytes)
        sm,ok=onnxsim.simplify(m)
        if ok: yield ("onnxsim", sm)
    except Exception: pass

GENERATORS=[gen_base, gen_conv, gen_rewrite]
# subagent-built family generators are appended via golf_gens/*.py (see load_extra)
def load_extra():
    d=BASE/"golf_gens"
    if not d.exists(): return
    sys.path.insert(0,str(d))
    for f in sorted(d.glob("gen_*.py")):
        try:
            mod=__import__(f.stem)
            if hasattr(mod,"candidates"): GENERATORS.append(mod.candidates)
        except Exception as e:
            print(f"  [extra gen {f.stem} load FAIL: {e}]")

def golf_one(task_num, base_bytes):
    """Returns (base_cost, base_pts, best, tried). base_cost = VERIFIED cost of the
    actual submission.zip graph for this task (the authoritative reference)."""
    task=dataio.load_task(task_num)
    best=None; tried=[]; base_cost=None; base_pts=None
    for gen in GENERATORS:
        try: cands=list(gen(task_num, base_bytes))
        except Exception: cands=[]
        for label,m in cands:
            try: vr=verify.verify(m,task,task_num)
            except Exception: continue
            if vr["ok"]:
                c=cost_of(vr); tried.append((label,c,round(vr["points"],2)))
                if label=="base": base_cost=c; base_pts=vr["points"]
                if best is None or c<best[1]:
                    best=(label,c,vr["points"],m)
    return base_cost, base_pts, best, tried

if __name__=="__main__":
    a,b=int(sys.argv[1]),int(sys.argv[2])
    load_extra()
    res=json.load(open(BASE/"logs"/"blend_results.json"))
    # base graphs from current submission.zip
    import zipfile
    basez={}
    with zipfile.ZipFile(BASE/"out"/"submission.zip") as zf:
        for nm in zf.namelist():
            import re; mm=re.match(r"task(\d{3})\.onnx$",os.path.basename(nm))
            if mm: basez[int(mm.group(1))]=zf.read(nm)
    os.makedirs(GOUT,exist_ok=True)
    wins=0; gain=0.0
    for t in range(a,b+1):
        if t not in basez: continue
        base_cost,base_pts,best,tried=golf_one(t, basez.get(t))
        if base_cost is None: continue  # base graph itself failed to verify (shouldn't happen)
        rec={"task":t,"base_cost":base_cost,"base_pts":round(base_pts,2),"tried":tried}
        if best and best[1]<base_cost and best[0]!="base":
            onnx.save(best[3],str(GOUT/f"task{t:03d}.onnx"))
            d=best[2]-base_pts; wins+=1; gain+=d
            rec["win"]={"gen":best[0],"cost":best[1],"pts":round(best[2],2),"dpts":round(d,2)}
            print(f"WIN task{t:03d}: {best[0]} cost {base_cost}->{best[1]} pts {base_pts:.2f}->{best[2]:.2f} (+{d:.2f})")
        json.dump(rec,open(GOUT/f"task{t:03d}.json","w"))
    print(f"\ngolf2 [{a}..{b}]: {wins} wins, +{gain:.1f} proj")
