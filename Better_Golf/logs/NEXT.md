# Resume pointer (autonomous grind)

Mode: **pure-local grind** (local==Kaggle PROVEN, see logs/CALIB.md). No
per-task submits. Submit only the accumulated best `out/submission.zip`
(filename MUST be exactly `submission.zip`) when local projection beats the
current best real LB (5480.41). Truth = `logs/results.json`. Checkpoint
report every ~15-25 tasks. Atomic commit + push per family.

## State (2026-05-16, after LinearLocalConv)
- Solved **35/400 → projected 463.5 pts** (was 418.5; +44.9 this session).
- Families: local_neighborhood x23 (avg ~10, non-linearly-separable),
  **linear_local_conv x7** (095/098/127/171/283/294/317, ~18.19, 0 memory),
  color_permute x2 (22.70), color_lut x2 (20.39), fractal3_bg0 x1 (15.22).
- `linear_local_conv` = ONE Conv[10,10,K,K]+bias, sole output named
  `output` → memory 0, params=10·10·K²+10 (910 @ K=3 → 18.19 pts). Fitted
  by 10 one-vs-rest unit-margin perceptrons over EVERY 30×30 canvas cell
  of every train+test+arc-gen grid; canvas-safe via bias≤-1 on no-colour.
  Falls back to local_neighborhood when not linearly separable → no regression.
- Calibration proven earlier (task171 isolated Kaggle 13.90 == local). No
  more calibration submits. Best prior real public LB to beat: 5480.41.

## Exact next action (highest leverage first)
1. **Small-hidden MLP for the 23 non-separable local_neighborhood tasks.**
   They score ~8-12 because the pattern-matcher carries two huge
   `[1,P,30,30]` intermediates. Replace with the SMALLEST
   `Conv(K)->Relu->Conv(1x1)->output` whose hidden channel count H is the
   true rule's complexity (search/grow H from 1; train hidden by
   perceptron-on-residual or random-feature + linear top). Intermediate
   cost 2·H·900·4 → H=4 ≈ 14.7 pts vs current ~10. Yield ≈ 23 × +~4 ≈ +90.
   Cheaper still: try per-output-colour logic minimisation (espresso /
   greedy prime-implicant set cover with unobserved windows as don't-cares)
   to shrink P drastically in the existing 2-Conv structure.
2. **New families for the unsolved 365** (0 pts each — biggest total pool):
   flood-fill / enclosure (task002 class — see neurogolf_utils _TASK_ZERO),
   symmetry-fill, object-recolor-by-shape; then shape-changing (2× scale,
   1/3 crop, tiling, gravity) one task at a time, official grader as oracle,
   atomic commit per family.
3. Re-render logs each batch; commit+push; checkpoint report.

## How to resume
`python run.py render` to refresh logs from results.json. Re-solve a
family group by looping `solve.solve_one(n)` over its task ids (cheaper
than a 400 sweep; colour families detect before linear_local_conv so no
regression). Always gate acceptance on `verify.verify` (official grader).
