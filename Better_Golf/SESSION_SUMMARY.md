# SESSION_SUMMARY — neurogolf-2026 (you-are-here)

_Overwritten each checkpoint. History in context.md. Read this + context.md first on resume._

## Status: Phase 1 DONE (best LB 6372.58, rank ~265/1893). Phase 3 grind STARTED — no cheap wins found; real per-task golf is the only path.
- competition neurogolf-2026, deadline 2026-07-15 (T-32d). Target rank 10 (user confirmed FULL GRIND).
- working dir `$WORK/Kaggle-Competitions/Better_Golf`. env conda `kaggle` (`$WORK/software/private/conda/envs/kaggle/bin/python`). grader onnx==1.21.0/ort==1.24.4/onnx-tool==1.0.1.
- best on LB: vyanktesh 6372-58 flat verbatim = **6372.58** (= out/submission.zip, out/submission.best-6372.zip).

## EXACT NEXT ACTION (next session — Phase 3 real golf)
1. Build a proper per-task golf harness: `golf.py` with build-candidate + real-oracle verify + accept-if(cost↓ & n_fail==0 & true-rule) + write to out/golf/taskNNN.onnx + rebuild submission by overlaying out/golf/* on the 6372 base.
2. TEST the COMPACT-INDEX-SPACE hypothesis on ONE high-cost task end-to-end: ArgMax([1,10,30,30])→[1,1,30,30] int8 index; do transform in index space; Equal-with-color-consts → one-hot output. Verify cheaper, then SUBMIT to confirm it's grader-faithful (realizes on LB, not a 0-LB novel-op-chain). This single test decides if Phase 3 can scale.
3. If grader-faithful: industrialize index-space rewrites across the 258 tasks @14-17 + 48 @10-14. If 0-LB: fall back to per-task golf using ONLY the working-bundle op vocabulary.

## running_jobs: none.
## Submission budget: 2/5 used today (blend 6191.85, vyanktesh 6372.58). 3 left today; resets daily. 2 final picks at deadline 07-15.

## Hard-won findings (do not re-litigate)
- Public ceiling = 6372 (~rank 265). Bundles converged; cross-blend consensus-safe gain only +2.4; dtype already narrowed. AUTOMATED LEVERS EXHAUSTED.
- Greedy cheapest-valid-per-task is PRIVATE-UNSAFE (blend proj 6379 -> actual 6192). Only validated bundles / true-rule builds / lossless rewrites realize.
- NO cheap per-task wins: color-map/const/identity saturated; geometric (flip/rot) needs data-dependent extent detection (content top-left in fixed 30x30) => public cost is justified. transpose is free (top-left-preserving); flip is not.
- Submitted file MUST be named `submission.zip` (else 400).
- top-10 (7467) = +1095 = out-golfing GMs on ~250 hard tasks. Realistic interim: top-100/top-50. Honest: top-10 is a stretch.

## DO-NOT-REDO
- Step0 intel, data+grader env, 16 sources fetched, blend (job 1698133), cost map (logs/blend_results.json), 6372 baseline locked, geometric/color-map/consensus scans done & negative.

## Artifacts / repo
- out/submission.zip = 6372 base (+ .best-6372/.vyanktesh-6372/.blend-6379 backups). Committed+pushed: STATUS.md, context.md, SESSION_SUMMARY.md, jobs/blend.sbatch, fetch_sources.sh. data/ & sources/ & out/*.zip gitignored.
