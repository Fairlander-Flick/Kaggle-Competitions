"""Transformation families: detector + minimal-cost ONNX builder per family.

COST MODEL (from neurogolf_utils, exact):
    cost  = memory + params
    memory = sum of static byte-sizes of every tensor EXCEPT those literally
             named "input" / "output"  (so a single node whose only output is
             named "output" contributes ZERO memory).
    params = sum of element counts of all initializers + Constant-node values.
    points = max(1, 25 - ln(max(1, memory + params)))   # per task, 400 tasks

Design rule baked in here: prefer a ONE-NODE graph whose sole node emits the
tensor named "output". Every extra intermediate tensor pays its full static
size; every Constant/initializer pays its element count. Families are ordered
by best achievable points so the solver tries the cheapest correct one first.

Only PROVABLY canvas-safe families live here. The grid lives top-left inside a
fixed 30x30 all-zero-padded one-hot canvas; a family is "canvas-safe" iff its
canvas-global ONNX op equals the intended per-grid transform including padding.
Per-cell / channel-only ops (identity, recolor) are canvas-safe. Position- or
shape-changing ops are NOT and are added later, task by task, with their own
re-embedding construction.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import onnx
import onnx.helper as h
from onnx import TensorProto

Grid = List[List[int]]
Pair = Tuple[Grid, Grid]

IR_VERSION = 10
OPSET = [h.make_opsetid("", 10)]
SHAPE = [1, 10, 30, 30]


def _io():
    x = h.make_tensor_value_info("input", TensorProto.FLOAT, SHAPE)
    y = h.make_tensor_value_info("output", TensorProto.FLOAT, SHAPE)
    return x, y


def _model(graph) -> onnx.ModelProto:
    return h.make_model(graph, ir_version=IR_VERSION, opset_imports=OPSET)


def points_for(memory: int, params: int) -> float:
    return max(1.0, 25.0 - math.log(max(1.0, memory + params)))


# --------------------------------------------------------------------------- #
# Family base
# --------------------------------------------------------------------------- #
class Family:
    name = "base"
    est_points = 0.0  # best-case points if it fits; used only for ordering

    def detect(self, train: List[Pair]) -> Optional[dict]:
        """Return a spec dict if this family explains every TRAIN pair, else None.
        The solver re-checks the spec against ALL pairs (train+test+arc-gen)."""
        raise NotImplementedError

    def apply(self, spec: dict, grid: Grid) -> Optional[Grid]:
        raise NotImplementedError

    def build_onnx(self, spec: dict) -> onnx.ModelProto:
        raise NotImplementedError


def _same_shape(p: Pair) -> bool:
    i, o = p
    return len(i) == len(o) and len(i[0]) == len(o[0])


# --------------------------------------------------------------------------- #
# 1. Identity  — output == input.  1 node, 0 params, 0 memory => 25.000 pts
# --------------------------------------------------------------------------- #
class Identity(Family):
    name = "identity"
    est_points = 25.0

    def detect(self, train):
        for i, o in train:
            if i != o:
                return None
        return {}

    def apply(self, spec, grid):
        return [row[:] for row in grid]

    def build_onnx(self, spec):
        x, y = _io()
        n = h.make_node("Identity", ["input"], ["output"])
        return _model(h.make_graph([n], "identity", [x], [y]))


# --------------------------------------------------------------------------- #
# Shared: derive a deterministic per-color map from same-shape pairs
# --------------------------------------------------------------------------- #
def _color_map(train: List[Pair]) -> Optional[Dict[int, int]]:
    m: Dict[int, int] = {}
    for i, o in train:
        if not _same_shape((i, o)):
            return None
        for r in range(len(i)):
            for c in range(len(i[0])):
                a, b = i[r][c], o[r][c]
                if a in m and m[a] != b:
                    return None  # not a function of color alone
                m[a] = b
    return m


# --------------------------------------------------------------------------- #
# 2. ColorPermute — recolor that is a bijection. Gather(axis=1) over channels.
#    1 node + INT64[10] initializer => params 10 => 25 - ln(10) = 22.697 pts
# --------------------------------------------------------------------------- #
class ColorPermute(Family):
    name = "color_permute"
    est_points = 22.697

    def detect(self, train):
        m = _color_map(train)
        if m is None or all(k == v for k, v in m.items()):
            return None  # identity handled by Identity
        full = {c: c for c in range(10)}
        full.update(m)
        targets = list(full.values())
        if len(set(targets)) != 10:
            return None  # not bijective -> ColorLUT will handle it
        # Gather indices g: output_channel k receives input_channel g[k].
        inv = {v: k for k, v in full.items()}
        g = [inv[k] for k in range(10)]
        return {"g": g, "map": full}

    def apply(self, spec, grid):
        m = spec["map"]
        return [[m[c] for c in row] for row in grid]

    def build_onnx(self, spec):
        x, y = _io()
        idx = h.make_tensor("g", TensorProto.INT64, [10], spec["g"])
        n = h.make_node("Gather", ["input", "g"], ["output"], axis=1)
        return _model(h.make_graph([n], "color_permute", [x], [y], [idx]))


# --------------------------------------------------------------------------- #
# 3. ColorLUT — general (possibly non-injective) recolor. 1x1 Conv, weight
#    [10,10,1,1] => params 100 => 25 - ln(100) = 20.395 pts
# --------------------------------------------------------------------------- #
class ColorLUT(Family):
    name = "color_lut"
    est_points = 20.395

    def detect(self, train):
        m = _color_map(train)
        if m is None or all(k == v for k, v in m.items()):
            return None
        full = {c: c for c in range(10)}
        full.update(m)
        return {"map": full}

    def apply(self, spec, grid):
        m = spec["map"]
        return [[m[c] for c in row] for row in grid]

    def build_onnx(self, spec):
        x, y = _io()
        w = np.zeros((10, 10, 1, 1), dtype=np.float32)
        for a, b in spec["map"].items():
            w[b, a, 0, 0] = 1.0
        wt = h.make_tensor("W", TensorProto.FLOAT, [10, 10, 1, 1],
                           w.flatten().tolist())
        n = h.make_node("Conv", ["input", "W"], ["output"],
                        kernel_shape=[1, 1], pads=[0, 0, 0, 0])
        return _model(h.make_graph([n], "color_lut", [x], [y], [wt]))


# --------------------------------------------------------------------------- #
# 4. Fractal3 — 3x3 self-fractal, background=0 (task001 family).
#    out[3i:3i+3, 3j:3j+3] = input  if input[i,j]!=0 else 0-block.
#    Position/shape-changing => NOT canvas-safe: build the 9x9 fractal then
#    Pad back into the 30x30 canvas (Pad opset-13 pads = input, tiny params).
# --------------------------------------------------------------------------- #
class Fractal3(Family):
    name = "fractal3_bg0"
    est_points = 15.0  # several small intermediates; correctness first

    def detect(self, train):
        for i, o in train:
            if len(i) != 3 or len(i[0]) != 3:
                return None
            if len(o) != 9 or len(o[0]) != 9:
                return None
        return {}

    def apply(self, spec, grid):
        if len(grid) != 3 or len(grid[0]) != 3:
            return None
        out = [[0] * 9 for _ in range(9)]
        for i in range(3):
            for j in range(3):
                if grid[i][j] != 0:
                    for r in range(3):
                        for c in range(3):
                            out[i * 3 + r][j * 3 + c] = grid[r][c]
        return out

    def build_onnx(self, spec):
        x = h.make_tensor_value_info("input", TensorProto.FLOAT, SHAPE)
        y = h.make_tensor_value_info("output", TensorProto.FLOAT, SHAPE)
        op = [h.make_opsetid("", 13)]

        def i64(name, vals):
            return h.make_tensor(name, TensorProto.INT64, [len(vals)], vals)

        ones9 = h.make_tensor("ones9", TensorProto.FLOAT, [1, 1, 9, 9],
                              [1.0] * 81)
        inits = [
            i64("g_s", [0, 0]), i64("g_e", [3, 3]), i64("g_ax", [2, 3]),
            i64("m_s", [1]), i64("m_e", [10]), i64("m_ax", [1]),
            i64("rsum_ax", [1]),
            h.make_tensor("rs_sc", TensorProto.FLOAT, [4], [1, 1, 3, 3]),
            i64("tg_rep", [1, 1, 3, 3]), i64("mb_rep", [1, 10, 1, 1]),
            ones9,
            i64("ch_pad", [0, 0, 0, 0, 0, 9, 0, 0]),
            i64("pad", [0, 0, 0, 0, 0, 0, 21, 21]),
            h.make_tensor("pv", TensorProto.FLOAT, [], [0.0]),
        ]
        nodes = [
            h.make_node("Slice", ["input", "g_s", "g_e", "g_ax"], ["G3"]),
            h.make_node("Tile", ["G3", "tg_rep"], ["TG"]),
            h.make_node("Slice", ["G3", "m_s", "m_e", "m_ax"], ["Mc"]),
            h.make_node("ReduceSum", ["Mc", "rsum_ax"], ["Msum"],
                        keepdims=1),
            h.make_node("Resize", ["Msum", "", "rs_sc"], ["MB"],
                        mode="nearest",
                        coordinate_transformation_mode="asymmetric",
                        nearest_mode="floor"),
            h.make_node("Tile", ["MB", "mb_rep"], ["MBt"]),
            h.make_node("Mul", ["TG", "MBt"], ["core"]),
            # off-blocks (mask==0) are solid color-0 => set channel 0 there.
            h.make_node("Sub", ["ones9", "MB"], ["off"]),
            h.make_node("Pad", ["off", "ch_pad", "pv"], ["offch0"],
                        mode="constant"),
            h.make_node("Add", ["core", "offch0"], ["O9"]),
            h.make_node("Pad", ["O9", "pad", "pv"], ["output"],
                        mode="constant"),
        ]
        return h.make_model(
            h.make_graph(nodes, "fractal3", [x], [y], inits),
            ir_version=IR_VERSION, opset_imports=op)


# Ordered cheapest-correct-first (highest est_points first).
REGISTRY: List[Family] = [Identity(), ColorPermute(), ColorLUT(), Fractal3()]
