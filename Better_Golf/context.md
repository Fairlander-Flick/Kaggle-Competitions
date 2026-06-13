---
doc: context
note: "LIVE persistent invariants for the neurogolf-2026 campaign (HPC edition).
       Created 2026-06-13 on resume of the Better_Golf engine. APPEND-ONLY below the line."
---

# context.md — neurogolf-2026 ("Better_Golf" engine)

```yaml
competition_id: neurogolf-2026
title: "The 2026 NeuroGolf Championship (IJCAI-ECAI 2026)"
modality: optimization_golf            # NOT tabular, NOT DL training.
spine: G                               # §12 Foundry golf/optimization spine — already built (Better_Golf/engine)
task: "per task: smallest CORRECT ONNX graph that reproduces every <input,output> pair"

# ── scoring (EXACT, read from data/neurogolf_utils/neurogolf_utils.py — source of truth) ──
score_per_task: "max(1.0, 25 - ln(max(1, memory + params)))"   # 400 tasks, theoretical max 10000
cost: "memory + params"
memory_def: "Σ over every intermediate tensor (NOT named input/output) of byte_size,
             = max(static_shape_inference[strict_mode] size, ORT-profiler runtime size).
             ANY non-static dim (dim_param/missing/<=0) anywhere => calculate_memory None => 0 pts (DQ)."
params_def: "Σ element counts of all initializers + sparse_initializers + Constant-node values
             (value_floats/ints/strings counted by len; scalar Constant = 1 param)."
free_tensors: "input and output (rigid [1,10,30,30] FLOAT) cost ZERO memory."
correctness: "(onnx_output > 0.0) must np.array_equal one-hot output on ALL train+test+arc-gen
              pairs AND a small PRIVATE holdout. Exact match only."
banned_ops: [Loop, Scan, NonZero, Unique, Script, Function, Compress, Sequence*]
hard_constraints: "single input + single output; no subgraphs (Graph/Graphs attrs); opset domain
                   in {'', 'ai.onnx'}; ONNX file <= 1.44 MB; no tensor/init name collisions;
                   no 'kernel_time' in names; zero-cost net => full 25 pts."

# ── measurement contract (§12.2 — this replaces CV) ──
oracle: "engine/verify.py == neurogolf_utils.score_network verbatim (same ORT profiling, same DQ).
         LOCAL official grade == Kaggle LB FOR GRADER-FAITHFUL graphs (proven by 5743 repro May'26)."
hazard_1_gamed_names: "Public bundles named '6645'/'6335' etc. can be COST-GAMED FAKES → 1128 / ERROR
                        on the real grader. ALWAYS official-verify every candidate; never trust the name."
hazard_2_novel_opchain: "HAND-BUILT novel ONNX op-chains pass local verify but score ~0 on the real
                          grader (the projected↔actual gap). Only grader-faithful REWRITES of existing
                          public graphs (node removal / dtype narrowing within same op vocab) realize 1:1.
                          => blend uses --no-ours (graded public graphs only) as the trustworthy base."
accept_rule: "blend = cheapest-VALID-per-task across all sources, official-verified cheapest-first.
              A rewrite/graft accepted ONLY if official local cost strictly lower AND n_fail==0 AND measurable.
              Submit only when local projected beats current best ACTUAL LB (LB is the only truth)."

# ── HPC execution environment ──
cluster: tinygpu
slurm_suffix: ".tinygpu"
compute_note: "CPU-ONLY work (ONNX build/verify/grade). Embarrassingly parallel across 400 tasks.
               Frontend OK for blend/package (~minutes). Heavy 400-task official verify => SLURM
               array on CPU cores of a 'work'-partition GPU job (TinyGPU rejects CPU-only jobs),
               or just run on frontend if < a few min. NO GPU needed."
campaign_dir_runstate: "$WORK/kaggle/neurogolf-2026-run"   # skill scaffold (data/, logs/, _pages_raw)
working_repo_dir: "$WORK/Kaggle-Competitions/Better_Golf"   # the engine + durable docs + sources/ (THIS is 'where we left off')
data: "Better_Golf/data -> $WORK/kaggle/neurogolf-2026-run/data (symlink; 400 task json + neurogolf_utils)"
conda_env: kaggle
conda_python: "/home/woody/dsaa/dsaa115h/software/private/conda/envs/kaggle/bin/python"
grader_stack: "onnx==1.21.0  onnxruntime==1.24.4  onnx-tool==1.0.1  numpy==2.4.4 (matches Kaggle grader; byte-exact)"
max_concurrent_jobs: 8

model_map:
  brain: claude-opus-4-8
  codegen: sonnet
  bulk: haiku

# ── §13 Campaign ──
campaign:
  start_date: 2026-04-15
  entry_deadline: 2026-07-08T23:59:00Z      # also team-merger deadline
  deadline: 2026-07-15T23:59:00Z            # Final Submission Deadline (T-32d from 2026-06-13)
  target_rank: 10                            # public LB top-10 (operator request)
  daily_submission_quota: 5                  # per rules; 2 final picks
  final_picks: 2
  prize_pool_usd: 50000
  kaggle_team_name: "Fairlander-Flick"
  github_repo: "https://github.com/Fairlander-Flick/Kaggle-Competitions.git"

# ── leaderboard snapshot 2026-06-13 (Step 0) ──
lb_2026_06_13:
  top1: 7714.79            # CroDoc
  rank10_cutoff: 7467.45   # Dziyana Valenta (#10)
  our_best_lb: 5743.43     # STALE (May'26 Octaviograu repro). Sources/zip were gitignored & lost.
  best_public_notebook: 6372.62  # rajathrpai / vyanktesh (June'26) — current shareable ceiling
  gap_bestpublic_to_top10: ~1095  # the top teams' PRIVATE per-task golf edge (the real grind)
```

