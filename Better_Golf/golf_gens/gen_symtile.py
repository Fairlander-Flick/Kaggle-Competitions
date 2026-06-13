"""gen_symtile.py — minimal ONNX graphs for SYMMETRY / TILING / PERIODICITY /
INTEGER-SCALING ARC tasks (NeuroGolf-2026).

Public API:
    candidates(task_num, base_bytes) -> yields (label:str, model:onnx.ModelProto)

Everything is wrapped so import + candidates() never raise; on any failure a
family simply yields nothing. Graphs use only the allowed op vocabulary
(Slice, Concat, Pad, Tile, Transpose, ConvTranspose, Mul, Identity), keep
input/output named exactly "input"/"output" with static shape [1,10,30,30]
FLOAT, and pass onnx.checker.

Cost model (mirrors engine.verify): cost = memory(intermediate tensors) +
params(initializer + Constant element counts). input/output are FREE. So the
golf objective is: minimise the number AND element-count of intermediate
tensors, and the size of initializers.

Design notes / families
------------------------
1. INTEGER UPSCALE by k (each cell -> k x k block): a single grouped
   ConvTranspose with a constant ones-kernel writes straight into "output"
   (free) -> only cost is the kernel initializer (10*1*k*k elems) plus any
   bias. Nearest-neighbour upsample of the whole 30x30 frame, then the static
   output crop to [1,10,30,30] keeps the top-left block in place, so it is
   exact for top-left-anchored variable-extent grids.

2. MIRROR completion (double width  output=[I | fliplr(I)]  or
   double height output=[I ; flipud(I)]): one reverse-Slice + one Concat +
   one Pad. The reverse-Slice operates only on the actual H/W content block
   (fixed when the task has a single input shape), so anchoring is respected.

3. MIRROR-QUAD (output = [[I, fliplr],[flipud, flip]]): assemble the 2H x 2W
   block from reverse-Slices + Concats, then Pad to the frame.

Each family yields several construction variants (different op orderings /
fewer intermediates); the driver/verifier keeps whichever is exact AND cheaper
than the task's current base graph.
"""
from __future__ import annotations

import numpy as np

try:
    import onnx
    from onnx import helper as oh, TensorProto as TP, numpy_helper as onh
except Exception:  # pragma: no cover - onnx must exist in the env
    onnx = None

GS = [1, 10, 30, 30]
C, F = 10, 30  # channels, frame size

# --------------------------------------------------------------------------
# task-shape probe (uses engine.dataio if importable; else None -> skip)
# --------------------------------------------------------------------------
def _task_pairs(task_num):
    try:
        from engine import dataio
        task = dataio.load_task(task_num)
        return task.get("train", []) + task.get("test", []) + task.get("arc-gen", [])
    except Exception:
        return []


def _shp(g):
    return (len(g), len(g[0]) if g else 0)


def _single_input_shape(pairs):
    shps = {_shp(p["input"]) for p in pairs}
    return next(iter(shps)) if len(shps) == 1 else None


# --------------------------------------------------------------------------
# rule detectors (must hold on ALL pairs -> private-safe)
# --------------------------------------------------------------------------
def _detect_scale(pairs):
    for k in (2, 3, 4, 5):
        ok = True
        for p in pairs:
            I = np.array(p["input"]); O = np.array(p["output"])
            oh_, ow_ = O.shape
            up = np.repeat(np.repeat(I, k, 0), k, 1)
            if oh_ > up.shape[0] or ow_ > up.shape[1] or not np.array_equal(up[:oh_, :ow_], O):
                ok = False
                break
        if ok:
            return k
    return None


def _detect_mirror(pairs):
    """Return 'W' if output=[I|fliplr], 'H' if output=[I;flipud], else None."""
    okW = okH = True
    for p in pairs:
        I = np.array(p["input"]); O = np.array(p["output"])
        if okW:
            cat = np.hstack([I, I[:, ::-1]])
            if O.shape != cat.shape or not np.array_equal(cat, O):
                okW = False
        if okH:
            cat = np.vstack([I, I[::-1, :]])
            if O.shape != cat.shape or not np.array_equal(cat, O):
                okH = False
    if okW:
        return "W"
    if okH:
        return "H"
    return None


def _detect_quad(pairs):
    """Return op-combo tuple (tl,tr,bl,br) over {I,H,V,B} if a fixed quad
    assignment reproduces every pair, else None."""
    from itertools import product
    OPS = {
        "I": lambda a: a,
        "H": lambda a: a[:, ::-1],
        "V": lambda a: a[::-1, :],
        "B": lambda a: a[::-1, ::-1],
    }
    for combo in product("IHVB", repeat=4):
        good = True
        for p in pairs:
            I = np.array(p["input"]); O = np.array(p["output"])
            ih, iw = I.shape
            if O.shape != (2 * ih, 2 * iw):
                good = False
                break
            tl = OPS[combo[0]](I); tr = OPS[combo[1]](I)
            bl = OPS[combo[2]](I); br = OPS[combo[3]](I)
            cat = np.vstack([np.hstack([tl, tr]), np.hstack([bl, br])])
            if not np.array_equal(cat, O):
                good = False
                break
        if good:
            return combo
    return None


