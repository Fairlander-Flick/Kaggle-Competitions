# NeuroGolf 2026 — CAMPAIGN STATUS (authoritative "where we left off")

_Last updated: 2026-06-13. This is the single source of truth for the campaign.
For the operating contract see context.md (invariants) + SESSION_SUMMARY.md (you-are-here)._

## The game
400 ARC-AGI tasks. Per task submit `taskNNN.onnx` that EXACTLY reproduces every
`<input,output>` pair (train+test+arc-gen **+ a private holdout**). Score per task =
`max(1, 25 − ln(memory + params))`; sum over 400 (theoretical max 10000). `memory` =
bytes of all intermediate tensors (input/output free); `params` = initializer/Constant
element counts. Static shapes mandatory; Loop/Scan/NonZero/Unique/Script/Function/Compress
banned; file ≤1.44MB; **submitted file must be named `submission.zip`**.

## Standing
| date | submission | LB | rank |
|---|---|---|---|
| 2026-05-19 | Octaviograu repro (stale) | 5743.43 | — |
| 2026-06-13 | greedy cross-blend (private-unsafe) | 6191.85 | — |
| **2026-06-13** | **vyanktesh 6372-58 flat verbatim** | **6372.58** | **~#265 / 1893** |

LB gradient (2026-06-13): top100=6570 · top50=6970 · top20=7281 · **top10=7467** · top1=7714.

## What we learned this session (the strategy)
1. **Public ceiling = 6372.** The strong June bundles (rajathrpai/vyanktesh/seddik/biohack44)
   have converged — they're forks of one lineage. Cross-blending gains ~0.
2. **Greedy "cheapest-valid-per-task" is private-UNSAFE.** It picks graphs that pass local
   arc-gen but FAIL the hidden private holdout → 0 on those tasks. Proof: our blend projected
   6379 locally but scored **6192** actual (−188). A single *validated* bundle (vyanktesh) scored
   its full 6372. ⇒ never cross-pick unvalidated cheaper graphs.
3. **Top-10 = +1095 over public**, and it's entirely **lossless memory minimization**. Top teams
   average cost ~560/task vs public ~8700/task — same logic, far smaller intermediate tensors.
4. Cost is **memory-dominated**. 258/400 tasks sit at 14–17 pts (intermediate mem 85k–190k bytes).
   Lifting them via dtype-narrowing/fusion is where the points are.
5. **LOSSLESS rewrites are the ONE safe lever beyond 6372**: dtype-narrow intermediates
   (float32→uint8/bool), fuse/eliminate big intermediates (ReduceSum-chain fusion, Cast-chain
   collapse, bool-reduction narrowing), constant-fold. They preserve the EXACT computation ⇒ pass
   private iff the base does (it does) ⇒ safe to climb. (Per octaviograu: dtype-narrowing within the
   same op vocabulary realizes 1:1 on the grader; *introducing novel op chains* gets 0 — avoid.)

## Plan
- **Phase 1 — DONE.** Re-fetched current bundles, locked 6372.58 baseline (+629 over stale).
- **Phase 2 — NOW.** Build an aggressive *provably-lossless* memory minimizer; apply to the 6372 base;
  accept per-task rewrite only if real-oracle cost↓ AND n_fail==0 AND semantics-preserving. Target ~top50→top20.
- **Phase 3.** Per-task minimal-ONNX golf on the residual cost tail → top-10.

## Run mechanics
- Engine: `engine/` (dataio·verify·solve·package) — `verify.py` == official `neurogolf_utils` grader.
- `blend.py` = cheapest-valid-per-task (use `--no-ours`); `fusion_rewrite.py` = lossless rewrites.
- Heavy 400-task verify = SLURM job (`jobs/blend.sbatch` pattern; TinyGPU `work` partition, 1 GPU, CPU work).
- Data: `data/ -> $WORK/kaggle/neurogolf-2026-run/data` (gitignored). Sources gitignored — re-fetch via `fetch_sources.sh`.
