# SESSION_SUMMARY — neurogolf-2026 (you-are-here)

_Overwritten each checkpoint. History in context.md. Read this + context.md first on resume._

## Status: Phase 1 DONE. New best LB = 6372.58 (rank ~265/1893). Building Phase 2 (lossless memory minimizer).
- **competition:** neurogolf-2026. Deadline 2026-07-15 (T-32d). Target rank 10 (public LB).
- **working dir:** `$WORK/Kaggle-Competitions/Better_Golf`. env: conda `kaggle` (`$WORK/software/private/conda/envs/kaggle/bin/python`); grader onnx==1.21.0/ort==1.24.4/onnx-tool==1.0.1.
- **current best submission on LB:** vyanktesh 6372-58 flat verbatim = **6372.58** (= out/submission.zip and out/submission.best-6372.zip).

## EXACT NEXT ACTION
Build the **Phase-2 lossless memory minimizer** (the safe climb). Start from the vyanktesh 6372 base; for every task graph apply PROVABLY-lossless rewrites that shrink intermediate-tensor memory:
- dtype-narrow intermediates (float32 -> uint8/bool where value range allows, semantics identical),
- octaviograu fusions: ReduceSum/ReduceMax-chain fusion, Cast-chain collapse, bool-reduction dtype narrowing,
- constant-fold, drop unused initializers/value_info.
Reuse `fusion_rewrite.py` + study seddik graph-surgeon / souldrive lossless-optimizer in sources/. Accept a rewrite ONLY if real-oracle cost strictly lower AND n_fail==0 on all arc-gen AND transform is semantics-preserving (lossless => private-safe). Verify via SLURM (see jobs/blend.sbatch pattern). Then package + submit when projected beats 6372.58.

## running_jobs
- (none active) — blend job 1698133 COMPLETED.

## Submission budget: 2/5 used today (blend 6191.85, vyanktesh 6372.58). 3 left. Reset daily. 2 final picks at deadline.

## Key facts / decisions
- Best public ceiling = 6372 (bundles converged, forks of one lineage; cross-blend gains ~0 and is private-UNSAFE).
- **Top-10 (7467) = +1095 over public** = top teams' private LOSSLESS memory minimization (avg cost 560 vs public 8700). Cost is MEMORY-dominated; 258 tasks sit at 14-17 pts (mem 85k-190k) — the bulk of the headroom.
- Headroom: lift<17->17=+603(top50); <18->18=+920(top20); <20->20=+1656(>top10).
- LOSSLESS rewrites preserve exact computation => pass private iff base does => the ONE safe lever. Greedy bundle-swapping is private-unsafe (proven: blend 6379 proj -> 6192 actual).
- Submitted file MUST be named exactly `submission.zip` (else 400 Bad Request).

## DO-NOT-REDO
- Step 0 intel done; data + grader env built; 16 public sources fetched (sources/); cost map in logs/blend_results.json.
- Phase-1 blend ran (job 1698133, proj 6379 / actual 6192). vyanktesh 6372 = validated baseline.

## Artifacts
- out/submission.zip = best 6372. out/submission.best-6372.zip, .vyanktesh-6372.zip, .blend-6379.zip (backups).
- sources/*/ = fetched bundles. logs/blend_results.json = per-task cost map. context.md = invariants+lb_history.
