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


_OFF4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
_OFF8 = _OFF4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def build_neighbor_recolor(target, src, newc, conn):
    """Morphological neighbour-conditioned recolor (FAMILY, not one-off):
    a cell of colour `target` that has >=1 conn-neighbour of colour `src`
    becomes colour `newc`; everything else is unchanged.

    Construction (2 small intermediates → ~16.6 pts, canvas-safe):
      cnt  = Conv(input, W[1,10,3,3])  W[target] center = 9 ("is-target"),
             W[src] ring = 1 over the conn offsets, zero-pad → float [1,1,30,30]
             cnt = 9*[cell is target] + (#src conn-neighbours), max ring 8 < 9
      chg  = Greater(cnt, 9)  bool [1,1,30,30]  (strict > : target & >=1 src)
      out  = Where(chg, NEWC[1,10,1,1], input)  → output (free, final node)
    Padding columns are all-zero (channel `target` = 0 there) so they never
    flip and Conv zero-pad never invents a `src` neighbour → canvas-safe.
    params = 90(W) + 1(thr) + 10(NEWC) = 101 ; memory = 3600(cnt)+900(chg)."""
    W = np.zeros((1, 10, 3, 3), dtype=np.float32)
    W[0, target, 1, 1] = 9.0
    off = _OFF8 if conn == 8 else _OFF4
    for dr, dc in off:
        W[0, src, dr + 1, dc + 1] = 1.0
    w = helper.make_tensor("W", TensorProto.FLOAT, [1, 10, 3, 3],
                           W.flatten().tolist())
    thr = helper.make_tensor("T", TensorProto.FLOAT, [], [9.0])
    NEW = np.zeros((1, 10, 1, 1), dtype=np.float32)
    NEW[0, newc, 0, 0] = 1.0
    nw = helper.make_tensor("NEWC", TensorProto.FLOAT, [1, 10, 1, 1],
                            NEW.flatten().tolist())
    nodes = [
        helper.make_node("Conv", ["input", "W"], ["cnt"],
                          kernel_shape=[3, 3], pads=[1, 1, 1, 1],
                          strides=[1, 1]),
        helper.make_node("Greater", ["cnt", "T"], ["chg"]),
        helper.make_node("Where", ["chg", "NEWC", "input"], ["output"]),
    ]
    return _model(nodes, [w, thr, nw])


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


def _nbr_any(mask, off):
    """bool[H,W]: cell has >=1 in-grid neighbour (per `off`) that is True.
    Zero-pad outside the grid — byte-identical to the ONNX Conv zero-pad."""
    H, W = mask.shape
    pad = np.zeros((H + 2, W + 2), dtype=bool)
    pad[1:-1, 1:-1] = mask
    acc = np.zeros((H, W), dtype=bool)
    for dr, dc in off:
        acc |= pad[1 + dr:1 + dr + H, 1 + dc:1 + dc + W]
    return acc


def _detect_neighbor_recolor(ps):
    """Pure data: find (target, src, newc, conn) s.t. every pair is exactly
    'cell==target AND has a conn-neighbour==src  ->  newc, else unchanged'.
    Returns the tuple or None. (Single-pass on the INPUT grid — an iterative
    flood will mismatch arc-gen here and correctly fall through.)"""
    arrs = [(np.array(i), np.array(o)) for i, o in ps]
    tgt, new = set(), set()
    any_chg = False
    for ia, oa in arrs:
        d = ia != oa
        if d.any():
            any_chg = True
            tgt.update(ia[d].tolist())
            new.update(oa[d].tolist())
    if not any_chg or len(tgt) != 1 or len(new) != 1:
        return None
    target, newc = tgt.pop(), new.pop()
    if target == newc:
        return None
    for conn, off in ((4, _OFF4), (8, _OFF8)):
        for src in range(10):
            good = True
            for ia, oa in arrs:
                pred = (ia == target) & _nbr_any(ia == src, off)
                # predicted-change cells must become exactly newc; every
                # other cell must be untouched.
                if not (np.array_equal(oa[pred], np.full(pred.sum(), newc))
                        and np.array_equal(oa[~pred], ia[~pred])):
                    good = False
                    break
            if good:
                return (target, src, newc, conn)
    return None


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

    # D3 morphological neighbour-conditioned recolor (FAMILY ~16.6 pts).
    # Only reachable when no cheaper exact rule above fit (a conditional
    # recolor breaks D2's consistent global map, so it falls through here).
    if same:
        nr = _detect_neighbor_recolor(ps)
        if nr:
            t, s, nc, cn = nr
            return (f"nbr_recolor[{t}<{s}>{nc}/{cn}]",
                    build_neighbor_recolor(t, s, nc, cn), 101)

    return None
