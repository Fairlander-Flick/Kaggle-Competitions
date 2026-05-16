# Resume pointer (autonomous grind)

Mode: autonomous grind + checkpoint report every ~15-25 tasks. Auto-submit
when projected > 5480.41 (budget 100/day, locally-verified zip only). Each
task: log + atomic commit + push. Truth = `logs/results.json`.

## State
- Solved: task001 (fractal3_bg0, 15.219), task016 (color_permute, 22.697),
  task309 (color_lut, 20.395). Foundation + 4 families shipped & pushed.
- Best prior real LB to beat: 5480.41. Target ≥ 7500.

## Landscape (measured, all 400)
- 262 same-shape; 0 pure-identity, 4 pure color-map, **258 local/spatial**.
- 138 shape-changing: ratios 2x2(15), 1/3(6), 3x3(5), 1/3.3(5), 1x2(4), ...

## Exact next action
Build the highest-yield engine: **local-neighborhood solver** for same-shape
tasks. Per task try K=1,3,5: derive an EXACT cell-wise lookup
`out[r,c] = f(input KxK window)`; require consistency across ALL
train+test+arc-gen; realize minimally in ONNX (prefer single Conv when the
fitted map is linearly separable in one-hot window space; else conv→relu→conv).
Verify with the real grader (oracle). Accept only on full pass. Then sweep
1..400, auto-submit if projection > 5480.41, atomic-commit per family.
Then attack shape-changing tail families (2x scale, 1/3 crop, tiling, ...).
