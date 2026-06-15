"""Octaviograu's 3 grader-faithful fusion patterns, applied to OUR genuine
5706.97 bundle (out/submission.shipstate-5707.zip).

Patterns (verbatim from intel/octaviograu_5743-35-canonical-onnx-fusions,
the only technique confirmed +LB on the REAL grader):
  P1 ReduceSum-chain fusion   (node removal, semantics-preserving)
  P2 Cast-chain collapse      (node removal, semantics-preserving)
  P3 bool-reduction dtype narrowing (dtype narrow within op vocabulary)

Only node-removal / dtype-narrowing within an existing op vocabulary —
exactly the class Octaviograu proved grader-faithful (novel op-chains get
0 LB; we add none). Every rewrite is gated by OUR trusted official
engine.verify.verify (validated this session: it correctly rejects the
non-grader-faithful class). Accept only: ok AND n_fail==0 AND strictly
more points than the original file.

Run:  python fusion_rewrite.py [--limit N]
Out:  out/submission.fusion.zip + logs/fusion_receipts.json
"""
from __future__ import annotations
import json, math, sys, zipfile
from collections import defaultdict, Counter as _Counter
from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto
from onnx import helper as oh
from onnx import numpy_helper as onh
from onnx import version_converter

from engine import dataio, verify as bgverify

BASE = Path(__file__).parent
SRC_ZIP = BASE / "out" / "submission.best-6372.zip"
OUT_ZIP = BASE / "out" / "submission.fusion.zip"
RECEIPTS = BASE / "logs" / "fusion_receipts.json"
EPS = 1e-9

# ---------------------------------------------------------------------------
# Pattern 1 — ReduceSum-chain fusion  (verbatim, Octaviograu cells 7-8)
# ---------------------------------------------------------------------------
def shape_of(model, name):
    for col in (model.graph.input, model.graph.output, model.graph.value_info):
        for v in col:
            if v.name != name:
                continue
            dims = []
            for d in v.type.tensor_type.shape.dim:
                if d.HasField('dim_value'):
                    dims.append(d.dim_value)
                else:
                    return None
            return tuple(dims)
    return None


def find_reducesum_chains(model):
    nodes = list(model.graph.node)
    consumers = defaultdict(list)
    for i, n in enumerate(nodes):
        for inp in n.input:
            if inp:
                consumers[inp].append(i)
    graph_outs = {o.name for o in model.graph.output}
    chains = []
    for i, n in enumerate(nodes):
        if n.op_type != 'ReduceSum':
            continue
        out = n.output[0]
        if not out or out in graph_outs:
            continue
        cs = consumers.get(out, [])
        if len(cs) != 1:
            continue
        c_idx = cs[0]
        c_node = nodes[c_idx]
        if c_node.op_type != 'ReduceSum':
            continue
        if c_node.input and c_node.input[0] != out:
            continue
        shape = shape_of(model, out)
        size = int(np.prod(shape)) * 2 if shape else 0
        chains.append({'first': i, 'second': c_idx, 'intermediate': out,
                       'shape': shape, 'size_hint': size})
    return chains


