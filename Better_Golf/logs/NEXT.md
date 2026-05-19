# Resume pointer — FINAL PROTOCOL v3 (STRATEGIC PIVOT 2026-05-19)

## PIVOT: this is a public-bundle-blend + grader-faithful-rewrite game
Notebook intel (Octaviograu et al.) proved hand-building ONNX is the WRONG
game: novel op-chains pass local verify but get **0 LB** on the real grader
→ that IS the ~7% projected↔actual gap. Our 77 hand-built were poisoning
the blend. Full record: `intel/INTELLIGENCE.md` + ~/.claude memories
(neurogolf-real-game-strategy / -public-bundle-leads / -projected-actual-gap).

### Done 2026-05-19 — HUNT PREMISE FALSIFIED BY DATA
- Hunted public CC0 artifacts; downloaded beicicc6645/afr6335/jsrdcht6029/
  octavia6042 to `sources/hunt/`.
- `blend.py` gained `--no-ours`. Graded-only blend = proj 6148.04.
- **Submitted beicicc6645 verbatim → real grader 1128.42** (NOT the named
  "6645.39"). Artifact-name scores are FAKE (authors' projected / cost-
  gaming `dummy_cost_scalar`). Our verifier correctly rejected 17/20
  beicicc files (nfail=0) — strictness is the MOAT, not a bug.
- Restored out/submission.zip ← shipstate (genuine best **5706.97**).
  Kaggle LB takes best submission ⇒ standing intact at 5706.97 (confirm
  on LB page). Backups: submission.shipstate-5707.zip,
  submission.gradedblend-6148.zip, submission.beicicc6645.zip.

## PLATEAU CONFIRMED (2026-05-19) — paradigm-shift required
Three experiments this session all return ~5707:
1. bundle-hunt → beicicc6645 verbatim → real **1128** (names are fake).
2. graded-only blend (`--no-ours`) → proj 6148.04 ≈ 5707 actual.
3. Octaviograu 3-pattern fusion (`fusion_rewrite.py`) → **+3.18 proj**
   (18 tasks; faithful class ≈ +3 actual). Banked to submission.zip,
   NOT submitted (no-spray: +3 ≪ ±400 noise). Lever bundle-specific &
   exhausted.

Per CLAUDE.md plateau protocol → paradigm shift. The single biggest
unexploited lever is **the ~7% projected↔actual gap itself** (proj 6149
vs actual 5707 ≈ 441 LB locked). Validated asset: our `engine.verify` is
a trustworthy faithfulness oracle; Octaviograu's exact grader-matching
oracle code is in `intel/` (cells 5/7). 

## PARADIGM A — EXECUTED, BREAKTHROUGH (2026-05-19)
Root cause LOCALIZED with hard data (`gap_diagnose.py`, oracle#1 +
static strict-DQ probe; Octaviograu ORT oracle#2 dropped — redundant +
double-profiling segfault):
- proj 6152.36 vs actual 5706.97, gap +445. **23 tasks engine.verify
  scores 13-17 but real grader 0s** = 339.6 LB = **76% of gap**.
  Flags: `noshape:20` (no static shape under strict_mode infer →
  grader calculate_memory None → 0) + `unused_init:3`.
- `gap_fix.py` (A/B, only the 23): **11 fixed** with DQ-clean valid
  swaps, 12 unfixable (8 have 0 clean candidates anywhere; 4 clean-but-
  incorrect). **dq_honest_projected = 5964.52** (realistic actual est).
- **SUBMITTED 2026-05-19 07:36** (out/submission.zip ← gapfix).
  Status PENDING; expect ≈5850–5965 (≥ +150 actual; gate cleared:
  DQ-clean ⇒ projected≈actual, real margin, A/B, no spray).
- Autonomous mandate granted ("kendin karar al, en yüksek puan").

### Next autonomous cycles
1. Read actual LB → calibrate: actual≈5964 ⇒ DQ model exact; actual≈5850
   ⇒ ~110 LB residual (Octaviograu novel-op class or cost-divergence)
   to hunt next.
2. Re-diagnose submitted bundle (bg) → next leak tier.
3. 12 unfixable (~150 LB): re-hunt FRESH public sources filtered through
   the DQ-clean gate (more sources ⇒ more clean cheapest-valid wins); or
   hand-build grader-faithful ONNX for the high-value ones (030/049/109/
   117/131/138/361/398 have zero clean candidates anywhere).
4. Loop diagnose→fix→submit, gated, until genuine plateau / budget.

