# STATE — nerede kaldık? (AMIA 2026 campaign tracker)

_Live "you are here" for this competition. Updated as work progresses._

**Last update:** 2026-06-13 ~09:15 UTC · **Deadline:** 2026-06-14 21:55 UTC (~37h left)
**Run dir (cluster):** `$WORK/kaggle/amia-public-challenge-2026-run` (data + artifacts, not in git)
**Cluster:** TinyGPU (`tinyx`) · conda env `kaggle` · brain = Claude Code on frontend

## Status board

| # | Deliverable | Status |
|---|---|---|
| 1 | Recon: task, metric, deadline, leak hypothesis | ✅ done |
| 2 | Leak carve-out approved by operator | ✅ done |
| 3 | Pixel matcher + 100% train self-validation | ✅ done (8573/8573 exact) |
| 4 | Test match 100% coverage, clean bijection | ✅ done (6427/6427) |
| 5 | Leak submission via CLI | ✅ **LB 0.999, rank 1 (tied)** |
| 6 | GitHub repo folder + docs | 🟡 in progress |
| 7 | Leak → public Kaggle notebook + submit via notebook | ✅ done (https://www.kaggle.com/code/fairlanderflick/amia-2026-provenance-recovery-map-0-999) |
| 8 | Honest detector training (YOLO11 @1024 + no-finding clf) | ⬜ todo |
| 9 | Honest → public Kaggle notebook + submit via notebook | ⬜ todo |
| 10 | Final pick: select scoring submissions; LB defend | ⬜ todo |

## Key facts (don't re-derive)
- **It is a re-host of public VinBigData.** All 15,000 imgs = original public TRAIN set (labelled).
- `image_id`s obfuscated (random base62); **pixel content intact** → matchable.
- **Predictions in ORIGINAL resolution** (img_size.csv: dim0=H, dim1=W). NOT 1024.
- No-finding string: `14 1 0 0 1 1`. ~84.5% of test is no-finding.
- Public datasets used for the leak:
  - `awsaf49/vinbigdata-yolo-labels-dataset` → `train_merge.csv` (raw multi-rad GT, original px)
  - `xhlulu/vinbigdata-chest-xray-resized-png-256x256` → originals for pixel matching
- Honest-model prior LB on this account: best **0.468** (RT-DETR+YOLO ensembles).
- Kaggle handle: `fairlanderflick`; team "Ugur Tasdan".

## Submissions log
| date | file | method | public LB |
|---|---|---|---|
| 2026-06-13 09:06 | leak/submission.csv | provenance recovery | **0.999** |
| 2026-06-13 11:32 | notebook output | provenance recovery (public notebook) | (pending score) |

## Next action
Build the leak Kaggle notebook (`notebooks/`), push public, submit via notebook. Then prep + launch
honest YOLO11 training on TinyGPU A100.
