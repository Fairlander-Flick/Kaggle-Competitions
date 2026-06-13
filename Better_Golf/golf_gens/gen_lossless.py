"""Lossless ONNX-golf candidate generator for NeuroGolf-2026.

Exposes `candidates(task_num, base_bytes)` -> yields (label, onnx.ModelProto)
that compute the IDENTICAL function as the base submission graph but cost less
(memory + params). The driver (golf2.py) oracle-gates every candidate with the
official verifier, so we OVER-GENERATE safe rewrites and let the oracle pick.

Scoring facts this module exploits (from neurogolf_utils.calculate_*):
  * memory = sum over INTERMEDIATE tensors of (num_elements * dtype.itemsize),
    where the dtype comes from onnx.shape_inference and the runtime-profiled
    size is multiplied by the SAME itemsize.  => NARROWING an intermediate
    tensor's dtype (FLOAT->FLOAT16, INT64->INT32, anything->BOOL/INT8) directly
    cuts its byte cost.  `input`/`output` tensors are FREE.
  * params = element COUNT of every initializer + Constant value (dtype-blind).
    => only REMOVING initializers / Constant elements, or FOLDING a subgraph
    into a smaller initializer, reduces params.

Techniques (each a separate, independently-gated candidate):
  1. onnxoptimizer.optimize with several aggressive pass lists.
  2. onnxsim.simplify (constant folding + shape fold), a few configs.
  3. Dead-initializer / dead-Constant / dead-value_info elimination.
  4. Duplicate-initializer merge.
  5. Constant-fold initializer-only subgraphs into single initializers.
  6. CUSTOM intermediate dtype narrowing:
       a. narrow the `to` of Cast nodes whose output feeds only narrow-tolerant
          consumers, to the smallest dtype that preserves exact values;
       b. clear stored value_info so shape-inference re-derives the (now narrower)
          dtypes -- shape inference is what the grader uses for memory.

Everything is wrapped in try/except: on any failure we simply yield fewer
candidates and never raise into the driver.
"""
from __future__ import annotations

import itertools
from typing import Iterator, List, Tuple

import numpy as np
import onnx
from onnx import TensorProto as TP
from onnx import helper as oh
from onnx import numpy_helper as onh

IO_NAMES = {"input", "output"}

# onnx elem_type ints
T_FLOAT = 1
T_UINT8 = 2
T_INT8 = 3
T_UINT16 = 4
T_INT16 = 5
T_INT32 = 6
T_INT64 = 7
T_BOOL = 9
T_FLOAT16 = 10
T_DOUBLE = 11
T_UINT32 = 12
T_UINT64 = 13

# Ops whose output is intrinsically boolean (0/1) regardless of input dtype.
_BOOL_PRODUCERS = {
    "Greater", "Less", "Equal", "GreaterOrEqual", "LessOrEqual",
    "And", "Or", "Not", "Xor",
}


def _clone(m: onnx.ModelProto) -> onnx.ModelProto:
    c = onnx.ModelProto()
    c.CopyFrom(m)
    return c


def _check(m: onnx.ModelProto) -> bool:
    """Strict structural check that the model is well-formed (cheap pre-filter
    before the expensive oracle verify). Returns False on any problem."""
    try:
        onnx.checker.check_model(m, full_check=True)
        return True
    except Exception:
        return False


def _strip_value_info(m: onnx.ModelProto) -> onnx.ModelProto:
    """Drop stored value_info so the grader's shape-inference re-derives dtypes.

    The grader runs infer_shapes(strict_mode=True) itself; stored value_info can
    only pin a WIDER dtype than inference would pick. Clearing it lets inference
    assign the narrowest provable dtype to each intermediate. Lossless: it never
    changes computed values, only metadata. Oracle-gated regardless."""
    c = _clone(m)
    del c.graph.value_info[:]
    return c


