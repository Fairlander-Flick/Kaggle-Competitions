#!/usr/bin/env python
"""Human golf inspector: show a task's rule examples + the base graph you must
beat (cost + ops + biggest intermediates) + the cost target.

Usage: inspect_task.py <task_num> [n_examples]
"""
import sys, zipfile, math, collections
sys.path.insert(0, ".")
import numpy as np, onnx
from onnx import shape_inference
from engine import dataio
from engine.verify import verify

COLORS = " 123456789"  # 0 shown as space; colors 1-9 as digits


def show(grid):
    return "\n".join("".join(COLORS[c] if 0 <= c < 10 else "?" for c in row)
                     for row in grid)


def main():
    n = int(sys.argv[1])
    ne = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    t = dataio.load_task(n)
    s = dataio.grid_shapes(t)
    print(f"==== task{n:03d} ====")
    print(f"pairs: train {s['n_train']} test {s['n_test']} arc-gen {s['n_arcgen']}")
    print(f"shapes in {s['input_shapes']} -> out {s['output_shapes']} | "
          f"same-shape {s['same_shape']}")
    print(f"colors in {s['input_colors']} -> out {s['output_colors']}")
    print(f"\n--- {ne} examples (0=space) ---")
    exs = t.get("train", []) + t.get("arc-gen", [])
    for ex in exs[:ne]:
        ig, og = ex["input"], ex["output"]
        print(f"\nINPUT ({len(ig)}x{len(ig[0])}):")
        print(show(ig))
        print(f"OUTPUT ({len(og)}x{len(og[0])}):")
        print(show(og))

    # base graph
    try:
        m = onnx.load_model_from_string(
            zipfile.ZipFile("out/submission.best-6373.zip").read(f"task{n:03d}.onnx"))
        r = verify(m, t, n)
        bc = (r["memory"] or 0) + (r["params"] or 0)
        bp = max(1, 25 - math.log(max(1, bc)))
        mi = shape_inference.infer_shapes(m, strict_mode=True)
        ops = collections.Counter(nd.op_type for nd in mi.graph.node)
        rows = []
        for vi in list(mi.graph.value_info) + list(mi.graph.output):
            tt = vi.type.tensor_type
            try:
                dt = onnx.helper.tensor_dtype_to_np_dtype(tt.elem_type)
                shp = [d.dim_value for d in tt.shape.dim]
                if vi.name != "output":
                    rows.append((int(np.prod(shp)) * np.dtype(dt).itemsize,
                                 tuple(shp), str(dt)))
            except Exception:
                pass
        rows.sort(reverse=True)
        print(f"\n--- BASE graph (must beat) ---")
        print(f"cost(mem+par)={bc}  pts={bp:.3f}  nodes={len(mi.graph.node)}")
        print(f"ops={dict(ops)}")
        print("biggest intermediates:", rows[:5])
        print(f"\n>>> TARGET: build an ONNX exact on ALL {s['n_train']+s['n_test']+s['n_arcgen']} "
              f"pairs with memory+params < {bc}  (each point needs cost below e^(25-pts)).")
    except Exception as e:
        print("base inspect failed:", e)


if __name__ == "__main__":
    main()
