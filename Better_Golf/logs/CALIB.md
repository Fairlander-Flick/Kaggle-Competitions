# Calibration log — proving local == Kaggle

Goal: prove the local official-grader verifier (`engine/verify.py`, runs
`neurogolf_utils.verify_subset/score_network` verbatim over train+test+arc-gen
from the downloaded JSON) equals the Kaggle leaderboard score. One isolated
single-task submission per new family; LB of a 1-task zip == that task's local
points (all other tasks omitted score 0).

## Operational facts (verified 2026-05-16)

- Competition slug: **`neurogolf-2026`** ("The 2026 NeuroGolf Championship"),
  deadline 2026-07-15, user entered. Reward $50k.
- **Submission file MUST be named `submission.zip`.** A zip named anything else
  → `400 Bad Request` on CreateSubmission (file uploads, submission rejected).
  `engine/package.py` already writes `out/submission.zip` → real submits OK.
- Kaggle submissions table has **both `publicScore` and `privateScore`**
  columns; privateScore blank for all historical entries (revealed at close —
  standard Kaggle, not a different metric). Public reference: an open-solution
  copy scored publicScore **5480.41**.
- Grader code has NO holdout: `verify_network` scores exactly the
  train+test+arc-gen passed in; points iff `arc_agi_wrong+arc_gen_wrong==0`.
  Only unprovable-from-code assumption: Kaggle feeds the same arc-gen as the
  downloaded JSON. This log resolves that empirically.

## Calibration submissions

| date | task | family | local pts | LB publicScore | match? |
|---|---|---|---|---|---|
| 2026-05-16 15:44 | task171 | local_neighborhood | 13.907 | **13.90** | ✅ YES |

**RESULT: local == Kaggle PROVEN.** publicScore 13.90 == local 13.907
(Kaggle truncates display to 2 decimals; |Δ| < 0.01). The downloaded
arc-gen == Kaggle's arc-gen; the official-grader local path is faithful.
→ Switch to **pure-local grind**. No per-task submits needed. Submit only
the accumulated best `submission.zip` (named exactly that) when the local
projection beats the current best, never spray. Re-calibrate once per
genuinely-new construction family only if a future result looks suspect.

Interpretation rule: |LB − local| < 0.01 → local==Kaggle proven for this
family → switch to pure-local grind, submit only the accumulated best zip.
Mismatch → record gap, inspect arc-gen delta, adapt before further submits.