# ---------------------------------------------------------------------------
# 1. onnxoptimizer
# ---------------------------------------------------------------------------
_OPT_SAFE = [
    "eliminate_identity", "eliminate_nop_cast", "eliminate_nop_dropout",
    "eliminate_nop_flatten", "eliminate_nop_pad", "eliminate_nop_concat",
    "eliminate_nop_split", "eliminate_nop_expand", "eliminate_nop_transpose",
    "eliminate_nop_reshape", "eliminate_nop_with_unit",
    "eliminate_consecutive_idempotent_ops",
    "eliminate_deadend", "eliminate_unused_initializer",
    "eliminate_duplicate_initializer", "eliminate_common_subexpression",
    "fuse_consecutive_squeezes", "fuse_consecutive_unsqueezes",
    "fuse_consecutive_transposes", "fuse_consecutive_concats",
    "fuse_consecutive_slices",
]
_OPT_CONV = _OPT_SAFE + [
    "fuse_add_bias_into_conv", "fuse_matmul_add_bias_into_gemm",
    "fuse_pad_into_conv", "fuse_pad_into_pool", "fuse_bn_into_conv",
    "fuse_transpose_into_gemm", "fuse_concat_into_reshape",
    "extract_constant_to_initializer",
]


def _gen_optimizer(m: onnx.ModelProto) -> Iterator[Tuple[str, onnx.ModelProto]]:
    try:
        import onnxoptimizer
    except Exception:
        return
    avail = set(onnxoptimizer.get_available_passes())
    for label, passes in (("opt_safe", _OPT_SAFE), ("opt_conv", _OPT_CONV)):
        ps = [p for p in passes if p in avail]
        try:
            opt = onnxoptimizer.optimize(_clone(m), ps)
            yield label, opt
            # value_info-stripped variant: lets inference re-narrow dtypes
            yield label + "_vi", _strip_value_info(opt)
        except Exception:
            continue
    # full available pass set (most aggressive) — minus known-risky structural ones
    risky = {"split_init", "split_predict", "lift_lexical_references",
             "rename_input_output", "set_unique_name_for_nodes", "nop",
             "rewrite_input_dtype"}
    full = [p for p in onnxoptimizer.get_available_passes() if p not in risky]
    try:
        yield "opt_full", onnxoptimizer.optimize(_clone(m), full)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 2. onnxsim
# ---------------------------------------------------------------------------
def _gen_simplify(m: onnx.ModelProto) -> Iterator[Tuple[str, onnx.ModelProto]]:
    try:
        import onnxsim
    except Exception:
        return
    shapes = {"input": [1, 10, 30, 30]}
    for label, kw in (
        ("onnxsim", dict()),
        ("onnxsim_shaped", dict(overwrite_input_shapes=shapes)),
        ("onnxsim_nofold", dict(skip_constant_folding=True)),
    ):
        try:
            sm, ok = onnxsim.simplify(_clone(m), **kw)
            if ok:
                yield label, sm
                yield label + "_vi", _strip_value_info(sm)
        except Exception:
            continue


# ---------------------------------------------------------------------------
# 3. Dead initializer / dead value_info elimination (hand-rolled, conservative)
# ---------------------------------------------------------------------------
def _used_tensor_names(g) -> set:
    used = set()
    for n in g.node:
        used.update(i for i in n.input if i)
    return used