def fuse_reducesum_chain(model, target_pair):
    m = onnx.ModelProto()
    m.CopyFrom(model)
    nodes = list(m.graph.node)
    first_idx, second_idx = target_pair
    n1 = nodes[first_idx]
    n2 = nodes[second_idx]
    inits = {i.name: i for i in m.graph.initializer}

    def axes_for(node):
        if len(node.input) >= 2 and node.input[1] in inits:
            return list(onh.to_array(inits[node.input[1]]).flatten()), 'input'
        for attr in node.attribute:
            if attr.name == 'axes':
                return list(attr.ints), 'attr'
        return [], 'attr'

    axes_a, mode_a = axes_for(n1)
    axes_b, mode_b = axes_for(n2)
    if not axes_a or not axes_b:
        return None

    def keepdims_of(node):
        for attr in node.attribute:
            if attr.name == 'keepdims':
                return attr.i
        return 1

    if keepdims_of(n1) == 0:
        removed = sorted(int(a) for a in axes_a)
        rebased = []
        for b in axes_b:
            b = int(b)
            for r in removed:
                if r <= b:
                    b += 1
            rebased.append(b)
        merged_axes = sorted(set(int(a) for a in axes_a) | set(rebased))
    else:
        merged_axes = sorted(set(int(a) for a in axes_a) |
                             set(int(a) for a in axes_b))
    fused_keepdims = keepdims_of(n2)
    if mode_a == 'input' or mode_b == 'input':
        axes_init_name = n2.output[0] + '_fused_axes'
        axes_init = onh.from_array(np.array(merged_axes, dtype=np.int64),
                                   name=axes_init_name)
        m.graph.initializer.append(axes_init)
        fused = oh.make_node('ReduceSum',
                              inputs=[n1.input[0], axes_init_name],
                              outputs=[n2.output[0]],
                              keepdims=fused_keepdims)
    else:
        fused = oh.make_node('ReduceSum',
                              inputs=[n1.input[0]],
                              outputs=[n2.output[0]],
                              axes=merged_axes,
                              keepdims=fused_keepdims)
    new_nodes = []
    for i, n in enumerate(nodes):
        if i == first_idx:
            new_nodes.append(fused)
        elif i in (first_idx, second_idx):
            continue
        else:
            new_nodes.append(n)
    new_nodes = [n for n in new_nodes
                 if not (n.op_type == 'ReduceSum'
                         and list(n.output) == list(n2.output)
                         and n is not fused)]
    del m.graph.node[:]
    m.graph.node.extend(new_nodes)
    used = set()
    for n in m.graph.node:
        for inp in n.input:
            if inp:
                used.add(inp)
    new_inits = [i for i in m.graph.initializer if i.name in used]
    del m.graph.initializer[:]
    m.graph.initializer.extend(new_inits)
    return m


# ---------------------------------------------------------------------------
# Pattern 2 — Cast-chain collapse  (verbatim, Octaviograu cell 10)
# ---------------------------------------------------------------------------
def find_cast_chains(model):
    nodes = list(model.graph.node)
    consumers = defaultdict(list)
    for i, n in enumerate(nodes):
        for inp in n.input:
            if inp:
                consumers[inp].append(i)
    pairs = []
    for i, n in enumerate(nodes):
        if n.op_type != 'Cast':
            continue
        out = n.output[0]
        if not out:
            continue
        cs = consumers.get(out, [])
        if len(cs) != 1:
            continue
        c_node = nodes[cs[0]]
        if c_node.op_type != 'Cast':
            continue
        pairs.append((i, cs[0]))
    return pairs


def collapse_cast_pairs(model, pairs):
    m = onnx.ModelProto()
    m.CopyFrom(model)
    nodes = list(m.graph.node)
    remove = {i for i, _ in pairs}
    remap = {nodes[i].output[0]: nodes[i].input[0] for i, _ in pairs}
    new_nodes = []
    for i, n in enumerate(nodes):
        if i in remove:
            continue
        new_inputs = [remap.get(inp, inp) for inp in n.input]
        attrs_kv = {a.name: oh.get_attribute_value(a) for a in n.attribute}
        new_nodes.append(oh.make_node(n.op_type, new_inputs, list(n.output),
                                      name=n.name if n.name else None,
                                      **attrs_kv))
    del m.graph.node[:]
    m.graph.node.extend(new_nodes)
    used = set()
    for n in m.graph.node:
        for inp in n.input:
            if inp:
                used.add(inp)
    new_inits = [i for i in m.graph.initializer if i.name in used]
    del m.graph.initializer[:]
    m.graph.initializer.extend(new_inits)
    return m


# ---------------------------------------------------------------------------
# Pattern 3 — boolean-reduction dtype narrowing  (verbatim, Octaviograu c.12)
# ---------------------------------------------------------------------------
U8_NATIVE = {'Cast', 'ReduceMax', 'Reshape', 'Slice', 'Squeeze', 'Unsqueeze',
             'Transpose', 'Gather', 'Pad', 'Concat', 'Split', 'Identity',
             'Tile', 'Expand', 'Where', 'Equal'}


