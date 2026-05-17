# Resume pointer — FINAL PROTOCOL v2 (ecosystem + recompile, ALL constraints lifted 2026-05-17)

User lifted clean-room / no-internet / no-ensemble / float-one-hot.
Goal: **top-10 (~7000+)**. Empirically reachable (LB: ~8 teams 7000-7426;
top-10 cutoff ≈7000). Memory: [[neurogolf-ceiling-measured]] (my old
"unreachable" verdict REFUTED — wrong representation + ignored ecosystem),
[[neurogolf-cost-model]].

## The two root facts that define the plan
1. **Ecosystem.** Public legit `submission.zip`s are openly shared
   (afr1ste 5377/5480/5689/6225 open artifacts; jonathanchan ngc26 blend
   123v ~5554; nano-engine/imaadmahmood blenders). A blender that loads
   public sources → official-grader-validates → picks cheapest valid ONNX
   per task scores **~5200-6200 in ~1 session**. We are at 1039 only
   because we self-imposed clean-room.
2. **Representation.** Winning per-task recompiles use **boolean masks /
   scalar color IDs, Slice to the active small window (5x5..11x9), Pad
   back to 30x30** — NOT float `[1,10,30,30]` one-hot. Same rule, cost
   ~250k→~1-6k → ~17-18 pts. Our `families.py` float-one-hot caps ~12;
   that is the bottleneck, not the rules.
3. **Loophole/refresh.** Part of 7000+ is volatile grader-bug exploitation
   (constant-output banks, dynamic shapes) patched by "rule refreshes".
   Build LEGIT tiny ONNX only (refresh-durable; afr1ste: "semantic
   distillation still transfers"). Reject loophole models in validation.

## Phase 1 — BASE blend (highest ROI, do first; ~1 session)
`Better_Golf/blend.py` (this commit): for every source zip in
`Better_Golf/sources/*`, load each `taskNNN.onnx`, run the OFFICIAL
verifier (`engine.verify.verify`, n_fail==0 + measurable + not
disqualified), keep the **cheapest valid** per task, write
`out/submission.zip` + `logs/blend_results.json`. Reject anything that
fails official validation (auto-excludes loophole/dynamic/banned). Sources
to fetch (kaggle CLI, creds present):
- `kaggle kernels output jonathanchan/ngc26-constraint-smart-logic-mix-blending -p sources/ngc26`
- `kaggle kernels output afr1ste/neurogolf-6225-51-public-score-open-solution -p sources/afr6225` (find exact ref via `kaggle kernels list -s neurogolf --user afr1ste`)
- nano-engine-referenced svanikkolli datasets (`kaggle datasets download svanikkolli/secret-dataset` etc.)
- `kaggle datasets download karnakbaevarthur/logic-for-each-arc-task` (per-task rule intel for Phase 2)
Run `python blend.py`. Expect projected ~5500-6200. Then `run.py package`
already-solved-77 are inferior — blend supersedes; keep our flood_fill
ONNX as candidates too (cheapest-wins handles it).

## Phase 2 — DIFFERENTIAL recompile (the real work; many sessions)
Re-architect a NEW builder module `engine/scalar_onnx.py`: helpers to
(a) decode one-hot input → scalar `[1,1,30,30]` int grid, (b) Slice to
data-dependent active window, (c) boolean mask ops (And/Or/Not/Where/
CumSum/ReduceMax/Pad/Concat), (d) re-embed top-left → `output`. Per task:
read its rule from karnak logic dataset / public hints / self-derive,
implement minimal scalar/boolean graph, official-grader verify, compare
cost vs current blend pick; merge only if strictly cheaper (A/B). Target
the highest-cost tasks in `logs/blend_results.json` first (biggest pts/Δ).
The user's "maximize every task" strategy now genuinely sums to ~7000+
because per-task p_max in this representation is ~17-18, not ~12.

## Submission policy
`out/submission.zip` (exact name). Submit only when local projected
(sum of official points over valid picks) beats current best.
`kaggle competitions submit -c neurogolf-2026 -f out/submission.zip -m "<msg>"`.
Budget 100/day; A/B single changes, never spray.

## State (2026-05-17)
77/400 self-solved, projected 1039 (now superseded path). flood_fill family
(task002 12.57, task251 12.95) committed 9102448 — keep as blend candidates.
Triage probes (`triage_probe.py`/`triage_gen2.py`) were built on the WRONG
(float) feasibility model — informational only, not the plan. ALL reasoning
stays with Architect; subagents mechanical only ([[delegation-no-reasoning-to-subagents]]).

## Bootstrap (REQUIRED on a fresh git clone — repo excludes data/ & sources/)
The repo is code-only. Before anything runs, restore from `Better_Golf/`:
1. Python deps: `pip install onnx onnxruntime scipy numpy pandas kaggle`
2. kaggle creds at `~/.kaggle/kaggle.json` (chmod 600).
3. Competition data (task JSONs + grader):
   `kaggle competitions download -c neurogolf-2026 -p data && cd data && unzip -o neurogolf-2026.zip && cd ..`
   → must yield `data/task001.json`..`data/task400.json` + `data/neurogolf_utils/neurogolf_utils.py`.
   Sanity: `python -c "from engine import dataio,verify; dataio.load_task(2)"`
4. (memory is host-local, not in repo; NEXT.md + the prompt are self-contained.)

## Exact next action
1. Finish fetching Phase-1 sources into `Better_Golf/sources/` (jonathanchan
   ngc26 + afr1ste highest open artifact + 2-3 svanikkolli ensemble datasets).
2. `python blend.py` → official-validate → out/submission.zip + projected.
3. If projected > 1039 and clean: `kaggle competitions submit` (first real
   submission). Report projected vs LB.
4. Begin Phase 2: build `engine/scalar_onnx.py`, recompile top-cost tasks.