def _gen_prune(m: onnx.ModelProto) -> Iterator[Tuple[str, onnx.ModelProto]]:
    """Remove initializers that are never referenced by any node input, and
    value_info entries for tensors that no longer exist. Pure metadata/param
    removal — semantics-preserving by construction."""
    try:
        c = _clone(m)
        g = c.graph
        used = _used_tensor_names(g)
        keep = [init for init in g.initializer if init.name in used]
        removed = len(g.initializer) - len(keep)
        if removed > 0:
            del g.initializer[:]
            g.initializer.extend(keep)
        # prune value_info for tensors not produced by any node and not init
        produced = {o for n in g.node for o in n.output if o}
        produced |= {init.name for init in g.initializer}
        produced |= {vi.name for vi in g.input}
        kept_vi = [vi for vi in g.value_info if vi.name in produced]
        if len(kept_vi) != len(g.value_info):
            del g.value_info[:]
            g.value_info.extend(kept_vi)
        if removed > 0 or len(kept_vi) != len(m.graph.value_info):
            yield "prune_dead", c
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 4. Duplicate initializer merge
# ---------------------------------------------------------------------------
def _gen_dedup_init(m: onnx.ModelProto) -> Iterator[Tuple[str, onnx.ModelProto]]:
    """Merge byte-identical initializers into one, rewiring node inputs. Reduces
    params (element count) by the size of every removed duplicate."""
    try:
        c = _clone(m)
        g = c.graph
        by_key = {}
        canon = {}  # dup name -> canonical name
        for init in g.initializer:
            key = (init.data_type, tuple(init.dims), init.raw_data,
                   tuple(init.float_data), tuple(init.int32_data),
                   tuple(init.int64_data), tuple(init.double_data),
                   tuple(init.uint64_data))
            if key in by_key:
                canon[init.name] = by_key[key]
            else:
                by_key[key] = init.name
        if not canon:
            return
        # remove duplicates
        keep = [init for init in g.initializer if init.name not in canon]
        del g.initializer[:]
        g.initializer.extend(keep)
        # rewire node inputs
        for n in g.node:
            for i, inp in enumerate(n.input):
                if inp in canon:
                    n.input[i] = canon[inp]
        yield "dedup_init", c
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 5. Constant-fold initializer-only subgraphs into smaller initializers
# ---------------------------------------------------------------------------
def _gen_constfold(m: onnx.ModelProto) -> Iterator[Tuple[str, onnx.ModelProto]]:
    """Best-effort: onnxsim with only constant-folding does this robustly. We
    additionally provide an onnxoptimizer 'extract_constant_to_initializer' +
    fold pass already covered above. Here we yield a sim-fold focused variant
    that is most likely to shrink params (it removes Constant nodes and folds
    initializer-only Mul/Add/etc into single initializers)."""
    try:
        import onnxsim
        sm, ok = onnxsim.simplify(_clone(m), skip_shape_inference=False)
        if ok:
            yield "constfold", sm
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 6. CUSTOM intermediate dtype narrowing
# ---------------------------------------------------------------------------
# Consumers that tolerate a narrower INTEGER index/operand without changing the
# computed result. (We still oracle-gate, this is just the candidate filter.)
def _narrow_cast_outputs(m: onnx.ModelProto) -> onnx.ModelProto:
    """Narrow the `to` dtype of Cast nodes whose float output can be represented
    in FLOAT16 without loss for THIS graph's value range (one-hot ARC grids:
    values are small integers / 0-1 masks). We narrow FLOAT->FLOAT16 and
    DOUBLE->FLOAT only on Cast outputs feeding generic elementwise math; the
    oracle confirms exactness. INT64->INT32 Cast outputs are narrowed when the
    output is not consumed as a shape/indices tensor of a shape-sensitive op."""
    c = _clone(m)
    g = c.graph
    # build consumer map
    consumers = {}
    for n in g.node:
        for inp in n.input:
            consumers.setdefault(inp, []).append(n)
    changed = False
    for n in g.node:
        if n.op_type != "Cast":
            continue
        out = n.output[0]
        if out in IO_NAMES:
            continue
        to = None
        attr = None
        for a in n.attribute:
            if a.name == "to":
                to, attr = a.i, a
        if attr is None:
            continue
        cons = consumers.get(out, [])
        # never narrow if it feeds a shape/index slot of a structural op
        shape_sensitive = False
        for cn in cons:
            ot = cn.op_type
            if ot in ("Reshape", "Expand", "Tile", "ConstantOfShape", "Resize"):
                # second input (or beyond) is a shape/scale tensor
                if out in list(cn.input)[1:]:
                    shape_sensitive = True
            if ot in ("Slice",):
                if out in list(cn.input)[1:]:
                    shape_sensitive = True
            if ot in ("Gather", "GatherND", "GatherElements", "ScatterND",
                      "ScatterElements", "OneHot", "TopK", "Pad",
                      "Unsqueeze", "Squeeze", "Split"):
                # indices / axes — keep integer width to be safe
                shape_sensitive = True
        if shape_sensitive:
            continue
        new_to = None
        if to == T_DOUBLE:
            new_to = T_FLOAT
        elif to == T_FLOAT:
            new_to = T_FLOAT16
        elif to == T_INT64:
            new_to = T_INT32
        elif to == T_INT32:
            new_to = T_INT16
        if new_to is not None and new_to != to:
            attr.i = new_to
            changed = True
    if not changed:
        return None
    # strip value_info so inference recomputes downstream dtypes
    del g.value_info[:]
    return c


