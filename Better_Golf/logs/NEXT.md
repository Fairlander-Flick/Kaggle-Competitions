# Resume pointer (autonomous grind) — FINAL PROTOCOL (user-locked 2026-05-17)

Mode: **pure-local grind** (local==Kaggle PROVEN, logs/CALIB.md). No per-task
submits. Submit accumulated best `out/submission.zip` (name MUST be exactly
that) only when local projection beats best real LB (5480.41). Truth =
`logs/results.json`. Architect does ALL reasoning (analysis + canvas-safe
ONNX design + golf + debug + acceptance) — NEVER delegate to a subagent
(memory delegation-no-reasoning-to-subagents). NO internet/known-algorithm
search (user removed it 2026-05-17).

## Goal
Competition score floor **7000** (avg 17.5/400), stretch **7200** (18.0).
Cost model (memory neurogolf-cost-model): `points=25−ln(memory+params)`,
memory = Σ every intermediate tensor's bytes, `input`/`output` exempt.
Coverage-only caps ~5400 → compaction is mandatory, golf-as-you-go.

## Per-task good-enough (the stop rule)
`G(task) = min(18.0, p_max(task) − 1.0)` where `p_max` = Architect-computed
theoretical ceiling from the rule-class's mandatory-intermediate cost floor
(compute BEFORE constructing). Golf until `pts ≥ G`, then **STOP** (never
chase G→25 on a solo task; only family-template lifts that raise N members
are always taken). Self-balances: naturally-cheap tasks (identity/transpose/
recolor ~22-25) subsidize ceiling-capped ones. Every checkpoint report
running **Σp_max projection**; if < 7200 → structural alarm → paradigm-shift
that family's construction, not blind grind.

## Stuck budget (unit = a distinct verified/disproven skeleton, not a tweak)
- Coverage (0→solved): ≤ **3** distinct canvas-safe constructions. Fail →
  `deferred + reason`, revisit pass-2.
- Golf (solved→G): ≤ **3** measured golf iterations on the FAMILY TEMPLATE
  (amortized over members). Still < G → accept best, flag `golf-capped`,
  move on; revisit only via a later family-template multiplier.
- Max **2 full passes** (pass-2 = deferred + golf-capped w/ cross-family
  insight), then submit best.

## Work order (ordered, family-templated)
Process by ascending task index, BUT when you reach a task resolve its
WHOLE family/template at once: compute p_max → construct/golf the template
once (≤3+3) → apply template to ALL its members wherever they currently sit
(0 or fat-solved) → per-member official grader + independent fresh
engine.verify + atomic commit + one-line report + **next-step prompt**.
Full regression sweep per family-batch (not per task: a single change can
only regress via REGISTRY-shadow, provable by inspection). Already-solved
fat tasks (local_conv_min x40 @11.5, etc.) are NOT a separate phase — they
are the golf branch of this same ordered pass.

## State (2026-05-17, pass-1: flood_fill family done)
**77/400 solved, projected 1039.14 pts**, avg/solved 13.49.
- flood_fill family RESOLVED (N=2): task002 fill=4 K=25 → **12.573**
  (mem 248504, p 923); task251 fill=1 K=14 → **12.955** (mem 169304,
  p 923). Both: 1 coverage construction, 0 golf (first build ≥ G).
- p_max(flood, honest Conv-flood floor) ≈ 12.7/13.0 → G ≈ 11.7/12.0;
  both cleared on first build → stop-rule satisfied, golf skipped.
- Family Δpts = **+25.53** (0→25.53). Intrinsically ceiling-capped
  family (Conv forces float, K rounds mandatory); expected, subsidized
  by identity/geom (22-25) per self-balancing — NOT a structural alarm
  on its own (2/400).
- Regression: zero — FloodFill.detect=None on all 73 other solved
  (no REGISTRY-shadow possible, proven by code, no grader sweep needed).
- Σp_max projection: indeterminate at 19% resolved (77/400); flood is
  capped but the cheap high-pt families (identity/transpose/recolor)
  are still unresolved (ascending pass just started). Recheck at next
  family batch; 7000 floor still reachable IF bulk of 323 unsolved fall
  into cheap families + 40 fat local_conv_min get golfed. Not on a
  proven 7000 trajectory yet — depends on family mix of low indices.

### Prior baseline (pre-protocol, ref)
75/400 solved, projected 1013.61 pts. Commit 4f789a0 pushed.
Families: local_conv_min x40 (avg 11.5 — biggest+fattest, median mem 316KB,
PRIME golf target), linear_local_conv x7 (18.0), global_geom x7 (17.3 —
transpose subset → single Transpose node = 25, +~8/task), mirror_double x5
(13.3), quadrant_upscale x5 (12.0), color_permute x2 (22.7), color_lut x2
(20.4), symmetry_fill/int_scale x2, fractal3/crop_bbox/tiling x1. 325
unsolved. Reusable helpers in engine/families.py (`_idx`,`_occ_all`,
`_occ_nz`,`_flip_rows_P`,`_flip_cols_P`,`_shift_mat`); patterns
logs/FAMILY_SPEC.md; unsolved buckets logs/TRIAGE.md.

## Exact next action (pass-1 continue)
Lowest task index with `pts < G` is now **task 003** (unsolved, pts=0;
2 & 251 done). Go there: `dataio.grid_shapes` + eyeball train ex0,
identify its family/template, scan all 400 for family membership N,
compute honest `p_max` (rule-class mandatory-intermediate floor),
G=min(18, p_max−1). Budget by N (N≤2→3/2, 3≤N≤10→4/4, N>10→6/8).
Construct cheapest-correct canvas-safe ONNX, golf only until pts≥G
(ROI early-stop: Δpts×N < 1.0 → stop). Apply template to all members.
Per-member: `python run.py solve <n>` (official grader, n_fail==0) +
independent cold-reload engine.verify + atomic commit + one-line report.
Regression: prove no REGISTRY-shadow by inspection (detect=None on all
prior-solved). Update this file's State + next action at family-batch end.