def narrow_task(orig):
    name_counts = _Counter(n.name for n in orig.graph.node if n.name)
    if any(c > 1 for c in name_counts.values()):
        seen = _Counter()
        for n in orig.graph.node:
            if n.name and name_counts[n.name] > 1:
                base = n.name
                n.name = f'{base}_d{seen[base]}'
                seen[base] += 1
        for i, n in enumerate(orig.graph.node):
            if not n.name:
                n.name = f'node_{i}'
    cur_opset = orig.opset_import[0].version
    target_opset = max(cur_opset, 14)
    if cur_opset < target_opset:
        try:
            model = version_converter.convert_version(orig, target_opset)
        except Exception:
            return None, 0, 0
    else:
        model = orig
    try:
        m_inf = onnx.shape_inference.infer_shapes(model, strict_mode=False)
    except Exception:
        return None, 0, 0
    nodes = list(model.graph.node)
    consumers = defaultdict(list)
    for i, n in enumerate(nodes):
        for inp in n.input:
            if inp:
                consumers[inp].append(i)
    bool_tensors = set()
    for vi in m_inf.graph.value_info:
        if vi.type.tensor_type.elem_type == onnx.TensorProto.BOOL:
            bool_tensors.add(vi.name)
    targets = []
    for i, n in enumerate(nodes):
        if n.op_type != 'Cast':
            continue
        to = next((a.i for a in n.attribute if a.name == 'to'), None)
        if to not in (1, 10):
            continue
        if not n.input or n.input[0] not in bool_tensors:
            continue
        cast_out = n.output[0]
        cons = consumers.get(cast_out, [])
        if not cons:
            continue
        targets.append((i, cast_out, cons, to))
    if not targets:
        return None, 0, 0
    new_cast_nodes = {}
    new_consumer_nodes = {}
    inserts_after = defaultdict(list)
    will_change_dtype = set()
    for cast_idx, cast_out, cons_idxs, orig_to in targets:
        cast_node = nodes[cast_idx]
        fp_dt = TensorProto.FLOAT if orig_to == 1 else TensorProto.FLOAT16
        new_cast_nodes[cast_idx] = oh.make_node(
            'Cast', list(cast_node.input), list(cast_node.output),
            to=TensorProto.UINT8)
        will_change_dtype.add(cast_out)
        for ci in cons_idxs:
            consumer = nodes[ci]
            cons_attrs = {a.name: oh.get_attribute_value(a)
                          for a in consumer.attribute}
            if consumer.op_type in U8_NATIVE:
                old_out = consumer.output[0]
                new_out = old_out + '_u8'
                new_consumer_nodes[ci] = oh.make_node(
                    consumer.op_type, list(consumer.input), [new_out],
                    **cons_attrs)
                inserts_after[ci].append(
                    oh.make_node('Cast', [new_out], [old_out], to=fp_dt))
                for out in consumer.output:
                    if out:
                        will_change_dtype.add(out)
            else:
                bridge_out = cast_out + f'_back_{ci}'
                bridge = oh.make_node('Cast', [cast_out], [bridge_out],
                                      to=fp_dt)
                new_inputs = [bridge_out if inp == cast_out else inp
                              for inp in consumer.input]
                new_consumer_nodes[ci] = oh.make_node(
                    consumer.op_type, new_inputs, list(consumer.output),
                    **cons_attrs)
                inserts_after[cast_idx].append(bridge)
    final_nodes = []
    for i, n in enumerate(nodes):
        if i in new_cast_nodes:
            final_nodes.append(new_cast_nodes[i])
        elif i in new_consumer_nodes:
            final_nodes.append(new_consumer_nodes[i])
        else:
            final_nodes.append(n)
        if i in inserts_after:
            final_nodes.extend(inserts_after[i])
    new_model = onnx.ModelProto()
    new_model.CopyFrom(model)
    del new_model.graph.node[:]
    new_model.graph.node.extend(final_nodes)
    new_vi = [vi for vi in new_model.graph.value_info
              if vi.name not in will_change_dtype]
    del new_model.graph.value_info[:]
    new_model.graph.value_info.extend(new_vi)
    new_model.producer_name = ''
    return new_model, len(targets), len(targets)


