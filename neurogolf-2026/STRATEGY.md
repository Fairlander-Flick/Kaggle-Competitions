# NeuroGolf-2026 — Strategy & lessons from Google Code Golf 2025

_Last updated: 2026-06-15. Supersedes the old "train a CNN per task" plan, which is
abandoned: SGD-fit graphs pass local pairs but score ~0 on the hidden split (task192 cost us −14 LB)._

## TL;DR
- We mined the **gold-medal solutions of Google Code Golf 2025** — that competition uses the
  **exact same 400 ARC tasks** as NeuroGolf-2026 (`task001`=`007bbfb7`, identical ordering).
- Their golfed Python programs are the **true rule** for each task. We verified all of them locally:
  **398/400 reproduce every one of our grader's pairs** (train+test+arc-gen). The other 2 just time out.
- We now hold the ground-truth transformation for essentially every task → see [`RULES.md`](RULES.md).
- This does **not** auto-win, because ONNX-golf scores a *different* thing than code-golf (graph cost,
  not source length). But it removes the hardest part (figuring out what each task does) and tells us
  exactly which cheap ONNX construction to build.

## The two competitions, side by side
| | Google Code Golf 2025 | NeuroGolf-2026 (this) |
|--|--|--|
| Tasks | 400 ARC-AGI-1 training tasks | **same 400** |
| You submit | a Python program per task | an ONNX graph per task |
| Score/task | `max(1, 2500 − len(source))` | `max(1, 25 − ln(memory + params))` |
| Cheap = | few characters | few intermediate **bytes** + few param **elements** |
| Best trick | zlib-compress the source | keep tensors tiny + narrow dtype |

A 20-char Python rule is **not** necessarily a cheap ONNX graph: Python primitives (`zip`, `.count`,
`.index`, slicing) each expand to several ONNX ops. `task128` is a 61-byte column-gravity in Python but
needs ~30 ONNX nodes.

## Where we stand (2026-06-15)
- Our base = best public bundle (graph-surgeon), **6375** LB.
- Public notebook ceiling ≈ **6393** (everyone shares the same handful of bundles).
- Actual LB leaders: **7400–7759** — their methods are **private**. Gap to top-10 ≈ **+1100**.

## Why the leaders are ~3 pts/task ahead (the real lever)
Score is dominated by `memory = Σ bytes of every *intermediate* tensor` (input and output are FREE).
The 10-channel one-hot frame `[1,10,30,30]` is 36 000 bytes fp32 / 18 000 fp16 / 9 000 uint8.

The winning move:
1. **`ArgMax` the input one-hot → a single-channel integer label grid `[1,30,30]`** (900 bytes).
2. Do **all** task logic on that tiny label grid (uint8/bool where possible).
3. Emit the 10-channel one-hot **only as the very last op, writing straight to `output`** (FREE).
   Never materialise a `[1,10,30,30]` *intermediate*.

Our base already does some of this (fp16, `ArgMax`, `OneHot`) but **not consistently**.
Measured example — `task033`, base cost **55 112** bytes, of which **45 000** are three avoidable full
`[1,10,30,30]` intermediates. Its rule
(`[[g[A][B] or g[A%6][B%6] and g[5][0] for B in r] for A in r]`, r=range(17) — a fixed per-cell
gather/overlay) on a label grid would cut that ~10×: **14.1 → ~17–18**. Repeated over ~200 medium
tasks, this is the +1000 we need.

## Cheap ONNX families (verified)
- **Free attribute ops (opset ≤ 9): `Slice`, `Pad`, `Reshape`, `Transpose`** — shape params are
  *attributes* → **0 params**. (The old `exact_search` used opset-13 tensor-param versions, hence its
  flips looked expensive.)
- `Transpose` input→output in one op = **0 intermediates → 25 pts** (captured: task179/241).
- **Crop / constant / color-drop / per-cell recolor** → 1–2 ops; an exhaustive search showed the base
  is **already optimal** on these (e.g. task135/326 crop ties the base cost exactly).
- Honest conclusion: the easy families are done. Gains live in **medium tasks** where the rule is real
  but the graph wastes full-size intermediates (the label-grid lever).

## Plan to climb (per-task ONNX-golf campaign)
1. Take each true rule from `RULES.md`; classify the ONNX shape of its computation.
2. Rebuild it in **label-grid space**, one-hot only at the output; parameterise by fixed geometry
   (190/400 tasks have one fixed in-shape & one fixed out-shape).
3. Verify with the official grader on **all** pairs; keep only if strictly cheaper than base.
4. Run as a **SLURM array over 400 tasks**, massively parallel; merge winners into the base.

## Iron rules of this competition
- **Local == LB only for true-rule graphs.** Never submit an SGD/overfit graph.
- **Adopt the best public bundle as a floor**, then beat it per-task; never replace a good base graph
  with an unverified one.
- **Compute beats cleverness**: all 400 rules + a template library + the grader as oracle = a parallel
  search, which is exactly what the HPC cluster is for.

## Other ARC-flavoured competitions to mine (same playbook)
- **ARC Prize 2024/2025** (arcprize.org) — top solutions are DSL/program-synthesis over the same grid
  primitives; the [`top-quarks/ARC-solution`](https://github.com/top-quarks/ARC-solution) 1st-place DSL
  is a ready catalogue of grid transforms to port to label-grid ONNX.
- The SakanaAI repo's `prompt/` + `working/` show their LLM-assisted golf loop; the reusable part for us
  is the **judge-as-oracle** discipline, not the char-level tricks.