# --------------------------------------------------------------------------
# ONNX helpers
# --------------------------------------------------------------------------
def _i64(name, arr):
    return onh.from_array(np.array(arr, dtype=np.int64), name)


def _f32(name, arr):
    return onh.from_array(np.array(arr, dtype=np.float32), name)


def _model(nodes, inits, opset=13):
    x = oh.make_tensor_value_info("input", TP.FLOAT, GS)
    y = oh.make_tensor_value_info("output", TP.FLOAT, GS)
    g = oh.make_graph(nodes, "g", [x], [y], inits)
    m = oh.make_model(g, ir_version=10, opset_imports=[oh.make_opsetid("", opset)])
    onnx.checker.check_model(m)
    return m


# --------------------------------------------------------------------------
# builders
# --------------------------------------------------------------------------
def _build_scale_convT(k):
    """Grouped ConvTranspose, ones kernel [10,1,k,k], stride k -> nearest
    upsample. Output of ConvTranspose is k*F=k*30; we need exactly [1,10,30,30],
    so we ConvTranspose into a temp then Slice top-left 30x30. To keep "output"
    free we instead ConvTranspose to a temp and Slice -> output.
    Only intermediate is the k*30 x k*30 temp; we minimise by ConvTranspose with
    output_padding/auto crop. Simplest exact route: ConvTranspose then Slice."""
    W = np.zeros((C, 1, k, k), dtype=np.float32)
    W[:, 0, :, :] = 1.0
    nodes = [
        oh.make_node("ConvTranspose", ["input", "Wk"], ["up"],
                     strides=[k, k], group=C, kernel_shape=[k, k]),
    ]
    inits = [_f32("Wk", W)]
    # crop top-left 30x30
    inits += [_i64("ss", [0, 0]), _i64("se", [F, F]), _i64("sa", [2, 3]), _i64("st", [1, 1])]
    nodes.append(oh.make_node("Slice", ["up", "ss", "se", "sa", "st"], ["output"]))
    return _model(nodes, inits)


def _build_mirror(direction, H, W):
    """output = [I | fliplr]  (W)  or  [I ; flipud]  (H), then Pad to frame."""
    nodes = []
    inits = []
    # content block
    inits += [_i64("cs", [0, 0]), _i64("ce", [H, W]), _i64("ca", [2, 3]), _i64("ct", [1, 1])]
    nodes.append(oh.make_node("Slice", ["input", "cs", "ce", "ca", "ct"], ["blk"]))
    if direction == "W":
        # reverse along W (axis 3)
        inits += [_i64("rs", [W - 1]), _i64("re", [-W - 1]), _i64("ra", [3]), _i64("rt", [-1])]
        nodes.append(oh.make_node("Slice", ["blk", "rs", "re", "ra", "rt"], ["rev"]))
        nodes.append(oh.make_node("Concat", ["blk", "rev"], ["cat"], axis=3))
        outH, outW = H, 2 * W
    else:
        inits += [_i64("rs", [H - 1]), _i64("re", [-H - 1]), _i64("ra", [2]), _i64("rt", [-1])]
        nodes.append(oh.make_node("Slice", ["blk", "rs", "re", "ra", "rt"], ["rev"]))
        nodes.append(oh.make_node("Concat", ["blk", "rev"], ["cat"], axis=2))
        outH, outW = 2 * H, W
    pb, pr = F - outH, F - outW
    inits += [_i64("pads", [0, 0, 0, 0, 0, 0, pb, pr]), _f32("pv", 0.0)]
    nodes.append(oh.make_node("Pad", ["cat", "pads", "pv"], ["output"], mode="constant"))
    return _model(nodes, inits)


