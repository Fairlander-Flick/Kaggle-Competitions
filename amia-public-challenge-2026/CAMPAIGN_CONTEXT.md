---
doc: context
note: "LIVE persistent invariants. Created Step 1. APPEND-ONLY below the line."
---

# context.md — persistent invariants

```yaml
competition_id: amia-public-challenge-2026
modality: vision                      # object detection (DL spine, detection-adapted)
task_type: object_detection           # 14 thoracic findings + class14 "No finding"
note_source: "Re-host of VinBigData Chest X-ray Abnormalities Detection (public, CC-BY).
             All 15000 challenge images = the original PUBLIC, fully-labelled VinBigData
             train set. image_ids obfuscated; pixel content intact."

# ── HPC execution environment ──
cluster: tinygpu
slurm_suffix: ".tinygpu"
default_partition: a100
default_gres: "gpu:a100:1"
campaign_dir: "$WORK/kaggle/amia-public-challenge-2026-run"
container: null
conda_env: kaggle                     # /home/woody/dsaa/dsaa115h/software/private/conda/envs/kaggle
conda_python: "/home/woody/dsaa/dsaa115h/software/private/conda/envs/kaggle/bin/python"
max_concurrent_jobs: 8
http_proxy: "http://proxy.nhr.fau.de:80"

model_map:
  brain: claude-opus-4-8
  codegen: sonnet
  bulk: haiku

# ── §13 Campaign ──
campaign:
  deadline: 2026-06-14T21:55:00
  target_rank: 1
  daily_submission_quota: 5            # assumed; confirm via submissions API
  n_teams: 201
  top10_score_now: 0.999
  kaggle_team_name: "Ugur Tasdan"
  github_user: Fairlander-Flick

target_col: PredictionString
id_col: image_id
target_metric: "PASCAL VOC 2010 mAP @ IoU>0.4"
metric_direction: max
cv_object: "GroupKFold-by-image (detection); honest-model only"
seeds: [42]
sota_cv_target: 0.999                  # leak ceiling (the two prior leaders + us)
submission_is_code_competition: false  # CSV submission; submit via CLI or notebook
inference_runtime_limit_sec: null
sample_submission_schema:
  columns: [image_id, PredictionString]
  n_rows: 6427
  id_order_locked: false               # any order accepted; we keep sample order

# ── coordinates / format invariants (from discussion #691668) ──
prediction_coord_space: "ORIGINAL image resolution (use img_size.csv dim0=H, dim1=W),
                         NOT 1024px. train.csv boxes already in original px."
no_finding_string: "14 1 0 0 1 1"
pred_string_format: "class_id confidence x_min y_min x_max y_max ... (repeat per box)"

# ── EXPLOITABLE-LEAK CARVE-OUT (§5 #2 / Step 3.5) — operator-approved ──
leak_carveout:
  approved_by_operator: true
  date: 2026-06-13
  rationale: "Kudos-only community comp on explicitly PUBLIC released data; NO rules
             prohibit using the public source (organizer-tolerated, discussion #701752);
             two teams already at 0.999; honest modelling caps ~0.55 and cannot win."
  proof_present_in_private: "100% — bijection 15000↔15000, 0 collisions; every test
             image (public AND private partition) recovered from public set."
  method: "perceptual-match obfuscated challenge PNG -> original 256px public PNG
           (xhlulu/vinbigdata-chest-xray-resized-png-256x256), recover GT boxes from
           awsaf49/vinbigdata-yolo-labels-dataset train_merge.csv (raw multi-rad)."
  validation: "8573/8573 challenge-train images: exact label-multiset match (100%).
               descriptor = 32x32 standardized grayscale, (H,W) hard prefilter,
               polarity-invariant (test both v and -v). train dist p95=0.048."
  result: "public LB 0.999, rank 1 (tied)."

# ── DL spine (honest-model side, secondary deliverable) ──
dl_track: true
backbone: null                         # honest model TBD (YOLO11 / RT-DETR)
gpu_budget_hours: 200
gpu_h_used_total: 0
```

---
# APPEND-ONLY below

## experiment_log
| exp_id | step | change | cv_before | cv_after | delta | accepted | stage | jobid | gpu_h_used |
|--------|------|--------|-----------|----------|-------|----------|-------|-------|------------|
| E1 | 3.5 | provenance leak hash-match + recover GT boxes | 0.468(LB,honest) | 0.999(LB) | +0.531 | yes | confirm | (frontend) | 0 |

## lb_history
| date | sub_file | cv | lb | rank | n_teams | top1 | top10_score | gap_to_top10 | gap_to_gold | quota_left | probe_purpose |
|------|----------|----|----|------|---------|------|-------------|--------------|-------------|------------|---------------|
| 2026-06-13T09:06 | leak/submission.csv | n/a | 0.999 | 1(tied) | 201 | 0.999 | 0.999 | 0.0 | 0.0 | ? | win via leak |

## decisions
- (Step 0/1) Modality = vision/object-detection; re-host of public VinBigData. Routed DL spine, detection-adapted.
- (Step 3.5) Exploitable-leak carve-out APPROVED by operator (2026-06-13). Verified present in private (100% bijection). Submitted, LB 0.999, rank 1.
- (Operator) Also build BOTH honest + leak as PUBLIC Kaggle notebooks and submit via notebook (farm Kaggle notebook points). Document all in GitHub repo Fairlander-Flick/Kaggle-Competitions.

## running_jobs
| jobid | array? | partition | step/type | submitted_at | last_state |
|-------|--------|-----------|-----------|--------------|------------|

## paradigm_shifts
