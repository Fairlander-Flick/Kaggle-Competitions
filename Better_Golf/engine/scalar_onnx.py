"""Phase-2 DIFFERENTIAL recompile — minimal static-shape ONNX builders.

Cost model (verbatim from data/neurogolf_utils):
  points = max(1, 25 - ln(memory + params))
  memory = Σ static byte-size of every tensor EXCEPT named input/output;
           strict_mode shape inference — ANY non-static dim → DISQUALIFIED.
  params = Σ element counts of all initializers + Constant values.
So: input & output tensors are FREE; a graph whose only node emits `output`
with no initializer/Constant pays 0 → 25 pts. Each builder below is the
cheapest canvas-safe construction for one data-derived rule.

Detectors are DATA-DRIVEN (derive the rule from the actual train+test+
arc-gen grids, never from English hints — those are noisy priors only).
Padding cells are all-zero one-hot columns; every builder here maps an
all-zero column to all-zero, so all are canvas-safe by construction.
"""
from __future__ import annotations

import numpy as np
import onnx
from onnx import TensorProto, helper

from . import dataio

_IR = 10
_OPS = [helper.make_opsetid("", 10)]
_SHAPE = [1, 10, 30, 30]


def _model(nodes, inits):
    x = helper.make_tensor_value_info("input", TensorProto.FLOAT, _SHAPE)
    y = helper.make_tensor_value_info("output", TensorProto.FLOAT, _SHAPE)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version=_IR, opset_imports=_OPS)


# ---- builders (each: smallest graph, final node → `output`) -------------

def build_identity():
    """out == in. Cost 0 → 25.0."""
    return _model([helper.make_node("Identity", ["input"], ["output"])], [])


def build_transpose():
    """out == in transposed (HxW grid top-left → WxH grid top-left, padding
    stays zero). perm is a node attribute (NOT counted). Cost 0 → 25.0."""
    n = helper.make_node("Transpose", ["input"], ["output"], perm=[0, 1, 3, 2])
    return _model([n], [])


def build_recolor_gather(inv):
    """Global colour bijection via channel Gather. `inv[d]` = the input
    channel feeding output channel d (i.e. inverse of the colour map).
    params = 10 → 22.70. Canvas-safe (Gather of an all-zero column = 0)."""
    idx = helper.make_tensor("idx", TensorProto.INT64, [10],
                             [int(v) for v in inv])
    n = helper.make_node("Gather", ["input", "idx"], ["output"], axis=1)
    return _model([n], [idx])


def build_recolor_conv(mp):
    """General colour map (possibly many→one) via 1x1 Conv. W[d,c]=1 iff
    colour c maps to d. params = 100 → 20.40. Canvas-safe."""
    W = np.zeros((10, 10, 1, 1), dtype=np.float32)
    for c, d in mp.items():
        W[d, c, 0, 0] = 1.0
    w = helper.make_tensor("W", TensorProto.FLOAT, [10, 10, 1, 1],
                           W.flatten().tolist())
    n = helper.make_node("Conv", ["input", "W"], ["output"],
                          kernel_shape=[1, 1], pads=[0, 0, 0, 0],
                          strides=[1, 1])
    return _model([n], [w])


# ---- data-driven detector cascade ---------------------------------------

def _pairs(task):
    out = []
    for k in ("train", "test", "arc-gen"):
        for ex in task.get(k, []):
            i, o = ex["input"], ex["output"]
            if max(len(i), len(i[0])) > 30:
                continue  # grader skips >30
            out.append((i, o))
    return out


def detect(task_num):
    """Return (label, builder_model, est_params) for the cheapest exact
    canvas-safe rule found purely from this task's data, else None.
    est_params lets the caller rank vs the current blend pick before the
    (slower) official verify."""
    task = dataio.load_task(task_num)
    ps = _pairs(task)
    if not ps:
        return None

    same = all(len(i) == len(o) and len(i[0]) == len(o[0]) for i, o in ps)
    transp = all(len(i) == len(o[0]) and len(i[0]) == len(o) for i, o in ps)

    # D0 identity (0 params → 25.0)
    if same and all(i == o for i, o in ps):
        return ("identity", build_identity(), 0)

    # D1 transpose (0 params → 25.0)
    if transp and all([list(r) for r in zip(*i)] == o for i, o in ps):
        return ("transpose", build_transpose(), 0)

    # D2 global colour map (same shape, consistent per-cell substitution)
    if same:
        mp = {}
        ok = True
        for i, o in ps:
            for ra, rb in zip(i, o):
                for a, b in zip(ra, rb):
                    if a in mp and mp[a] != b:
                        ok = False
                        break
                    mp[a] = b
                if not ok:
                    break
            if not ok:
                break
        if ok and mp:
            # Try bijection → Gather (params 10, 22.70). Build inverse:
            # output channel d gets input channel inv[d] = the colour c
            # with mp[c]=d. Fill unconstrained colours to complete a perm.
            inj = len(set(mp.values())) == len(mp)
            if inj:
                inv = [None] * 10
                used_in = set()
                for c, d in mp.items():
                    inv[d] = c
                    used_in.add(c)
                free_in = [c for c in range(10) if c not in used_in]
                for d in range(10):
                    if inv[d] is None:
                        inv[d] = free_in.pop()
                return ("recolor_gather", build_recolor_gather(inv), 10)
            return ("recolor_conv", build_recolor_conv(mp), 100)

    return None