def _build_quad(combo, H, W):
    """Assemble [[tl,tr],[bl,br]] from reverse-slices, then Pad to frame."""
    nodes = []
    inits = []
    inits += [_i64("cs", [0, 0]), _i64("ce", [H, W]), _i64("ca", [2, 3]), _i64("ct", [1, 1])]
    nodes.append(oh.make_node("Slice", ["input", "cs", "ce", "ca", "ct"], ["blk"]))
    # reverse helpers
    inits += [_i64("hs", [W - 1]), _i64("he", [-W - 1]), _i64("ha", [3]), _i64("ht", [-1])]
    inits += [_i64("vs", [H - 1]), _i64("ve", [-H - 1]), _i64("va", [2]), _i64("vt", [-1])]

    have = {"I": "blk"}

    def get(op):
        if op in have:
            return have[op]
        if op == "H":
            nodes.append(oh.make_node("Slice", ["blk", "hs", "he", "ha", "ht"], ["bH"]))
            have["H"] = "bH"; return "bH"
        if op == "V":
            nodes.append(oh.make_node("Slice", ["blk", "vs", "ve", "va", "vt"], ["bV"]))
            have["V"] = "bV"; return "bV"
        if op == "B":
            src = get("V")
            nodes.append(oh.make_node("Slice", [src, "hs", "he", "ha", "ht"], ["bB"]))
            have["B"] = "bB"; return "bB"

    tl, tr, bl, br = (get(combo[0]), get(combo[1]), get(combo[2]), get(combo[3]))
    nodes.append(oh.make_node("Concat", [tl, tr], ["top"], axis=3))
    nodes.append(oh.make_node("Concat", [bl, br], ["bot"], axis=3))
    nodes.append(oh.make_node("Concat", ["top", "bot"], ["quad"], axis=2))
    pb, pr = F - 2 * H, F - 2 * W
    inits += [_i64("pads", [0, 0, 0, 0, 0, 0, pb, pr]), _f32("pv", 0.0)]
    nodes.append(oh.make_node("Pad", ["quad", "pads", "pv"], ["output"], mode="constant"))
    return _model(nodes, inits)


# --------------------------------------------------------------------------
# public entry
# --------------------------------------------------------------------------
def candidates(task_num, base_bytes):
    """Yield (label, onnx.ModelProto) candidates for symmetry/tiling/scaling
    tasks. Never raises; yields nothing if onnx missing or no family matches."""
    if onnx is None:
        return
    try:
        pairs = _task_pairs(task_num)
    except Exception:
        return
    if not pairs:
        return

    # ---- integer upscale (extent-independent: works for any single/multi shape)
    try:
        k = _detect_scale(pairs)
        if k is not None:
            yield (f"symtile.scale{k}.convT", _build_scale_convT(k))
    except Exception:
        pass

    # families below need a single fixed input shape (static anchoring)
    shp = _single_input_shape(pairs)
    if shp is None:
        return
    H, W = shp
    if H <= 0 or W <= 0:
        return

    # ---- mirror double-width / double-height
    try:
        d = _detect_mirror(pairs)
        if d is not None and (d == "W" and 2 * W <= F or d == "H" and 2 * H <= F):
            yield (f"symtile.mirror{d}", _build_mirror(d, H, W))
    except Exception:
        pass

    # ---- mirror-quad
    try:
        combo = _detect_quad(pairs)
        if combo is not None and 2 * H <= F and 2 * W <= F:
            yield ("symtile.quad." + "".join(combo), _build_quad(combo, H, W))
    except Exception:
        pass


# --------------------------------------------------------------------------
# self-validation harness
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import json, os
    from pathlib import Path
    from engine import dataio, verify

    BASE = Path(__file__).resolve().parent.parent
    res = json.load(open(BASE / "logs" / "blend_results.json"))
    GOUT = BASE / "out" / "symtile"
    os.makedirs(GOUT, exist_ok=True)

    wins = []
    total_gain = 0.0
    detected = []
    for t in range(1, 401):
        key = f"{t:03d}"
        if key not in res:
            continue
        base = res[key]
        base_cost = base["memory"] + base["params"]
        base_pts = base["points"]
        task = dataio.load_task(t)
        best = None
        for label, model in candidates(t, base_cost):
            detected.append((t, label))
            try:
                vr = verify.verify(model, task, t)
            except Exception as e:  # noqa: BLE001
                print(f"  task{t:03d} {label}: verify crashed {e}")
                continue
            if not vr["ok"]:
                continue
            cost = (vr["memory"] or 0) + (vr["params"] or 0)
            if cost < base_cost and (best is None or cost < best[1]):
                best = (label, cost, vr["points"])
        if best:
            label, cost, pts = best
            gain = pts - base_pts
            total_gain += gain
            wins.append((t, label, base_cost, cost, base_pts, pts, gain))
            for lbl2, model2 in candidates(t, base_cost):
                if lbl2 == label:
                    onnx.save(model2, str(GOUT / f"task{t:03d}.onnx"))
                    break

    print("\n=== DETECTED (family matched a task) ===")
    for t, lbl in detected:
        print(f"  task{t:03d}: {lbl}")
    print("\n=== WINS (exact AND cheaper than base) ===")
    for t, lbl, bc, nc, bp, np_, g in wins:
        print(f"  task{t:03d} {lbl}: cost {bc}->{nc}  pts {bp:.2f}->{np_:.2f}  (+{g:.2f})")
    print(f"\nsymtile: {len(wins)} wins, +{total_gain:.2f} pts over base")
