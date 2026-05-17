# Resume pointer (autonomous grind)

Mode: **pure-local grind** (local==Kaggle PROVEN, see logs/CALIB.md). No
per-task submits. Submit only the accumulated best `out/submission.zip`
(filename MUST be exactly `submission.zip`) when local projection beats the
current best real LB (5480.41). Truth = `logs/results.json`. Checkpoint
report every ~15-25 tasks. Atomic commit + push per family.

## State (2026-05-17, after LocalConvMin)
- Solved **35/400 → projected 510.5 pts** (was 463.5; +47.0 this session).
- Families: **local_conv_min x23** (~9.6–13.7, replaced ALL local_neighborhood),
  linear_local_conv x7 (095/098/127/171/283/294/317, ~18.19, 0 memory),
  color_permute x2 (22.70), color_lut x2 (20.39), fractal3_bg0 x1 (15.22).
- `local_conv_min` = same proven canvas-safe Conv→Relu→Conv1x1 skeleton as
  local_neighborhood but every channel is a logic-minimised CUBE (prime
  implicant: only the literals that fix the colour) instead of one channel
  per full window. Per-output-colour DNF cover via greedy literal dropping
  with the observed off-set as the exclusion constraint; centre literal
  always kept → canvas-safe by the same argument. Multiple same-colour
  cubes may co-fire → final Clip(0,1) collapses the routed channel back to
  an exact one-hot. Double-gated: accepted only if full ONNX cost strictly
  drops vs the exact matcher AND the official grader passes → it strictly
  dominates local_neighborhood, never a regression. Replaced all 23
  (e.g. task293 P 2738→cubes, 8.19→10.28; task073 12.32→13.71).
- local==Kaggle still PROVEN (verify.py runs neurogolf_utils verbatim;
  every accept measured ok). Clip is a new op but ran clean under the
  grader's ORT_DISABLE_ALL session — not suspect, no recalibration.
  Best prior real public LB to beat: 5480.41 (we are at 510.5 → no submit).

## Exact next action (highest leverage first)
1. **New families for the unsolved 365** — now the biggest pool (0 pts each).
   228 are same-shape but NOT a ≤5×5 local function (else already solved):
   need GLOBAL structure. Cheapest, canvas-safe-buildable first:
   - symmetry-fill / mirror-complete (reflect across h/v/diag axis, fill 0s).
   - flood-fill / enclosure (task002 class — see neurogolf_utils _TASK_ZERO).
   - object-recolor-by-shape / by-size / by-count.
   Then shape-changing 137 (2× scale, 1/3 crop, tiling, gravity) one task at
   a time with the Pad-re-embed trick (see Fractal3), official grader oracle.
2. **Squeeze local_conv_min further** (optional, lower yield): randomised /
   multi-pass literal-drop order + pick-smallest-cover; an exact set-cover
   ILP per colour would shave P' more on the big tasks (151/293/352 still
   carry the most memory). Each −ln(cost) point is monotone in P'.
3. Re-render logs each batch; commit+push; checkpoint report.

## How to resume
`python run.py render` to refresh logs from results.json. To re-solve a
family group, loop `solve.solve_one(n)` over its task ids (cheaper than a
400 sweep; colour & linear families detect before local_conv_min so no
regression; local_conv_min detects before local_neighborhood). Always gate
acceptance on `verify.verify` (official grader). New family → add to
engine/families.py REGISTRY ordered by est_points, with a pure-python
apply() for the quick pre-filter.