---
## Resume log (append-only)

### 2026-06-13 — Campaign resumed (Step 0 intelligence refresh)
- Prior effort (Better_Golf) stopped mid-May at genuine 5743.43, concluding "public-faithful
  ceiling ~5744". That conclusion is now STALE: the public field advanced to ~6372 (June) and the
  LB top-10 cutoff rose to ~7467. Re-entered per §13.5 (intelligence refresh, not a stop).
- Re-downloaded data (lost sources). Rebuilt grader env (onnx stack pinned). Re-fetching CURRENT best
  public bundles (6372/6364/6332/6315/6275/6154 + rewrite tools) into sources/.
- Plan: Phase 1 cross-blend current public (cheapest-valid-per-task) → expect ~6372+ (big jump from
  5743). Phase 2 grader-faithful rewrite passes. Phase 3 per-task minimal-ONNX golf on cost tail → top-10.

### lb_history
- { date: 2026-06-13T16:44Z, sub: "phase1 greedy cross-blend (--no-ours)", proj: 6379.57, lb: 6191.85,
    note: "GREEDY cheapest-valid-per-task LOST ~188 vs validated bundle: cheapest-on-arc-gen graphs
           overfit & FAIL the private holdout (->0). cross-pick is private-unsafe." }
- { date: 2026-06-13T16:49Z, sub: "vyanktesh 6372-58 flat verbatim", proj: ~6372, lb: 6372.58,
    rank: ~265, n_teams: 1893, note: "NEW BEST. realizes 1:1 (grader-faithful). validated bundles
    pass private; greedy blends do not. file MUST be named submission.zip (renamed file => 400)." }

### LB gradient (2026-06-13, 1893 teams) — our 6372.58 ≈ rank #265
- top100=6570 (+198) | top50=6970 (+598) | top20=7281 (+908) | top10=7467 (+1095) | top1=7714
- avg cost: public ~8700/task vs top10 ~560/task => top teams use MINIMAL-DTYPE intermediates.

### Cost map (blend_results.json, ~baseline): MEMORY-dominated
- buckets: 48 @10-14, 258 @14-17, 78 @17-20, 16 @>=20. median cost 13652 (mem dominates; params tiny).
- headroom: lift<17->17 +603(=>6982~top50); <18->18 +920(=>7299~top20); <20->20 +1656(=>8035>top10).
- => CLIMB = LOSSLESS memory minimization (dtype-narrow intermediates float32->int8/bool, fuse/eliminate
  big intermediates: ReduceSum-chain fusion, Cast-chain collapse, bool-reduction narrowing). Lossless =>
  semantics identical => passes private iff original did (vyanktesh base does) => SAFE climb. This is the
  ONLY private-safe lever beyond the public ceiling. Restrict Phase 2 to PROVABLY-lossless transforms.
