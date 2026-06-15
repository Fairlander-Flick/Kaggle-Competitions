"""Decisive test: can a CHEAP net hit 100%-exact (=> beat the public base)?
For a few tasks, sweep small configs with a big epoch budget; for each, report
max exact-match and (if exact) the official verified cost vs base."""
import sys, time, json, math, numpy as np, torch
sys.path.insert(0, ".")
from engine import dataio
from engine.verify import verify
import nngolf

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device", DEV, flush=True)
cost = json.load(open("logs/vyank_costmap.json"))

CFG = [(0,0,3),(0,0,5),(2,1,3),(4,1,3),(8,1,3),(4,1,5),(8,1,5),(16,1,5),(16,2,3)]
TASKS = [222, 98, 97, 4, 193]
EPOCHS, SEEDS = 15000, 2

for tn in TASKS:
    task = dataio.load_task(tn)
    X, Y, n = nngolf.build_xy(task)
    Xt = torch.from_numpy(X).to(DEV); Yt = torch.from_numpy(Y).to(DEV)
    base = cost.get(str(tn)); bpts = max(1,25-math.log(max(1,base))) if base else None
    print(f"\n### task{tn:03d} base_cost={base} base_pts={bpts}", flush=True)
    best_cost = None
    for (w,d,k) in CFG:
        got = None
        for s in range(SEEDS):
            t0=time.time()
            m, mexact = nngolf.train_one(Xt, Yt, w, d, s, EPOCHS, k)
            if mexact == n:
                for dt in ("float16","float32"):
                    try: om = nngolf.export_onnx(m, dt)
                    except Exception: continue
                    if not nngolf.static_ok(om): continue
                    r = verify(om, task, tn)
                    if r.get("ok"):
                        c = r["memory"]+r["params"]; pts=r["points"]
                        got = (c,pts,dt)
                        break
            if got: break
        if got:
            c,pts,dt = got
            win = "WIN +%.2f"%(pts-bpts) if base and c<base else "(not<base)"
            print(f"  cfg w{w}d{d}k{k}: EXACT cost={c} pts={pts:.2f} {dt} {win} [{time.time()-t0:.0f}s]", flush=True)
            best_cost = c if best_cost is None else min(best_cost,c)
            break  # cheapest-first: first exact config is the cheapest
        else:
            print(f"  cfg w{w}d{d}k{k}: max_exact={mexact}/{n} (no exact)", flush=True)
    print(f"=> task{tn:03d} cheapest_exact_cost={best_cost} (base {base})", flush=True)
