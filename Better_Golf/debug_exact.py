"""Diagnostic: can SGD reach 100%-EXACT reproduction on window-learnable tasks?
Trains a generous net (GPU) and reports the max exact-pair count reached."""
import sys, time, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
sys.path.insert(0, ".")
from engine import dataio

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device", DEV, "cuda", torch.cuda.is_available(), flush=True)

def build_xy(task):
    xs, ys = [], []
    for k in ("train", "test", "arc-gen"):
        for ex in task.get(k, []):
            xo, yo = dataio.to_onehot(ex["input"]), dataio.to_onehot(ex["output"])
            if xo is None or yo is None: continue
            xs.append(xo[0]); ys.append(yo[0])
    return np.stack(xs).astype(np.float32), np.stack(ys).astype(np.float32)

class Net(nn.Module):
    def __init__(self, w, d, k):
        super().__init__()
        p = k // 2; layers = []; c = 10
        for _ in range(d):
            layers += [nn.Conv2d(c, w, k, padding=p), nn.ReLU()]; c = w
        self.body = nn.Sequential(*layers); self.head = nn.Conv2d(c, 10, 1)
    def forward(self, x): return self.head(self.body(x))

def exact(logits, Y):
    pred = logits > 0; tgt = Y > 0.5
    return int((pred == tgt).reshape(Y.shape[0], -1).all(1).sum())

for tn in [98, 222, 77]:
    task = dataio.load_task(tn)
    X, Y = build_xy(task); N = X.shape[0]
    Xt = torch.from_numpy(X).to(DEV); Yt = torch.from_numpy(Y).to(DEV)
    tgt = (Yt > 0.5).float()
    best = -1
    for (w, d, k) in [(32, 2, 3), (64, 3, 5), (96, 4, 5)]:
        torch.manual_seed(0)
        m = Net(w, d, k).to(DEV)
        opt = torch.optim.Adam(m.parameters(), lr=2e-3)
        t0 = time.time()
        for ep in range(4000):
            opt.zero_grad(); lo = m(Xt)
            loss = (F.relu(1 - lo) * tgt).sum() / N + (F.relu(1 + lo) * (1 - tgt)).sum() / N
            loss.backward(); opt.step()
            if ep % 500 == 0 or ep == 3999:
                with torch.no_grad(): e = exact(m(Xt), Yt)
                best = max(best, e)
                if e == N: break
        print(f"task{tn:03d} w{w}d{d}k{k}: best_exact={best}/{N} "
              f"({time.time()-t0:.0f}s){' SOLVED' if best==N else ''}", flush=True)
        if best == N: break
    print(f"=> task{tn:03d} max_exact={best}/{N}", flush=True)
