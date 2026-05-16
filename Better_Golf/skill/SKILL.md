---
name: better-golf
description: Use for the NeuroGolf 2026 Kaggle competition. Per-task workflow that builds the smallest correct ONNX graph for each of the 400 tasks, verifies with the official grader locally, logs what/how, and submits budget-aware. Use at the start of any NeuroGolf session or when asking "what's next".
---

# Better_Golf — NeuroGolf 2026 per-task solver

Clean-room. Ignores all prior `Golf/` code. Home:
`Kaggle-Competitions/Better_Golf/`.

## The one fact that decides everything

The grader (`neurogolf_utils.verify_network`) checks the network against
**every example in `train + test + arc-gen`**, and all of them — inputs AND
outputs — are in the downloaded `taskNNN.json`. Nothing is hidden. So this is
**not prediction; it is construction**: for each task build the smallest ONNX
graph that exactly reproduces every known input→output pair. arc-gen has ~260
procedurally-generated variants of the *same rule* per task, so a memorized
constant cannot win — the **true generalizing rule is mandatory and fully
verifiable offline**. Know, never guess.

## Scoring (exact, from neurogolf_utils.py)

```
cost   = memory + params
memory = Σ static byte-size of every tensor EXCEPT those named "input"/"output"
params = Σ element counts of all initializers + Constant-node values
points = max(1, 25 - ln(max(1, memory + params)))      # per task, ×400
```

Consequences, in priority order:
1. A **one-node graph whose sole node emits the tensor named `output`** pays
   **zero memory** (input/output excluded, no intermediates) → identity-class
   tasks score the full **25**.
2. Every extra intermediate tensor pays its full static size. Every
   initializer/Constant pays its element count. `Gather` perm `[10]` → params
   10 → **22.70**. `Conv1x1` weight `[10,10,1,1]` → params 100 → **20.40**. A
   `[1,10,30,30]` constant → params 9000 → only **~15.9** (this is why the old
   `generate_exploit.py` capped low — and it also returned one constant for
   every example, so it failed train/arc-gen and scored **0**).
3. Disqualifiers (→ task scores 0): banned ops `Loop/Scan/NonZero/Unique/
   Script/Function/Compress`; non-static / non-positive dims; >1 graph
   input or output; initializer/IO name collision; subgraphs/functions/custom
   domain; tensor name containing `kernel_time`; file > 1.44 MB.

## The canvas trap

Each grid sits **top-left in a fixed 30×30 one-hot canvas**, padded with
all-zero ("no color") cells. A canvas-global op also hits the padding:
- **Per-cell / channel-only** rules (identity, recolor, per-cell LUT) are
  canvas-safe — the global op equals the per-grid transform. Already shipped.
- **Position/shape-changing** rules (flip, rotate, crop, scale, tile, gravity,
  symmetry, object moves) are **not** canvas-safe: the ONNX must recover the
  grid extent, transform, and re-embed top-left with zeros elsewhere. Each such
  family is added **one task at a time** with its own minimal construction.

## Per-task loop (the job — never shirk it)

For task N, in order, **pausing to report + log after each task**:

1. **Analyze.** `dataio.grid_shapes` + eyeball train ex0 ASCII. Same-shape?
   colors gained/lost? size ratio? local vs global? symmetry?
2. **Match a family** in `engine/families.py` (tried cheapest-correct-first).
3. **If none fits, add one.** Implement `detect`/`apply`/`build_onnx` for the
   true rule. Minimal ONNX: fewest nodes, final node → `output`, smallest
   constants, no implicit broadcast on `Mul/Add/Sub` (insert explicit `Tile`).
4. **Verify with the real grader.** `verify.verify` runs the official
   `neurogolf_utils` path verbatim. Accept only if it passes **all**
   train+test+arc-gen and is measurable. Local points == Kaggle points.
5. **Log + index.** `solve.solve_one` regenerates `logs/SOLVE_LOG.md` (what the
   task is, family used, how solved, score) and `logs/TASK_INDEX.md` (clickable
   per-task index). Single source of truth: `logs/results.json`.
6. **Commit atomically.** One commit per task / per new family, conventional
   message, pushed to the private `Kaggle-Competitions` repo.
7. **Report** one tight line to the user, then next task.

A family that fits train but fails arc-gen is **not the rule** — keep digging
(`quick_apply_check` enforces this before the ONNX verify).

## Commands

```
python run.py solve <n>          # one task: solve, verify, log, index
python run.py sweep <a> <b>      # batch; refresh logs
python run.py render             # rebuild TASK_INDEX.md / SOLVE_LOG.md
python run.py package            # out/submission.zip from solved ONNX
python run.py submit "<msg>"     # budget-aware (gates on verified gain)
```

## Submission policy

Budget 100/day, but submit only a zip whose **every** file passed the local
official verifier (projected == actual). Gate on beating best real LB
(5480.41). Unsolved tasks are omitted (scored 0 regardless). Never spray.

## Definition of done per task

`status: solved` in `results.json`, `.onnx` in `out/onnx/`, log+index
regenerated, atomic commit pushed, one-line report given. "Tedious" is never a
stop — the win is the grind across all 400.
