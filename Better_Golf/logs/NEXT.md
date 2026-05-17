# Resume pointer (autonomous grind)

Mode: **pure-local grind** (local==Kaggle PROVEN, see logs/CALIB.md). No
per-task submits. Submit only the accumulated best `out/submission.zip`
(filename MUST be exactly `submission.zip`) when local projection beats the
current best real LB (5480.41). Truth = `logs/results.json`. Checkpoint
report every ~15-25 tasks. Atomic commit + push per family batch.

Working style: **Architect does ALL reasoning** (analysis + canvas-safe ONNX
design + debugging + acceptance) — do NOT delegate any reasoning to a Sonnet
subagent (user directive 2026-05-17; see memory delegation-no-reasoning-to-
subagents). Acceptance gate is ALWAYS the official grader (verify.verify,
n_fail==0 over train+test+arc-gen, measurable) plus an independent fresh
engine.verify re-run on a sample + a full re-solve regression sweep.

## State (2026-05-17, after 5 shape/position families)
- Solved **53/400 → projected 768.81 pts** (was 631.72; +137.09 this
  session). Trajectory (real, monotone, every family double-gated):
  418.5 → 463.5 → 510.5 → 631.7 → **768.8**.
- Regression check: re-solved ALL 42 prior tasks → **0 changes** (same
  family+points). 6 of the 11 new ONNX independently re-verified via a fresh
  engine.verify (official path), n_fail==0. local==Kaggle still holds.
- New families (all opset-10 except int_scale opset-13; all canvas-safe via
  the GlobalGeom data-dependent permutation/translation-matmul trick — fixed
  [30,30]/[.,.,30,30] shapes, data-dep VALUES; existing 8 families left
  byte-identical, REGISTRY: new ones after GlobalGeom, before conv trio):
  - **symmetry_fill x2** (113,385) ~12.78 — same-shape; bg(0) cell filled by
    vertically-mirrored cell. `flip=MatMul(flip_rows_P,in)`;
    `out=flip+(in-flip)*tile(mask)`, mask=Σ ch1..9 (real-colour ⇒ keep in).
  - **crop_bbox x1** (31) 13.37 — crop to non-bg(colour≥1) bbox. r/c min,max
    from non-bg occupancy → row-select Pr & col-select Pc → MatMul(MatMul
    (Pr,in),Pc).
  - **quadrant_upscale x5** (083,142,152 mirror; 106,194 rot) ~11.85-12.09 —
    2× block. mirror=[[A,fliplr],[flipud,rot180]], rot=[[A,rot90cw],
    [rot90ccw,rot180]]. flips reuse GlobalGeom perms; shift-right-W /
    shift-down-H translation matrices place 4 disjoint quadrants → sum =
    valid one-hot. fit() disambiguates variant over ALL pairs (train ex0
    can match both for symmetric inputs).
  - **int_scale x2** (223 k=3, 307 k=2) ~12.3-13.1 — Resize(nearest,floor,
    scale [1,1,k,k]) then Slice back to 30×30 (opset-13, Fractal3 skeleton).
  - **tiling x1** (249 1×2) ~12.78 — Σ over (p,q) of shift(in, pH, qW) via
    translation matmuls; q=0/p=0 ⇒ identity.
- Best prior real public LB to beat: 5480.41 (we are at 768.8 → no submit).

## Exact next action (highest leverage first)
1. **Sub-groups N + P (6 tasks, cheap, do FIRST):** N=116,172,210 (out 2×
   height only), P=164,231,311 (out 2× width only). These are likely a
   tiling/mirror variant of the just-built families — INSPECT ex0 each
   (arc-pattern-analysis), then EXTEND `tiling` (or a 2-pane mirror) to
   cover them. ~6 tasks ≈ +75 pts for one small family extension.
2. **Sub-group I leftovers (defer, low yield):** task327 (3×3→6×6 diagonal
   self-shift — custom convolution placement) and task108 (2× size but a
   sparse-cell COMPACTION/relocation, not a quadrant rule). 2 singletons,
   build only if a cheap construction emerges; otherwise skip for the mass.
3. **The mass — Sub-group A x111** (5,8,9,12,... shape-eq, identical
   palette, spatially conditional; NOT ≤5×5-local else conv caught them).
   Need GLOBAL structure. Cluster via arc-pattern-analysis; build ONE
   canvas-safe family per recurring pattern (enclosure / flood-fill —
   task002 _TASK_ZERO class — connectivity, object move/recolor). Highest
   total pool; tackle after the cheap N/P win.
4. **Sub-groups D/E/F/G (colour-gained marking, ~41 tasks):** same-shape,
   one new colour at structured positions — likely object/contour marking;
   a single "mark cells satisfying a local+global predicate" family may
   clear a cluster. arc-pattern-analysis per sub-group.

## How to resume
`python run.py render` to refresh logs from results.json. Read
logs/TRIAGE.md for full unsolved buckets + task-id lists; logs/FAMILY_SPEC.md
for the canvas-safe construction patterns already proven (reuse the helper
emitters in engine/families.py: `_idx`,`_occ_all`,`_occ_nz`,`_flip_rows_P`,
`_flip_cols_P`,`_shift_mat`). Per new family: Architect writes the exact
canvas-safe ONNX recipe AND implements it in engine/families.py (insert into
REGISTRY ordered by est_points; exact detect so no regression), runs
`python run.py solve <n>` per task, independently re-runs engine.verify on a
sample + a full re-solve regression sweep, then commit+push per family batch
+ checkpoint report. Do NOT delegate reasoning to subagents.
