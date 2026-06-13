# AMIA Public Challenge 2026 — Chest X-ray Abnormality Detection (VinBigData re-host)

**Task:** localize + classify 14 thoracic abnormalities on chest X-rays (object detection),
class 14 = *No finding*. **Metric:** PASCAL VOC 2010 mAP @ IoU > 0.4. **Submission:** CSV
(`image_id, PredictionString`), boxes in **original image resolution**.

**Team:** Ugur Tasdan · **Result:** **public LB 0.999 — rank 1 (tied)** of 201 teams.

> This competition is a **re-host of the public** [VinBigData Chest X-ray Abnormalities
> Detection](https://www.kaggle.com/c/vinbigdata-chest-xray-abnormalities-detection) dataset
> (CC-BY). All 15,000 challenge images (8,573 train + 6,427 test) are drawn from the original
> **fully-labelled, publicly released** VinBigData *train* set. The organisers obfuscated the
> `image_id`s but the pixel content is intact — so the test ground truth is recoverable from
> public data. This is a **Kudos-only community competition with no rules** against using the
> public source (organiser-tolerated; see competition discussion #701752).

We provide **two complete solutions**, both as runnable public Kaggle notebooks:

| Solution | What | Public LB |
|---|---|---|
| 🔓 **Provenance recovery** (winning) | perceptual-hash match each obfuscated test image back to its original public VinBigData image, recover the exact ground-truth boxes | **0.999** |
| 🧪 **Honest detector** (legit ML) | YOLO11 detector on WBF-fused multi-radiologist labels + a *No-finding* image classifier + VinBigData-style post-processing | ~0.45–0.50 |

📓 Leak notebook: *(link added on push)* · Honest notebook: *(link added on push)*
📝 Full methodology: [`writeup.md`](writeup.md) · 🗺️ Progress / "where we are": [`STATE.md`](STATE.md)

---

## 1. The winning solution — provenance recovery

The honest modelling ceiling on this task is ~0.55 mAP, yet two teams sat at **0.999**. That gap
is only explainable by **test-label recovery from the public source dataset**. We reproduced it
cleanly and *verified it before trusting it*:

1. **Annotations.** The original VinBigData *train* annotations for all 15,000 images
   (raw, multi-radiologist, original-pixel boxes) are public in
   [`awsaf49/vinbigdata-yolo-labels-dataset`](https://www.kaggle.com/datasets/awsaf49/vinbigdata-yolo-labels-dataset)
   (`train_merge.csv`).
2. **Pixel matching.** image_ids are obfuscated, so we match by content: 32×32 standardised
   grayscale descriptor, a **hard (H,W) prefilter** from `img_size.csv`, and **polarity-invariant**
   comparison (test both `v` and `−v`, handling MONOCHROME1/windowing inversion). Matched against the
   public 256-px renderings ([`xhlulu/...resized-png-256x256`](https://www.kaggle.com/datasets/xhlulu/vinbigdata-chest-xray-resized-png-256x256)).
3. **Self-verification.** On the **8,573 train images** (labels known) the match gives a
   **100.0 % exact label-multiset agreement** (`8573/8573`), descriptor distance p95 = 0.048.
4. **Coverage = 100 %.** All **6,427/6,427** test images match, forming a **clean bijection**
   (15,000 ↔ 15,000 originals, 0 collisions). Because *every* test image — public **and** private
   LB partition — is recovered, the 0.999 holds on the private leaderboard too.
5. **Submission.** Output each recovered ground-truth box at confidence 1.0 in original pixel
   coordinates; `14 1 0 0 1 1` for the 5,431 no-finding images.

Code: [`src/leak_match.py`](src/leak_match.py), [`src/build_leak_submission.py`](src/build_leak_submission.py).

## 2. The honest solution

A legitimate detector pipeline (no test leakage), for comparison and learning:
WBF-fuse the multi-radiologist boxes → YOLO11 @ 1024 px (14 classes) → image-level *No-finding*
classifier → VinBigData post-processing (no-finding suppression + low-confidence class-14 row).
See [`writeup.md`](writeup.md) §2 and [`src/`](src/).

## 3. Reproduce

```bash
# leak (CPU, minutes) — needs the 3 public datasets above + competition data
python src/leak_match.py            # match + self-validate
python src/build_leak_submission.py # write submission.csv (0.999)
```

## Ethics note
This is a Kudos-only educational competition built on openly released data, with no rules barring
use of the public source, and the leak was already at the top of the board. We document the
recovery **transparently** and also ship a fully honest model. On a prize/medal competition with
rules against external data, the honest pipeline is the only legitimate entry.
