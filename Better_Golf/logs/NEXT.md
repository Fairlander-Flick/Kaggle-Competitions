# Resume pointer — FINAL PROTOCOL v2 (Phase-1 DONE, Phase-2 active)

## State (2026-05-18)
- **Phase-1 BASE blend SHIPPED.** 5 public banks + logic/karnak + our 77
  → official-grader cheapest-valid per task → **400/400 valid,
  projected 6148.81 pts**, `out/submission.zip` 1064 KB.
- **First real submit COMPLETE: actual 5706.97** (projected 6148.81 →
  ~92.8% realization; +226.56 vs prior best real LB 5480.41). Calibration:
  gate Phase-2 submits with the ~7% margin (memory: projected↔actual gap).
  LB rank: outside top-10 (cutoff ≈7001; field shown 6784–7426); need
  ≈+1295 actual / projected ≳7550 for top-10.
- Sources in `sources/` (gitignored, fresh-clone must refetch): ngc26,
  afr5689, vyanktesh, karnak_xse (each ~400 onnx), karnak_map (75),
  logic/submission (204) + `logic/arc_explanations.csv` = **400-task
  English rule map** (Phase-2 driver). octavia5743 & svanikkolli kernels
  had no submission.zip output (skipped).

## Cost model — EXACT (read from data/neurogolf_utils, do not re-derive)
- `points = max(1, 25 - ln(memory+params))` per task ×400.
- `memory` = Σ static byte-size of every tensor EXCEPT named `input`/`output`.
  Uses `onnx.shape_inference.infer_shapes(strict_mode=True)` — **ANY tensor
  with a non-static dim (dim_param / missing dim_value / dim<=0) → return
  None → DISQUALIFIED (0 pts)**. So data-dependent Slice/dynamic shapes
  are INVALID. Phase-2 must use only statically-shaped tensors.
- `params` = Σ element counts of all initializers + Constant values
  (scalars now unit-cost: a scalar Constant = 1 param).
- Final node's output named `output` ([1,10,30,30] float, rigid — compared
  via np.array_equal to one-hot) is **memory-free**. `input` free too.
- ⇒ Phase-2 recipe: `input(free) → small static bool/int8 intermediates
  carrying the transform → final node → output(free)`. [1,1,30,30] int8 ≈
  900 B → ~18 pts. Minimize count & dtype of intermediates. p_task ~17-18
  achievable ⇒ ~7000+ is mathematically consistent.

## Phase-2 finding (2026-05-18) — trivial detectors capped; go family
`engine/scalar_onnx.py` + `phase2.py` BUILT (committed). Data-driven
detector cascade (identity / transpose / global-recolor) is honest but
**fires on only 6/400** — the ecosystem already compiled all trivial
tasks optimally; English "recolor"/"identity" tags are noisy (rejected
correctly by data check). Net trivial gain only +3.22 (task016 +1.61,
task337 +1.61 → written to out/onnx; 276/309/179/241 tie). NOT submitting
(no-spray; gate not cleared).
**Real points = the expensive tail** the blend leaves at ~12-17 (108
tasks <14, 214 in 14-17) because public banks compile them with float
[1,10,30,30]. Ceiling math: lift all→17 ⇒ proj 6930 (~actual 6430);
→18 ⇒ 7270 (~6750); →20 ⇒ 8030 (~7450 = TOP-10).
**Highest-leverage next: reusable boolean-conv FAMILY builders** (not
one-off per task):
- morphological neighbour-conditioned recolor (Conv [1,1,3,3] kernel=9
  → ~17-20): covers task157, task363, many of the 41 adjacency/line
  tasks ("color-0 cell with neighbour of color X → color Y").
- extend existing flood_fill family (commit 9102448, task002/251) in
  scalar/boolean repr to enclosed-fill tasks: task070, task102, task156.
- skip connected-component-size tasks (330/374/169/277) — need CC
  labelling, banned-op territory; low feasibility.

## Phase-2 — DIFFERENTIAL recompile (active; the real points)
Loop, greedy on points-Δ:
1. Pick highest-cost task from `logs/blend_results.json` (lowest points).
2. Read its rule from `sources/logic/arc_explanations.csv` (strong prior,
   NOT ground truth — always re-verify vs arc-gen with official grader).
3. Build minimal scalar/boolean ONNX via `engine/scalar_onnx.py` (TO BUILD:
   helpers for one-hot→scalar decode via ArgMax/ReduceMax; static bool mask
   ops And/Or/Not/Where/CumSum/ReduceMax/Pad/Concat; re-embed→output).
4. Official-verify (`engine.verify.verify`) — accept only n_fail==0 +
   measurable. Reject loophole/dynamic (auto via strict shape inference).
5. If strictly cheaper than blend pick → swap into out/onnx/, rebuild
   submission.zip (A/B single change), else keep blend pick.
6. Commit atomically, report one line, next task.

### Phase-2 target queue (lowest points first, biggest Δ)
task366 (8.24, mem 18.9M — single biggest win), 382 (12.29), 138 (12.80),
182 (12.81), 133 (12.82), 077 (12.83), 158 (12.88), 054 (12.89),
173 (12.89), 286 (12.97), 396 (12.97), 364 (13.03) … 108 tasks <14 pts.
Points buckets now: 2×25, 12×[20-25], 64×[17-20], 214×[14-17], 108×<14.

## Submission policy
`out/submission.zip` only; submit when local projected beats current best
real LB. Budget 100/day; A/B single changes; never spray.

## Bootstrap (fresh clone — repo is code-only, data/ & sources/ gitignored)
1. `pip install onnx onnxruntime scipy numpy pandas kaggle`
2. `~/.kaggle/kaggle.json` (chmod 600)
3. `kaggle competitions download -c neurogolf-2026 -p data && cd data &&
   unzip -o neurogolf-2026.zip && cd ..` → task001..400.json + neurogolf_utils
4. Refetch Phase-1 sources (see "Sources" above) via `kaggle kernels output`
   / `kaggle datasets download` then `python blend.py`.
5. Sanity: `python -c "from engine import dataio,verify; dataio.load_task(2)"`

## Exact next action
1. Build `scalar_onnx.build_neighbor_recolor(target,src,newc,conn)` —
   Conv [1,1,3,3] ones kernel on source-colour channel → has-neighbour
   mask → Where(mask & is-target, newc, input). Data-derive (target,src,
   newc,conn∈{4,8}) per task; verify vs arc-gen. First targets: task363
   (14.10), task157 (13.71). Expect ~17-20 → +3-6 each.
2. Sweep the builder across all SS low-pts tasks; write winners to
   out/onnx/; `python blend.py` (auto-merge cheapest); when projected
   ≳6150 → submit; gate with the ~7% margin (memory: projected↔actual).
3. Then port flood_fill (commit 9102448) to scalar/bool for enclosed-fill
   (task070/102/156). Repeat the loop on the expensive tail.
