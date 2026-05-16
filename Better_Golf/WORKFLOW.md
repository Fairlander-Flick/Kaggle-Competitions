# NeuroGolf 2026 — Operating Workflow

Navigate solutions via [`logs/TASK_INDEX.md`](logs/TASK_INDEX.md). Click any
task → its analysis + how it was solved in `logs/SOLVE_LOG.md`.

## Principle

Outputs are **known** (train+test+arc-gen all in `taskNNN.json`). We do not
predict — we construct the smallest ONNX that exactly reproduces all of them,
and verify with the **official** grader locally. Local score = Kaggle score.

## Loop (one task at a time, report + log after each)

```
analyze → match/extend family → build minimal ONNX → verify (real grader,
all examples) → log + index → atomic commit → report → next task
```

- **Analyze:** shapes, colors, size ratio, locality, symmetry; read train ex0.
- **Family:** `engine/families.py`, ordered by best achievable points.
- **Extend:** new rule ⇒ add `detect/apply/build_onnx`. Cost rules:
  - one node, sole node emits `output` ⇒ 0 memory.
  - smallest constants; no implicit broadcast (`Mul/Add/Sub`) — insert `Tile`.
  - avoid banned ops; static positive dims; single graph in/out.
- **Verify:** must pass *every* train+test+arc-gen AND be measurable.
- **Log:** `solve.solve_one` rewrites `SOLVE_LOG.md`, `TASK_INDEX.md` from
  `logs/results.json` (idempotent — re-running a task never duplicates).
- **Commit:** one atomic commit per task or per new family.

## Status snapshot

- Best prior real LB (old Golf): **5480.41**. Target: **≥ 7500**, aim ~10000.
- Shipped families: `identity` (25.000), `color_permute` (22.697),
  `color_lut` (20.395) — all canvas-safe, single-node.
- Next: position/shape families (tile/fractal, flip, rotate, crop, scale,
  symmetry, gravity, object ops), each added per task with re-embedding.

## Submission

`python run.py submit "<msg>"` — gates on a locally-verified zip that beats the
best real LB; unsolved tasks omitted; budget 100/day but never sprayed.
