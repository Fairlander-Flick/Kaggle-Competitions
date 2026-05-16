# Resume pointer (autonomous grind)

Mode: **pure-local grind** (local==Kaggle PROVEN, see logs/CALIB.md). No
per-task submits. Submit only the accumulated best `out/submission.zip`
(filename MUST be exactly `submission.zip`) when local projection beats the
current best. Truth = `logs/results.json`. Checkpoint report every ~15-25
tasks. Atomic commit + push per family.

## State (2026-05-16)
- Solved **35/400 → projected 418.5 pts**. Families: local_neighborhood x30
  (avg 10.57, best task171 13.907), color_permute x2 (22.70), color_lut x2
  (20.39), fractal3_bg0 x1 (15.22).
- Calibration done: task171 isolated → Kaggle publicScore 13.90 == local
  13.907. local==Kaggle proven. No more calibration submits needed.
- Best prior real public LB to beat: 5480.41. Target ≥ 7500.

## Exact next action (pure local, no submit until projection >> current)
1. **Optimise high-P LocalNeighborhood solves**: many score ~10 because the
   generic exact-window-LUT is heavy (large P -> big intermediate tensors).
   Replace with a bespoke minimal ONNX of the true local rule (neighbor-count
   / majority / single small kernel) -> points ~10 -> ~22. Highest yield:
   30 tasks x +~12 pts ~= +360.
2. **New families for the unsolved tail (365)**: flood-fill / enclosure
   (task002 class), symmetry-fill, object-recolor-by-shape; then
   shape-changing (2x scale, 1/3 crop, tiling) one task at a time, official
   grader as oracle, atomic commit per family.
3. Re-render logs each batch; commit+push; checkpoint report.