def _narrow_bool_casts(m: onnx.ModelProto) -> onnx.ModelProto:
    """For Cast nodes whose INPUT is a provably-boolean tensor (output of a
    bool-producing op) and whose `to` is a wide type, if the cast result is only
    consumed by ops that accept bool->... we cannot blindly retype. Instead we
    target the common pattern: Cast(bool-tensor -> FLOAT) used purely as a 0/1
    mask in arithmetic. We narrow that Cast's `to` to UINT8 (0/1 fits) when all
    consumers are elementwise math tolerant of uint8. Oracle-gated."""
    c = _clone(m)
    g = c.graph
    # which tensors are provably bool-valued
    boolish = set()
    for n in g.node:
        if n.op_type in _BOOL_PRODUCERS:
            for o in n.output:
                if o:
                    boolish.add(o)
    consumers = {}
    producer = {}
    for n in g.node:
        for o in n.output:
            if o:
                producer[o] = n
        for inp in n.input:
            consumers.setdefault(inp, []).append(n)
    # tolerant elementwise math ops where a 0/1 uint8 operand keeps exact result
    TOLERANT = {"Mul", "Add", "Sub", "Sum", "Max", "Min", "Where",
                "ReduceSum", "ReduceMax", "ReduceMin", "Equal", "Greater",
                "Less", "GreaterOrEqual", "LessOrEqual", "And", "Or", "Not",
                "Xor", "Abs", "Neg", "Sign", "Clip"}
    changed = False
    for n in g.node:
        if n.op_type != "Cast":
            continue
        src = n.input[0]
        if src not in boolish:
            continue
        out = n.output[0]
        if out in IO_NAMES:
            continue
        attr = next((a for a in n.attribute if a.name == "to"), None)
        if attr is None or attr.i in (T_UINT8, T_BOOL, T_INT8):
            continue
        cons = consumers.get(out, [])
        if not cons or any(cn.op_type not in TOLERANT for cn in cons):
            continue
        attr.i = T_UINT8
        changed = True
    if not changed:
        return None
    del g.value_info[:]
    return c


