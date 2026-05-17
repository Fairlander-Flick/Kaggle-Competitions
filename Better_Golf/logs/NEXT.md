# Resume pointer (autonomous grind)

Mode: **pure-local grind** (local==Kaggle PROVEN, see logs/CALIB.md). No
per-task submits. Submit only the accumulated best `out/submission.zip`
(filename MUST be exactly `submission.zip`) when local projection beats the
current best real LB (5480.41). Truth = `logs/results.json`. Checkpoint
report every ~15-25 tasks. Atomic commit + push per family.

Working style: Architect designs each new family's canvas-safe construction
+ gates acceptance on the official grader; grunt impl/verify is dispatched to
a Sonnet subagent with an exact ONNX recipe (saves tokens, no quality loss —
subagent output is independently re-verified via engine.verify before accept).

## State (2026-05-17, after GlobalGeom)
- Solved **42/400 → projected 631.72 pts** (was 510.5; +121.22 this session).
- Trajectory (real, monotone, every family double-gated): 418.5 → 463.5 →
  510.5 → **631.7**. local==Kaggle re-confirmed by independent re-run of the
  official grader path on task179/150/87 (byte-identical points).
- Families: local_conv_min x23 (~9.6–13.7), linear_local_conv x7 (~18.19),
  **global_geom x7 NEW**, color_permute x2 (22.70), color_lut x2 (20.39),
  fractal3_bg0 x1 (15.22).
- **global_geom** = canvas-safe geometric transforms via TRIAGE.md bucket:
  - **transpose** (task179, task241): single `Transpose` perm[0,1,3,2],
    canvas-safe (H×W grid → W×H still top-left, padding stays zero), NO
    intermediates/consts → **memory 0, params 0 → 25.000 pts each** (the
    only full-25 tasks we have; triage's 22 ceiling was wrong, transpose
    is free).
  - flip_h (150) / flip_v (155): one data-dependent permutation matrix
    built from runtime occupancy (ReduceSum/Max → W or H → A[k,c]=k+c,
    Equal(A,W-1) ∧ k<W) then MatMul on the spatial axis → 14.93 each.
  - rot90 (380) = flip_rows(Transpose(x)) → 14.01.
  - rot180 (87,140) = flip_cols then flip_rows (2 perm matrices) → 13.67.
  - All tensors fully static-shaped (data-dependent VALUES, fixed SHAPES)
    so the grader's strict shape_inference passes; ran clean under
    ORT_DISABLE_ALL. New ops (Transpose/ReduceSum/ReduceMax/Squeeze/
    Unsqueeze/Add/Sub/Cast/Equal/Less/Mul/MatMul) all measured ok — geom
    is an EXACT construction double-gated by the official grader, not a
    statistical fit; no recalibration needed.
- Best prior real public LB to beat: 5480.41 (we are at 631.7 → no submit).

## Exact next action (highest leverage first)
1. **Next cheap canvas-safe buckets from logs/TRIAGE.md** (each Architect-
   designs construction → Sonnet impls → grader-gate):
   - **crop_bbox x1** (task31, ~20 ceiling): data-dependent crop+re-embed —
     reuse the geom occupancy→permutation-matmul trick (select rows/cols of
     the non-zero bbox, MatMul-gather to top-left). Highest est per task.
   - **symmetry_fill x2** (113, 385, axis h, ~18): out = in with zero cells
     filled by horizontal reflection — canvas-safe per-cell `max(in, flip_v
     compaction of in)`; the flip_v primitive already exists in GlobalGeom.
   - **int_scale x2** (223 3×, 307) + **tiling x1** (249), ~16: shape-
     changing → Fractal3-style Pad/Tile re-embed, one task at a time.
   - **Sub-group I x7** (83,106,108,142,152,194,327): 2× non-uniform
     upscale — output[2r..2r+1,2c..2c+1] = f(neighbourhood); needs a custom
     family, inspect ex0 first (arc-pattern-analysis skill).
2. **Then the mass: Sub-group A x111** (shape-eq, same palette, spatially
   conditional — flood-fill / connectivity / object ops). These are NOT
   ≤5×5-local (else local_conv_min/local_neighborhood already caught them),
   so they need GLOBAL structure. Pick a recurring sub-pattern (e.g.
   enclosure/flood-fill — task002 _TASK_ZERO class) and build one canvas-
   safe family that clears many at once; arc-pattern-analysis per cluster.
3. **Optional, low yield:** squeeze global_geom flip/rot cost — rot180 (2
   perm, 83KB mem, 13.67) and flip (23KB) carry [1,1,30,30]/[30,30]
   intermediates; reuse ch_sum once / fewer temps / narrower dtype where
   legal → +1–2 pts ×5 tasks. Deep in the log tail; do only when bigger
   pools are exhausted.

## How to resume
`python run.py render` to refresh logs from results.json. Read
logs/TRIAGE.md for the full unsolved-task buckets + task-id lists. Per new
family: Architect writes the exact canvas-safe ONNX recipe → dispatch a
Sonnet subagent to implement in engine/families.py (insert into REGISTRY
ordered by est_points; exact detect so no regression) and run
`python run.py solve <n>` per task → Architect independently re-runs
engine.verify on a sample to confirm before accepting → commit+push per
family → checkpoint report. Acceptance gate is ALWAYS the official grader
(verify.verify, n_fail==0 over train+test+arc-gen, measurable).
