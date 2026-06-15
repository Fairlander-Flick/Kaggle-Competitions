#!/usr/bin/env python
"""Per-task neural-network "golf" harness for NeuroGolf-2026.

For one ARC task, train a tiny CNN that EXACTLY reproduces every
(input,output) one-hot pair, export to ONNX with fully static shapes, then
aggressively minimize the grader cost (memory + params) while preserving an
exact (output > 0.0) decode. Everything is verified against the official
grader via engine.verify.verify before being accepted.

Usage:
    nngolf.py <task_num> [--seeds N] [--epochs E] [--out PATH] [--max-cost C]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import List, Optional, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import onnx  # noqa: E402
from onnx import TensorProto, helper, numpy_helper  # noqa: E402

import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
import torch.nn.functional as F  # noqa: E402

from engine import dataio  # noqa: E402
from engine.verify import verify  # noqa: E402

CH, H, W = dataio.CHANNELS, dataio.HEIGHT, dataio.WIDTH
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
def build_xy(task: dict) -> Tuple[np.ndarray, np.ndarray, int]:
    """Stack every gradable pair into X,Y one-hot arrays [N,10,30,30]."""
    xs, ys = [], []
    for key in ("train", "test", "arc-gen"):
        for ex in task.get(key, []):
            xo = dataio.to_onehot(ex["input"])
            yo = dataio.to_onehot(ex["output"])
            if xo is None or yo is None:
                continue
            xs.append(xo[0])
            ys.append(yo[0])
    if not xs:
        return None, None, 0
    X = np.stack(xs).astype(np.float32)
    Y = np.stack(ys).astype(np.float32)
    return X, Y, len(xs)


# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------
class GolfCNN(nn.Module):
    """k-window conv rule.

    depth==0  -> a SINGLE Conv(10->10, kxk) writing logits straight to output.
                 Zero hidden intermediates => memory 0, params 100*k*k+10.
                 Optimal for linearly-separable window rules.
    depth>=1  -> body of `depth` Conv(.,width,kxk)+ReLU, then a 1x1 head to 10.
                 One small hidden layer captures non-linearly-separable rules;
                 keep width tiny (the hidden activation is the whole cost).

    Target = one-hot field: exactly the true channel >0 per in-grid cell, all
    channels <=0 for out-of-grid cells; (logit>0) must reproduce it exactly.
    """

    def __init__(self, width: int = 16, depth: int = 2, k: int = 3):
        super().__init__()
        self.depth = depth
        pad = k // 2
        if depth == 0:
            self.body = nn.Sequential()
            self.head = nn.Conv2d(CH, CH, k, padding=pad)
        else:
            layers = []
            c_in = CH
            for _ in range(depth):
                layers.append(nn.Conv2d(c_in, width, k, padding=pad))
                layers.append(nn.ReLU())
                c_in = width
            self.body = nn.Sequential(*layers)
            self.head = nn.Conv2d(c_in, CH, 1)

    def forward(self, x):
        return self.head(self.body(x))


def exact_match(logits: torch.Tensor, Y: torch.Tensor) -> int:
    """Count pairs where (logits>0) == (Y==1) at EVERY cell/channel."""
    pred = (logits > 0.0)
    tgt = (Y > 0.5)
    eq = (pred == tgt).reshape(Y.shape[0], -1).all(dim=1)
    return int(eq.sum().item())


def train_one(X: torch.Tensor, Y: torch.Tensor, width: int, depth: int,
              seed: int, epochs: int, k: int = 3, margin: float = 1.0
              ) -> Tuple[Optional[GolfCNN], int]:
    """Train a single model. Returns (model, n_exact_matched_pairs)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = GolfCNN(width, depth, k).to(DEV)
    opt = torch.optim.Adam(model.parameters(), lr=2e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    N = X.shape[0]
    best_state, best_match = None, -1
    tgt = (Y > 0.5).float()  # 1 where correct channel
    for ep in range(epochs):
        model.train()
        opt.zero_grad()
        logits = model(X)
        # Per-cell cross entropy on the argmax color over channels.
        # Background (out-of-grid) cells have all-zero target -> we want all
        # logits negative there, handled by the margin/BCE term below.
        # Hinge / margin loss: correct channel >= +margin, wrong <= -margin.
        # For all-zero-target (out of grid) cells, tgt==0 everywhere -> all
        # logits pushed below -margin. This is exactly the decode condition.
        pos = F.relu(margin - logits) * tgt
        neg = F.relu(margin + logits) * (1.0 - tgt)
        loss = pos.sum() / N + neg.sum() / N
        loss.backward()
        opt.step()
        sched.step()
        if ep % 10 == 0 or ep == epochs - 1:
            model.eval()
            with torch.no_grad():
                m = exact_match(model(X), Y)
            if m > best_match:
                best_match = m
                best_state = {k: v.detach().clone()
                              for k, v in model.state_dict().items()}
            if m == N:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        m = exact_match(model(X), Y)
    return model, m


# ----------------------------------------------------------------------------
# ONNX export + cost minimization
# ----------------------------------------------------------------------------
def _const(name, arr):
    return numpy_helper.from_array(np.asarray(arr), name=name)


def export_onnx(model: GolfCNN, dtype: str) -> onnx.ModelProto:
    """Hand-build a static-shape ONNX graph from the trained conv stack.

    dtype controls the intermediate activation precision used for the conv
    body ('float32', 'float16'). The decode only needs sign correctness so
    lower precision is fine when it survives verification. Final head writes a
    fp32 tensor directly into `output` (free).
    """
    np_dt = {"float32": np.float32, "float16": np.float16}[dtype]
    onnx_dt = {"float32": TensorProto.FLOAT,
               "float16": TensorProto.FLOAT16}[dtype]

    sd = model.state_dict()
    nodes, inits = [], []

    def _kpad(w):  # kernel_shape + pads from a conv weight [O,I,kh,kw]
        kh, kw = int(w.shape[2]), int(w.shape[3])
        return [kh, kw], [kh // 2, kw // 2, kh // 2, kw // 2]

    cur = "input"  # fp32 [1,10,30,30]
    # If body runs in fp16, cast input once (only matters when there's a body;
    # for depth==0 the single head conv runs in fp32 straight to output).
    has_body = len(list(model.body)) > 0
    if dtype != "float32" and has_body:
        nodes.append(helper.make_node("Cast", [cur], ["x0"], to=onnx_dt))
        cur = "x0"

    # conv body
    idx = 0
    li = 0
    body = model.body
    for layer in body:
        if isinstance(layer, nn.Conv2d):
            w = sd[f"body.{li}.weight"].cpu().numpy().astype(np_dt)
            b = sd[f"body.{li}.bias"].cpu().numpy().astype(np_dt)
            wn, bn = f"w{idx}", f"b{idx}"
            inits.append(_const(wn, w))
            inits.append(_const(bn, b))
            out = f"c{idx}"
            ks, pads = _kpad(w)
            nodes.append(helper.make_node(
                "Conv", [cur, wn, bn], [out],
                kernel_shape=ks, pads=pads, strides=[1, 1]))
            cur = out
            idx += 1
        elif isinstance(layer, nn.ReLU):
            out = f"r{idx}"
            nodes.append(helper.make_node("Relu", [cur], [out]))
            cur = out
            idx += 1
        li += 1

    # head conv -> produces logits feeding `output`. kernel may be kxk (depth0)
    # or 1x1 (with a body). When there is no body it runs in fp32 directly.
    hw = sd["head.weight"].cpu().numpy()
    hb = sd["head.bias"].cpu().numpy()
    hks, hpads = _kpad(hw)
    if not has_body:
        hwn = _const("hw", hw.astype(np.float32))
        hbn = _const("hb", hb.astype(np.float32))
        inits += [hwn, hbn]
        nodes.append(helper.make_node(
            "Conv", [cur, "hw", "hb"], ["output"],
            kernel_shape=hks, pads=hpads, strides=[1, 1]))
        inp = helper.make_tensor_value_info("input", TensorProto.FLOAT,
                                            [1, CH, H, W])
        outp = helper.make_tensor_value_info("output", TensorProto.FLOAT,
                                             [1, CH, H, W])
        graph = helper.make_graph(nodes, "golf", [inp], [outp], inits)
        m = helper.make_model(graph,
                              opset_imports=[helper.make_opsetid("", 13)])
        m.ir_version = 8
        return onnx.shape_inference.infer_shapes(m, strict_mode=True)
    if dtype != "float32":
        # do head in the body dtype then cast to fp32 output
        hwn = numpy_helper.from_array(hw.astype(np_dt), name="hw")
        hbn = numpy_helper.from_array(hb.astype(np_dt), name="hb")
        inits += [hwn, hbn]
        nodes.append(helper.make_node(
            "Conv", [cur, "hw", "hb"], ["hlogit"],
            kernel_shape=[1, 1], pads=[0, 0, 0, 0], strides=[1, 1]))
        nodes.append(helper.make_node("Cast", ["hlogit"], ["output"],
                                      to=TensorProto.FLOAT))
    else:
        hwn = numpy_helper.from_array(hw.astype(np.float32), name="hw")
        hbn = numpy_helper.from_array(hb.astype(np.float32), name="hb")
        inits += [hwn, hbn]
        nodes.append(helper.make_node(
            "Conv", [cur, "hw", "hb"], ["output"],
            kernel_shape=[1, 1], pads=[0, 0, 0, 0], strides=[1, 1]))

    inp = helper.make_tensor_value_info("input", TensorProto.FLOAT,
                                        [1, CH, H, W])
    outp = helper.make_tensor_value_info("output", TensorProto.FLOAT,
                                         [1, CH, H, W])
    graph = helper.make_graph(nodes, "golf", [inp], [outp], inits)
    m = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    m.ir_version = 8
    m = onnx.shape_inference.infer_shapes(m, strict_mode=True)
    return m


def static_ok(model: onnx.ModelProto) -> bool:
    """Every value_info/output tensor must have a fully static positive shape."""
    try:
        g = onnx.shape_inference.infer_shapes(model, strict_mode=True).graph
    except Exception:
        return False
    for vi in list(g.value_info) + list(g.output):
        tt = vi.type.tensor_type
        if not tt.HasField("shape"):
            return False
        for d in tt.shape.dim:
            if d.HasField("dim_param") or not d.HasField("dim_value") \
                    or d.dim_value <= 0:
                return False
    return True


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------
def solve(task_num: int, seeds: int, epochs: int, max_cost: float
          ) -> Tuple[Optional[onnx.ModelProto], dict]:
    task = dataio.load_task(task_num)
    X, Y, n = build_xy(task)
    if n == 0:
        return None, {"err": "no gradable pairs"}
    Xt = torch.from_numpy(X).to(DEV)
    Yt = torch.from_numpy(Y).to(DEV)

    best_model = None
    best_res = {"ok": False, "points": 0.0, "memory": None,
                "params": None, "err": "no exact-match net found"}

    # Cheapest architectures first: single kxk conv (zero hidden mem) then a
    # tiny hidden layer, escalating width/depth/kernel only if needed. The
    # FIRST config that yields a verified exact graph is the cheapest one.
    configs = [(0, 0, 3), (0, 0, 5), (2, 1, 3), (4, 1, 3), (2, 1, 5),
               (4, 1, 5), (8, 1, 3), (8, 1, 5), (16, 2, 3), (16, 2, 5),
               (32, 2, 3), (32, 2, 5), (48, 3, 5), (64, 3, 5)]
    configs = [c for c in configs if c[0] <= globals().get("_MAXWIDTH", 999)]
    for width, depth, k in configs:
        got_exact = False
        for seed in range(seeds):
            model, m = train_one(Xt, Yt, width, depth, seed, epochs, k)
            if m != n:
                continue
            got_exact = True
            # Try dtype variants from cheapest up.
            for dtype in ("float16", "float32"):
                try:
                    om = export_onnx(model, dtype)
                except Exception as e:  # noqa: BLE001
                    continue
                if not static_ok(om):
                    continue
                res = verify(om, task, task_num)
                if res.get("ok"):
                    cost = res["memory"] + res["params"]
                    if cost <= max_cost and (
                            best_res["memory"] is None
                            or cost < best_res["memory"] + best_res["params"]):
                        best_model = om
                        best_res = res
            # one exact-match seed for this config is usually enough; keep
            # scanning seeds only if none verified yet
            if best_model is not None:
                break
        # stop escalating architecture size once we have a verified solution
        if best_model is not None:
            break
        if got_exact:
            # exact in torch but failed verify across dtypes; keep escalating
            continue
    return best_model, best_res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task_num", type=int)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--epochs", type=int, default=3000)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--max-cost", type=float, default=float("inf"))
    ap.add_argument("--maxwidth", type=int, default=999,
                    help="skip configs whose hidden width exceeds this")
    args = ap.parse_args()
    global _MAXWIDTH
    _MAXWIDTH = args.maxwidth

    out = args.out or f"out/nn/task{args.task_num:03d}.onnx"
    result = {"task": args.task_num, "ok": False, "points": 0.0,
              "memory": 0, "params": 0, "err": ""}
    try:
        model, res = solve(args.task_num, args.seeds, args.epochs,
                           args.max_cost)
        if model is not None and res.get("ok"):
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            onnx.save(model, out)
            result.update(ok=True, points=round(res["points"], 4),
                          memory=res["memory"], params=res["params"],
                          err="")
        else:
            result["err"] = res.get("err", "no solution")
    except Exception as e:  # noqa: BLE001 — never crash the loop
        result["err"] = f"{type(e).__name__}: {e}"
    print(json.dumps(result))


if __name__ == "__main__":
    main()
