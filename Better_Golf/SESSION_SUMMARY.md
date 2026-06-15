# SESSION_SUMMARY — neurogolf-2026 (you-are-here)

_Overwritten each checkpoint. History in context.md. Read this + context.md first on resume._

## Status: NN-GOLF PHASE started (2026-06-14). Best LB still 6373.63 (~rank 265).
- competition neurogolf-2026, deadline 2026-07-15 (T-31d). Target rank 10. Quota 100/day.
- working dir `$WORK/Kaggle-Competitions/Better_Golf`. env conda `kaggle`
  (`$WORK/software/private/conda/envs/kaggle/bin/python`, torch 2.5.1+cu121).
- LB live 2026-06-14: top1 7715, top10 cutoff ~7481. our best out/submission.zip = 6373.63.

## Operator strategy (2026-06-14): per-task NN-train + cheapen, full autonomous, local-gate then submit.
But see FINDINGS — pure SGD is hitting an EXACTNESS wall (can't reach 100%-exact reliably).

## EXACT NEXT ACTION
1. Read GPU diagnostic job **1699511** (logs/dbg-1699511.out): does a GENEROUS net reach 100%-exact
   on tasks 098/222/077? This decides the method:
   - if YES (just optimization budget) -> scale nngolf on GPU via SLURM array over the 65 shallow
     tasks, cheapest-config-first, overlay on 6373 base, SUBMIT (realization test).
   - if NO (SGD can't hit literal exact) -> PIVOT: exact per-task LUT/rule CONSTRUCTOR (no SGD;
     extract the k-window rule from data, compile to compact bool/uint8 ONNX). NN-ternary-snap
     as fallback only. This is how ARC golf is actually won.
2. Either way: build cheaper EXACT graphs for shallow set -> overlay onto out/submission.best-6373.zip
   -> submit -> confirm LB realization (make-or-break: do OUR graphs realize or score 0 on private?).
3. Then attack the contextual tail (255/101/133/158…, cost 90k-360k) with compact multi-step
   constructions — that is where the +1000 to top-10 lives.

## running_jobs: NONE (all terminal).

## VERDICT (2026-06-14): NN conv-golf CANNOT beat the public base. Established by 3 experiments:
- 1699511 diag: big nets (w32-64) hit 100%-exact on GPU in 5-48s. (feasible to reproduce, yes.)
- 1699513 array (65 shallow tasks): 2 solved, **0 wins** — exact nets cost MORE than base.
- 1699617 cheap-feasibility: small/cheap nets (w2-w8) FAIL to reach exact on contextual tasks
  (max 170/266); cheapest exact is w8-w16 @ cost 47k-98k >= base 47k-58k. task098 single-conv = 910 = base (tie).
- ROOT: conv nets carry [1,W,30,30] activations (W*900*2B fp16 min) + input cast; floor ~47k for w8d1.
  Public base is already at/below the conv-net floor. top-10 (~545 B/task avg) is BELOW any conv net
  (even W=1 fp16 = 3600B) => winners use minimal SYMBOLIC graphs (free attribute-ops/GridSample/
  output-free), NOT neural nets. Confirms prior campaign's "automated levers exhausted at 6372."

## Operator decision (2026-06-14): do #1 (symbolic superopt search), run 24/7, no day-limit.

## Infra built this session (ready):
- superopt.py: per-task SAFE lossless rewriter (onnxsim+onnxoptimizer+drop-unused), grader-gated,
  keeps only cheaper-than-base. RESULT: finds NOTHING on costly tasks (255/101/2 unchanged) — base
  dtypes already narrowed. The SAFE lever is dead (confirms prior "+2.4 exhausted").
- harvest.py: overlay out/search/* onto base (re-graded, only if cheaper) -> out/submission.zip;
  --submit submits + logs logs/lb_history.json.
- nngolf.py / debug_*.py: NN route (proven can't beat base — activation-memory floor).

## THE REAL PROBLEM (all cheap automated levers now closed by experiment):
beating 6373 needs NOVEL per-task minimal SYMBOLIC graphs (data-movement+logic ops: Gather/GridSample/
Transpose/Slice/Pad/Reshape/Equal/Where — NOT dense float conv activations, NOT public blend). AND
they must capture the TRUE rule (arc-gen-exact != private-safe: prior novel hand-builds scored 0 on
private). This is genuine per-task golf R&D.

## THE 24/7 PLAN (generation + LB-confirmation):
- GENERATE cheaper-than-base candidate graphs per task (symbolic constructors per family; NN/search
  where favorable). Compute-heavy, GPU, parallel SLURM.
- CONFIRM via A/B single-task submits: base + ONE candidate task. If LB rises ~projected delta ->
  realizes (KEEP in confirmed set). If LB drops ~base task points -> private-fail (REJECT). 100/day
  quota classifies ~100 tasks/day. This is the safe way around the realization wall.
- Accumulate confirmed wins -> climbing submission.

## PRIVATE SET CONFIRMED (read from competition pages, lines 22/151/202/249):
there IS a hidden private dataset per task ("smaller number of examples, to prevent overfitting").
=> local verify (268 ex) is NECESSARY not SUFFICIENT; an overfit graph passing public can score 0 private.
BUT arc-gen has 262 true-rule examples => a graph exact on all 262+train+test is almost surely the
TRUE rule => passes private. So: prefer GENERAL/SIMPLE constructions (private-safe); A/B-confirm cheap
risky ones via single-task submit (100/day). Naive dihedral free-op win was ILLUSORY: grid is top-left
in a fixed 30x30 frame; full-frame flip moves content to bottom-right (extent problem) => flips need
data-dependent extent => not cheap. transpose works (keeps top-left square). Base is near-optimal on geom.

## THE METHOD (winning): per-task PROGRAM SEARCH over cheap-ONNX DSL (free Transpose/Cast/Identity;
tiny-param Slice/Pad/Gather/Reshape; single-channel uint8/bool index-space logic via ArgMax+Equal+Where;
Conv/GridSample/reductions), gated by local grader on all 268 ex, keep cheapest-exact < base, prefer
general forms, A/B-confirm. Massively parallel SLURM. families.py (15 ctors) = weak v1 of this.

## Infra ready: superopt.py (safe rewrite, finds ~0), harvest.py (overlay+submit+lb_history),
solve_task.py (array-safe families solve -> logs/sweep/taskNNN.json), nngolf.py (NN, can't beat base).

## sweep400 DONE: families 77/400 solved, 0 wins over base (base is well-optimized everywhere).

## ===== GOAL (operator /goal, 2026-06-15): maximize EACH task to #1, submit. Stop-hook active. =====
## WORKFLOW (operator chose, 2026-06-15): HUMAN-EYE + agent-builds. NN cheap-net search CANCELLED
## (jobs 1700124/1700137 scancelled) per operator. Operator browses GitHub TASKS_BY_SCORE.md (per-task
## current score, lowest-first) + renders/taskNNN_*.png, picks a task, tells the rule in plain words;
## the brain builds minimal ONNX -> grader-verify all 268 -> if < base cost: A/B single-task submit
## confirm -> keep realizers -> submit. Tools: inspect_task.py N, render_task.py N, render_all.py,
## harvest.py, overlay_nn.py. PNGs+index pushed to github (job b9nfacq7r). Best LB 6373.63.
## (history below; NN route confirmed can't beat base via search — human insight is the lever)
## COMPUTE-EXPLOIT RUNNING: NN-win SLURM arrays (GPU, massive budget 30000ep x16seed, small width<=8,
## fp32 head->output direct = cheap, accept only < base) on the 14 NN-winnable SHALLOW tasks (window-learnable, base>15k):
##   array 1700124 (13 tasks, base>30k: 77 208 243 222 97 193 162 192 4 70 265 278 359) + 1700137 (task293).
## Waiter be7nq1x4k -> reports wins (out/search/*.onnx). THEN: harvest.py overlay -> A/B single-task submit
## confirm -> keep realizers -> submit climbing submission.zip. Per-task agents were too token-heavy (76k/0win) -> dropped.
## Non-local mid/tail tasks (250+57): NN can't beat base; need OPERATOR human insight (inspect_task.py N) or new ctors.
## Realistic: NN wins are modest (+0.5-2/task on a few) due to activation floor; big gains need human per-task insight.
##
## (superseded) earlier per-task-agent orchestration:
## Queue: queue.txt (400 tasks, costliest-first). Claim markers: logs/claimed/NNN (touch when launched).
## Win = out/search/taskNNN.onnx (verify-ok AND cheaper than base). Per-task agent prompt: AGENT_TASK_PROMPT.md.
## Launch cmd (minimal): Agent(general-purpose, bg): "Read AGENT_TASK_PROMPT.md, golf task N, save out/search/taskN.onnx if win, report".
## PROTOCOL on each agent completion: (1) note win/no-win; (2) while in-flight<2: NEXT=first task in
##   queue.txt with no logs/claimed/NNN -> touch marker -> launch agent; (3) every ~15 new wins OR daily:
##   run `python harvest.py` then A/B-confirm cheap risky wins via single-task submit, keep realizers.
## In-flight now: batchA agent (a75d9b0b8f0b82a62, tasks 255 158 367 18 366 29 54 208 209 36 25 175,
##   their markers pre-claimed) + task101 agent (a9b9a0ff27c198f57). = 2 concurrent.
## A/B confirm: build base + ONE candidate task -> submit -> LB up ~delta = KEEP, down ~base_pts = REJECT.
## Best LB 6373.63 (out/submission.zip = base, unchanged). Honest: each verified+confirmed win climbs us;
## tail tasks (95-649 node base) are hard to beat; mid tasks more promising. Top-10 uncertain but in play.

## Hard findings this session
- 65 tasks shallow (k=3/5 window) learnable (corrected after a buggy first scan). Max ~+70 if all
  lifted to ~18pts. Cheap guaranteed wins but SMALL.
- The +1000 to top-10 is the CONTEXTUAL tail (flood-fill/object/counting), genuinely non-local.
- SGD exact-match is hard + slow (9min/task CPU, failed even task098 whose base=910=single conv).
  => exact construction, not gradient training, is likely the right tool.
- Cost model nailed: memory=Σ intermediate bytes (input/output FREE, narrow dtype wins), params=Σ
  init+Constant elems, ALL shapes static or DQ. Optimal window form = single kxk conv->output (mem 0).

## Artifacts / files (NEW this session)
- nngolf.py (per-task NN-golf harness: train->compact ONNX export->official verify).
- debug_exact.py + jobs/debug_exact.sbatch (the diagnostic).
- out/submission.best-6373.zip = current 6373 base (overlay target). out/submission.zip = same.

## DO-NOT-REDO
- Step0 intel, data+grader env, 6372/6373 baselines locked, blend exhausted, geometric/color scans
  negative, cost map (logs/vyank_costmap.json). Public bundle blend is DEAD (converged).