---
# Resume pointer — FINAL PROTOCOL v2 (Phase-1 DONE, Phase-2 active) [SUPERSEDED]

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

## Phase-2 FAMILY #1 — neighbour-conditioned recolor (DONE 2026-05-18)
`scalar_onnx.build_neighbor_recolor(target,src,newc,conn)` BUILT + wired as
detector D3 (data-driven, self-rejecting). Construction (canvas-safe, 2
intermediates): `Conv(input,W[1,10,3,3])` W[target]center=9 ("is-target") +
W[src]ring=1 over conn offsets, zero-pad → `cnt`[1,1,30,30]f32; `Greater(
cnt,9)`→`chg`[1,1,30,30]bool; `Where(chg,NEWC[1,10,1,1],input)`→output.
Cost EXACT: mem 4500 (3600 cnt + 900 chg) + par 101 (90 W + 1 thr + 10 NEWC)
→ **16.566 pts** (Where multidir-broadcast infers static [1,10,30,30] — no
Tile needed). **Proven correct: n_fail=0 on ALL 265 arc-gen pairs for 3
independent tasks (095, 147, 352).**
- Sweep result: detector fires honestly on few — 095/147 already compiled
  ≤16.57 by public banks (no win); **only task352 WIN +0.36** (16.20→16.566,
  banked out/onnx/task352.onnx). `blend.py` → 400/400 valid,
  **projected 6149.18** (was 6148.81). Gate 6150 NOT cleared; +0.37 proj
  (~+0.34 actual) is spray → **NOT submitted** (no-spray; matches policy).
- KEY FINDING: task363/157 (the expected first targets) are **NOT** single-
  pass — ex1 row5 `5222250000→5222252222` (colour-2 crosses a `5` barrier)
  ⇒ iterative flood / enclosed-region fill. Detector returned None
  correctly (no false positive). They belong to the flood family below.

## Phase-2 LEVERAGE AUDIT (2026-05-18) — data-falsified the flood plan
Hard evidence gathered this session (all 400-task / 265-pair sweeps):
- **Plain enclosed-flood fits ONLY task002/251** (already blended 13.47/
  13.51; the flood ONNX needs K=14/25 rounds → ~12 pts, strictly WORSE →
  no win anywhere). Conditioned-flood (seed = tgt adj src, spread newc
  through tgt): only task243 (K=27 → ONNX too dear vs blend 13.88),
  task147/276 (K=0/3, already cheap in blend). **Flood port leverage ≈ 0.**
- **`arc_explanations.csv` is UNRELIABLE for arc-gen.** task363/157/070/
  102/156 — every English rule, implemented faithfully, scores **0/265**
  vs arc-gen (it describes only the 2-3 ARC-AGI train demos; arc-gen
  generalises differently). The "Phase-2 English driver" premise is dead;
  rules must be reverse-engineered purely from arc-gen data.
- The remaining sub-14 tail (363/157/070/102/156/243/366 …) are **global**
  rules (connectivity / rectangle-interior / object-move) — verified NOT
  expressible as a 3×3-window LUT. Loop/Scan banned ⇒ they need K-round
  unrolled or large object constructions ⇒ structurally expensive ⇒ the
  public banks' 12-17 pt compilations are already near the rule-class
  floor. One-off recompiles seldom beat them.
- Net: cheap-family space (identity/transpose/recolor/neighbour) is
  EXHAUSTED — banks already optimal there; neighbor_recolor yielded only
  task352 +0.36. Marginal recompiles ≈ +0.3 ea ≈ LB noise (~7% gap).

## Exact next action (strategic fork — pick before grinding)
The "cheap reusable family lifts the tail" thesis is largely falsified.
Positive-EV paths, in order:
1. **Cheap-SHAVE sweep (best systematic EV):** do NOT invent new rules —
   for each blended task try to recompile its *existing, already-correct*
   public-bank graph into the same logic with smaller dtype / fewer
   constants (float[1,10,30,30]→int8/bool intermediates, drop redundant
   initializers). Lower risk, bounded but real, broad.
2. **task366 one big gamble** (8.24, mem 18.9M — biggest single delta):
   "move non-border-touching objects to top-left". Even a crude 13-pt
   object-move recompile = +5 pts (largest available). High effort,
   uncertain feasibility (object labelling, Loop-free).
3. Accept ship-state: proj 6149 / actual ~5707, already +227 over prior
   best 5480.41. Stop optimising the tail.
Resubmit ONLY when projected ≳6150 AND beats 5480.41 with the ~7% margin.