def _gen_narrow(m: onnx.ModelProto) -> Iterator[Tuple[str, onnx.ModelProto]]:
    for label, fn in (("narrow_cast", _narrow_cast_outputs),
                      ("narrow_bool", _narrow_bool_casts)):
        try:
            nm = fn(m)
            if nm is not None:
                yield label, nm
        except Exception:
            continue
    # plain value_info strip (lets the grader's own inference pick narrow dtypes
    # even with no node edits — cheap and frequently a win on its own).
    try:
        if len(m.graph.value_info) > 0:
            yield "strip_vi", _strip_value_info(m)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def candidates(task_num, base_bytes):
    """Yield (label, onnx.ModelProto) lossless rewrites of the base graph.

    The driver oracle-gates each; we over-generate. Never raises."""
    if base_bytes is None:
        return
    try:
        base = onnx.load_from_string(base_bytes)
    except Exception:
        return

    gens = (
        _gen_optimizer,
        _gen_simplify,
        _gen_prune,
        _gen_dedup_init,
        _gen_constfold,
        _gen_narrow,
    )
    seen_labels = set()
    produced = []  # collect for chaining
    for gen in gens:
        try:
            for label, mdl in gen(base):
                if mdl is None or label in seen_labels:
                    continue
                if not _check(mdl):
                    continue
                seen_labels.add(label)
                produced.append((label, mdl))
                yield label, mdl
        except Exception:
            continue

    # CHAINED candidates: apply dtype narrowing on top of an optimized graph
    # (optimizer/simplify often shrink the node set first, then narrowing the
    # remaining casts compounds the memory win). All oracle-gated.
    try:
        bases_for_chain = [m for (lbl, m) in produced
                           if lbl in ("opt_safe", "onnxsim", "opt_full",
                                      "onnxsim_shaped", "constfold")]
        for bm in bases_for_chain[:3]:
            for nlabel, nfn in (("nc", _narrow_cast_outputs),
                                ("nb", _narrow_bool_casts),
                                ("svi", _strip_value_info)):
                try:
                    nm = nfn(bm) if nfn is not _strip_value_info else _strip_value_info(bm)
                    if nm is None:
                        continue
                    lbl = f"chain_{nlabel}_{len(seen_labels)}"
                    if _check(nm):
                        seen_labels.add(lbl)
                        yield lbl, nm
                except Exception:
                    continue
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Self-validation
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    import os
    import re
    import sys
    import time
    import zipfile

    HERE = os.path.dirname(os.path.abspath(__file__))
    ROOT = os.path.dirname(HERE)
    sys.path.insert(0, ROOT)
    os.chdir(ROOT)
    from engine import dataio, verify

    def cost_of(vr):
        return (vr["memory"] or 0) + (vr["params"] or 0)

    basez = {}
    with zipfile.ZipFile(os.path.join(ROOT, "out", "submission.zip")) as zf:
        for nm in zf.namelist():
            mm = re.match(r"task(\d{3})\.onnx$", os.path.basename(nm))
            if mm:
                basez[int(mm.group(1))] = zf.read(nm)

    # Determine the ~40 highest-cost tasks. Reuse cached survey if present.
    cache = "/tmp/basecost.json"
    order = None
    if os.path.exists(cache):
        try:
            rows = json.load(open(cache))
            order = [r[0] for r in rows][:40]
        except Exception:
            order = None
    if order is None:
        # rank by file size proxy, verify top 80, take 40 by true cost
        proxy = sorted(basez, key=lambda t: len(basez[t]), reverse=True)[:80]
        rows = []
        for t in proxy:
            try:
                vr = verify.verify(onnx.load_from_string(basez[t]),
                                   dataio.load_task(t), t)
                if vr["ok"]:
                    rows.append((t, cost_of(vr)))
            except Exception:
                continue
        rows.sort(key=lambda r: -r[1])
        order = [r[0] for r in rows][:40]

    print(f"Testing {len(order)} highest-cost tasks\n")
    wins = 0
    total_gain = 0.0
    best_example = None  # (task, base_cost, new_cost, label, dpts)
    t0 = time.time()
    for t in order:
        if t not in basez:
            continue
        task = dataio.load_task(t)
        try:
            vb = verify.verify(onnx.load_from_string(basez[t]), task, t)
        except Exception:
            continue
        if not vb["ok"]:
            continue
        base_cost = cost_of(vb)
        base_pts = vb["points"]
        best = None  # (label, cost, pts)
        for label, mdl in candidates(t, basez[t]):
            try:
                vr = verify.verify(mdl, task, t)
            except Exception:
                continue
            if vr["ok"] and vr["n_fail"] == 0:
                c = cost_of(vr)
                if c < base_cost and (best is None or c < best[1]):
                    best = (label, c, vr["points"])
        if best is not None:
            wins += 1
            d = best[2] - base_pts
            total_gain += d
            print(f"WIN task{t:03d}: {best[0]:>14s} cost {base_cost:>7d}->{best[1]:>7d} "
                  f"pts {base_pts:.3f}->{best[2]:.3f} (+{d:.3f})")
            if best_example is None or (base_cost - best[1]) > (best_example[1] - best_example[2]):
                best_example = (t, base_cost, best[1], best[0], d)
        else:
            print(f"     task{t:03d}: no win (base_cost={base_cost})")
    print(f"\n=== {wins}/{len(order)} tasks improved, total +{total_gain:.3f} pts, "
          f"{round(time.time()-t0)}s ===")
    if best_example:
        print(f"Best: task{best_example[0]:03d} {best_example[1]}->{best_example[2]} "
              f"via {best_example[3]} (+{best_example[4]:.3f} pts)")