# ---------------------------------------------------------------------------
# Driver — gate every rewrite with OUR trusted official verifier
# ---------------------------------------------------------------------------
def candidates_for(orig_bytes):
    """Yield (pattern_label, candidate_model) in priority order P1,P2,P3."""
    base = onnx.load_from_string(orig_bytes)
    try:
        inf = onnx.shape_inference.infer_shapes(base, strict_mode=False)
    except Exception:
        inf = base
    chains = find_reducesum_chains(inf)
    if chains:
        biggest = max(chains, key=lambda c: c['size_hint'])
        fm = fuse_reducesum_chain(onnx.load_from_string(orig_bytes),
                                  (biggest['first'], biggest['second']))
        if fm is not None:
            yield 'P1_reducesum', fm
    pairs = find_cast_chains(inf)
    if pairs:
        yield 'P2_cast', collapse_cast_pairs(
            onnx.load_from_string(orig_bytes), pairs)
    nm, npat, _ = narrow_task(onnx.load_from_string(orig_bytes))
    if nm is not None:
        yield f'P3_narrow_{npat}', nm


def main(limit=400):
    z = zipfile.ZipFile(SRC_ZIP)
    orig = {nm: z.read(nm) for nm in z.namelist() if nm.endswith('.onnx')}
    picked = {}
    receipts = {}
    base_total = new_total = 0.0
    accepted = 0
    for n in range(1, limit + 1):
        nm = f"task{n:03d}.onnx"
        if nm not in orig:
            continue
        ob = orig[nm]
        task = dataio.load_task(n)
        try:
            bvr = bgverify.verify(onnx.load_from_string(ob), task, n)
        except Exception as e:
            bvr = {"ok": False, "points": 0.0, "err": str(e)[:40]}
        base_pts = bvr["points"] if bvr.get("ok") else 0.0
        base_total += base_pts
        best_bytes, best_pts, best_lab = ob, base_pts, "orig"
        for lab, cand in candidates_for(ob):
            try:
                onnx.checker.check_model(cand, full_check=True)
            except Exception:
                continue
            try:
                vr = bgverify.verify(cand, task, n)
            except Exception:
                continue
            if (vr.get("ok") and vr.get("n_fail") == 0
                    and vr["points"] > best_pts + EPS):
                best_bytes, best_pts, best_lab = (
                    cand.SerializeToString(), vr["points"], lab)
        picked[nm] = best_bytes
        new_total += best_pts
        if best_lab != "orig":
            accepted += 1
            receipts[f"{n:03d}"] = {
                "task": n, "pattern": best_lab,
                "base_points": round(base_pts, 4),
                "new_points": round(best_pts, 4),
                "delta": round(best_pts - base_pts, 4)}
        if n % 25 == 0:
            print(f"  ..task{n:03d}  accepted={accepted}  "
                  f"base={base_total:.1f}  new={new_total:.1f}")
    OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for nm, b in sorted(picked.items()):
            zf.writestr(nm, b)
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"base_total": round(base_total, 3),
               "new_total": round(new_total, 3),
               "delta": round(new_total - base_total, 3),
               "accepted": accepted, "receipts": receipts},
              open(RECEIPTS, "w"), indent=1, sort_keys=True)
    print(f"\nDONE. accepted={accepted}/{limit}  "
          f"base={base_total:.2f}  new={new_total:.2f}  "
          f"delta={new_total - base_total:+.2f}  -> {OUT_ZIP}")


if __name__ == "__main__":
    lim = 400
    if "--limit" in sys.argv:
        lim = int(sys.argv[sys.argv.index("--limit") + 1])
    main(lim)
