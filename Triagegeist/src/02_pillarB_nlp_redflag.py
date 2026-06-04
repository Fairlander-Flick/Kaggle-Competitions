# =============================================================================
# Triagegeist — Pillar B: Chief-Complaint NLP Red-Flag Flagger
# =============================================================================
# Author : Fairlander Flick
# Seed   : 42 (all stochastic components)
# Target : binary high_acuity = triage_acuity in {1, 2}
#
# Design:
#   1. Load & join (STRATEGY canonical preamble).
#   2. TF-IDF text model (word 1-2g + char 3-5g) → LR + LightGBM, 5-fold OOF.
#   3. Marginal-lift comparison: text-only vs vitals-only vs combined.
#   4. Red-flag lexicon: 15 clinically-grounded phrases — recall/precision as safety net.
#   5. Subjective vs objective complaint split — performance by category.
#   6. Top TF-IDF feature bar chart, PR-curve, lexicon bar chart.
#   7. Save pb_results.json.
# =============================================================================

import json, re, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    precision_recall_curve, recall_score, precision_score
)
import lightgbm as lgb

warnings.filterwarnings("ignore")

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

DATA = "/kaggle/input/competitions/triagegeist/"
LEAKAGE = ["disposition", "ed_los_hours"]
TARGET   = "triage_acuity"
VITALS   = [
    "systolic_bp", "diastolic_bp", "mean_arterial_pressure", "pulse_pressure",
    "heart_rate", "respiratory_rate", "temperature_c", "spo2",
    "gcs_total", "pain_score", "shock_index", "news2_score"
]

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA LOAD & JOIN (verbatim STRATEGY preamble)
# ─────────────────────────────────────────────────────────────────────────────
print("=== PILLAR B: Chief-Complaint NLP Red-Flag Flagger ===\n")

def load():
    train = pd.read_csv(DATA + "train.csv")
    test  = pd.read_csv(DATA + "test.csv")
    cc    = pd.read_csv(DATA + "chief_complaints.csv")
    ph    = pd.read_csv(DATA + "patient_history.csv")
    cc = cc.drop(columns=["chief_complaint_system"], errors="ignore")
    train = train.merge(cc, on="patient_id", how="left").merge(ph, on="patient_id", how="left")
    test  = test.merge(cc, on="patient_id", how="left").merge(ph, on="patient_id", how="left")
    return train, test

def clean(df):
    df = df.copy()
    df.loc[df["pain_score"] < 0, "pain_score"] = np.nan
    if "pulse_pressure" in df.columns:
        df.loc[df["pulse_pressure"] < 0, "pulse_pressure"] = np.nan
    return df

train_raw, test_raw = load()
train = clean(train_raw)

print(f"Train shape: {train.shape}")
print(f"Target distribution:\n{train[TARGET].value_counts().sort_index()}\n")

# Binary target: ESI levels 1 or 2 = high acuity
y = train[TARGET].isin([1, 2]).astype(int)
print(f"High-acuity positives: {y.sum()} / {len(y)}  ({y.mean()*100:.1f}%)\n")

# ─────────────────────────────────────────────────────────────────────────────
# 2. TF-IDF TEXT MODEL
# ─────────────────────────────────────────────────────────────────────────────
# NaN → empty string; lowercase
texts = train["chief_complaint_raw"].fillna("").str.lower()

# Feature union: word (1,2)-grams + char (3,5)-grams
word_tfidf = TfidfVectorizer(
    analyzer="word", ngram_range=(1, 2),
    max_features=8000, min_df=3, sublinear_tf=True
)
char_tfidf = TfidfVectorizer(
    analyzer="char_wb", ngram_range=(3, 5),
    max_features=8000, min_df=3, sublinear_tf=True
)

X_word = word_tfidf.fit_transform(texts)
X_char = char_tfidf.fit_transform(texts)
X_text = hstack([X_word, X_char], format="csr")
print(f"TF-IDF matrix: {X_text.shape[0]} rows × {X_text.shape[1]} features\n")

# ─── 5-fold OOF: Logistic Regression ───────────────────────────────────────
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

oof_lr  = np.zeros(len(y))
oof_lgb = np.zeros(len(y))

print("--- Training LR + LightGBM on TF-IDF (text-only) ---")
for fold, (tr_idx, va_idx) in enumerate(skf.split(X_text, y), 1):
    # Logistic Regression
    lr = LogisticRegression(
        C=1.0, class_weight="balanced", max_iter=1000,
        solver="lbfgs", random_state=RANDOM_STATE
    )
    lr.fit(X_text[tr_idx], y.iloc[tr_idx])
    oof_lr[va_idx] = lr.predict_proba(X_text[va_idx])[:, 1]

    # LightGBM (sparse-safe, handles imbalance via scale_pos_weight)
    pos_w = (y.iloc[tr_idx] == 0).sum() / max((y.iloc[tr_idx] == 1).sum(), 1)
    ds_tr = lgb.Dataset(X_text[tr_idx], label=y.iloc[tr_idx])
    ds_va = lgb.Dataset(X_text[va_idx], label=y.iloc[va_idx], reference=ds_tr)
    params = dict(
        objective="binary", metric="auc",
        learning_rate=0.05, num_leaves=63,
        min_child_samples=20, feature_fraction=0.8,
        scale_pos_weight=pos_w, verbosity=-1,
        random_state=RANDOM_STATE
    )
    cb = lgb.train(
        params, ds_tr, num_boost_round=300,
        valid_sets=[ds_va],
        callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(-1)]
    )
    oof_lgb[va_idx] = cb.predict(X_text[va_idx])
    print(f"  Fold {fold} — LR AUC={roc_auc_score(y.iloc[va_idx], oof_lr[va_idx]):.4f}"
          f"  LGB AUC={roc_auc_score(y.iloc[va_idx], oof_lgb[va_idx]):.4f}")

text_lr_auc  = roc_auc_score(y, oof_lr)
text_lr_ap   = average_precision_score(y, oof_lr)
text_lgb_auc = roc_auc_score(y, oof_lgb)
text_lgb_ap  = average_precision_score(y, oof_lgb)

# Use LGB as primary text model (generally better)
oof_text = oof_lgb

print(f"\nText-only OOF:  LR  ROC-AUC={text_lr_auc:.4f}  PR-AUC={text_lr_ap:.4f}")
print(f"                LGB ROC-AUC={text_lgb_auc:.4f}  PR-AUC={text_lgb_ap:.4f}\n")

# High-sensitivity threshold (top ~20% flagged = practical ED deployment)
thresh_sensitivity = np.percentile(oof_text, 80)
y_pred_hs = (oof_text >= thresh_sensitivity).astype(int)
recall_hs  = recall_score(y, y_pred_hs)
prec_hs    = precision_score(y, y_pred_hs)
print(f"At 80th-percentile threshold={thresh_sensitivity:.3f}: "
      f"Recall(L1-2)={recall_hs:.3f}  Precision={prec_hs:.3f}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. MARGINAL LIFT — text-only vs vitals-only vs combined
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Marginal Lift: text vs vitals vs combined ---")

# Vitals feature matrix (median-impute missing for LR fallback; LGB handles NaN)
X_vitals = train[VITALS].copy()
# Numeric imputation for combined sparse model (LGB handles natively, so just for indexing)
X_vitals_arr = X_vitals.values.astype(np.float32)

oof_vitals   = np.zeros(len(y))
oof_combined = np.zeros(len(y))

# Build combined: vitals (dense) + text TF-IDF (sparse) → hstack
X_vitals_sparse = csr_matrix(X_vitals_arr)
X_combined = hstack([X_text, X_vitals_sparse], format="csr")

for fold, (tr_idx, va_idx) in enumerate(skf.split(X_vitals_arr, y), 1):
    pos_w = (y.iloc[tr_idx] == 0).sum() / max((y.iloc[tr_idx] == 1).sum(), 1)
    params_base = dict(
        objective="binary", metric="auc",
        learning_rate=0.05, num_leaves=63,
        min_child_samples=20, feature_fraction=0.8,
        scale_pos_weight=pos_w, verbosity=-1,
        random_state=RANDOM_STATE
    )

    # Vitals-only
    dv_tr = lgb.Dataset(X_vitals_arr[tr_idx], label=y.iloc[tr_idx])
    dv_va = lgb.Dataset(X_vitals_arr[va_idx], label=y.iloc[va_idx], reference=dv_tr)
    mdl_v = lgb.train(
        params_base, dv_tr, num_boost_round=300,
        valid_sets=[dv_va],
        callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(-1)]
    )
    oof_vitals[va_idx] = mdl_v.predict(X_vitals_arr[va_idx])

    # Combined (text + vitals) — LightGBM on sparse CSR
    dc_tr = lgb.Dataset(X_combined[tr_idx], label=y.iloc[tr_idx])
    dc_va = lgb.Dataset(X_combined[va_idx], label=y.iloc[va_idx], reference=dc_tr)
    mdl_c = lgb.train(
        params_base, dc_tr, num_boost_round=300,
        valid_sets=[dc_va],
        callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(-1)]
    )
    oof_combined[va_idx] = mdl_c.predict(X_combined[va_idx])

    v_auc = roc_auc_score(y.iloc[va_idx], oof_vitals[va_idx])
    c_auc = roc_auc_score(y.iloc[va_idx], oof_combined[va_idx])
    print(f"  Fold {fold} — Vitals AUC={v_auc:.4f}  Combined AUC={c_auc:.4f}")

vitals_auc  = roc_auc_score(y, oof_vitals)
vitals_ap   = average_precision_score(y, oof_vitals)
comb_auc    = roc_auc_score(y, oof_combined)
comb_ap     = average_precision_score(y, oof_combined)

print(f"\nMarginal lift table:")
print(f"  {'Model':<20} {'ROC-AUC':>8}  {'PR-AUC':>8}")
print(f"  {'Text-only (LGB)':<20} {text_lgb_auc:>8.4f}  {text_lgb_ap:>8.4f}")
print(f"  {'Vitals-only (LGB)':<20} {vitals_auc:>8.4f}  {vitals_ap:>8.4f}")
print(f"  {'Combined (LGB)':<20} {comb_auc:>8.4f}  {comb_ap:>8.4f}")
text_lift_auc = comb_auc - vitals_auc
text_lift_ap  = comb_ap  - vitals_ap
print(f"\n  Text lift over vitals: ΔROC-AUC={text_lift_auc:+.4f}  ΔPR-AUC={text_lift_ap:+.4f}")
if abs(text_lift_auc) < 0.01:
    print("  *** Honest note: text adds negligible lift over vitals for acuity prediction. ***")
    print("  *** Real-world value: safety net when vitals deceptively normal (elderly/atypical ACS). ***\n")

# ─────────────────────────────────────────────────────────────────────────────
# 4. RED-FLAG LEXICON
# ─────────────────────────────────────────────────────────────────────────────
# 15 clinically-grounded red-flag patterns anchored in ESI L1/L2 presentations.
# Sources: ESI Handbook v5; UpToDate "Approach to the patient with headache";
#          ACC/AHA STEMI guidelines; Surviving Sepsis Campaign.

RED_FLAGS = {
    "thunderclap_headache"  : r"thunderclap|worst.{0,10}headache|worst headache",
    "chest_pain_diaphoresis": r"chest.{0,20}(pain|pressure|tightness).{0,40}(sweat|diaphor)|diaphor.{0,40}chest",
    "chest_pain"            : r"\bchest\s+(pain|pressure|tightness|discomfort)\b",
    "stroke_deficit"        : r"\bstroke\b|facial\s+droop|arm\s+weak|slurred\s+speech|aphasia|hemiplegia|focal\s+deficit",
    "respiratory_distress"  : r"\brespiratory\s+(failure|arrest|distress)\b|can.t\s+breathe|unable\s+to\s+breathe",
    "anaphylaxis"           : r"\banaphyla|allergic\s+reaction\s+(severe|acute)|throat\s+(closing|swelling)",
    "sepsis_rigors"         : r"\bsepsis\b|septic\s+shock|\brigors\b|rigors\s+and\s+fever|shaking\s+chills",
    "suicidal_ideation"     : r"suicid|overdose|self.?harm|wants\s+to\s+die",
    "hemorrhage"            : r"\bhemorrhage\b|massive\s+bleed|coughing\s+blood|hemoptysis|rectal\s+bleed\s+heavy",
    "cardiac_arrest"        : r"cardiac\s+arrest|pulseless|unresponsive\s+and\s+pulseless|vf\b|v\.?fib",
    "acute_abdomen"         : r"acute\s+abdomen|board.?like\s+abdomen|rigid\s+abdomen|ruptured\s+aort",
    "meningeal_signs"       : r"\bmeningit|nuchal\s+rigidity|stiff\s+neck\s+and\s+fever|photophobia\s+and\s+headache",
    "diabetic_emergency"    : r"diabetic\s+keto|dka\b|hypoglycemi.{0,10}(unresponsive|altered|severe)",
    "eclampsia"             : r"\beclampsia\b|pre.?eclampsia\s+severe|seizure\s+in\s+pregnan",
    "aortic_dissection"     : r"aortic\s+(dissect|tear|rupture)|tearing\s+(chest|back)\s+pain",
}

texts_raw = train["chief_complaint_raw"].fillna("").str.lower()

flag_cols = {}
for flag_name, pattern in RED_FLAGS.items():
    flag_cols[flag_name] = texts_raw.str.contains(pattern, regex=True, na=False).astype(int)

flag_df = pd.DataFrame(flag_cols)
any_flag = flag_df.any(axis=1).astype(int)

n_flagged = any_flag.sum()
print(f"\n--- Red-Flag Lexicon ---")
print(f"Total flagged: {n_flagged} / {len(any_flag)}  ({n_flagged/len(any_flag)*100:.2f}%)")

# Acuity distribution among flagged
acuity_dist = pd.crosstab(
    any_flag.rename("flag"), train[TARGET],
    margins=True, normalize="index"
).round(3)
print("\nAcuity distribution (row %):"); print(acuity_dist)

# Precision & recall of lexicon as standalone classifier for high acuity
flag_prec   = precision_score(y, any_flag, zero_division=0)
flag_recall = recall_score(y, any_flag, zero_division=0)
flag_auc    = roc_auc_score(y, any_flag) if any_flag.nunique() > 1 else 0.5
print(f"\nLexicon as standalone safety net:")
print(f"  Precision={flag_prec:.3f}  Recall={flag_recall:.3f}  ROC-AUC={flag_auc:.4f}")

# Per-flag counts and high-acuity rate
print("\nPer-flag breakdown:")
for fname, fcol in flag_cols.items():
    cnt = fcol.sum()
    if cnt == 0:
        print(f"  {fname:<30} n=0")
        continue
    ha_rate = y[fcol == 1].mean()
    print(f"  {fname:<30} n={cnt:>5}  high-acuity-rate={ha_rate:.3f}")

# ─────────────────────────────────────────────────────────────────────────────
# 5. SUBJECTIVE vs OBJECTIVE COMPLAINT SPLIT
# ─────────────────────────────────────────────────────────────────────────────
# Disparity literature (RESEARCH §4b) shows bias concentrates in subjective complaints.
# Subjective: symptom-reported (pain, dyspnea, dizziness, nausea, palpitations, fatigue)
# Objective:  mechanism/injury (trauma, laceration, fracture, burn, dislocation, wound)

SUBJ_PATTERN = (
    r"\bpain\b|chest\s+pain|dyspnea|shortness\s+of\s+breath|sob\b|dizziness|dizzy|"
    r"nausea|vomiting|palpitation|fatigue|weakness|syncope|confusion|"
    r"headache|abdominal\s+pain|back\s+pain|generalized\s+pain|malaise"
)
OBJ_PATTERN  = (
    r"\btrauma\b|laceration|fracture|burn\b|burn\s+injury|dislocation|"
    r"mva\b|motor\s+vehicle|fall\s+from|head\s+injury|blunt|wound\b|stabbing|"
    r"penetrating|crush\s+injury|amputation"
)

is_subj = texts_raw.str.contains(SUBJ_PATTERN, regex=True, na=False)
is_obj  = texts_raw.str.contains(OBJ_PATTERN,  regex=True, na=False)
# Complaints can match both; prioritise objective (protocol-driven = less discretion)
complaint_type = pd.Series("other", index=train.index)
complaint_type[is_subj]  = "subjective"
complaint_type[is_obj]   = "objective"   # overrides if both

print("\n--- Subjective vs Objective Split ---")
print(complaint_type.value_counts())

perf_rows = []
for ctype in ["subjective", "objective", "other"]:
    mask = complaint_type == ctype
    if mask.sum() < 50:
        continue
    auc_t  = roc_auc_score(y[mask], oof_text[mask])
    ap_t   = average_precision_score(y[mask], oof_text[mask])
    ha_r   = y[mask].mean()
    lx_rec = recall_score(y[mask], any_flag[mask], zero_division=0)
    lx_pre = precision_score(y[mask], any_flag[mask], zero_division=0)
    perf_rows.append({
        "type": ctype, "n": int(mask.sum()), "ha_rate": round(ha_r, 3),
        "text_AUC": round(auc_t, 4), "text_PR_AUC": round(ap_t, 4),
        "lexicon_recall": round(lx_rec, 3), "lexicon_precision": round(lx_pre, 3)
    })
    print(f"\n  {ctype.upper()} (n={mask.sum()}, HA rate={ha_r:.3f})")
    print(f"    text ROC-AUC={auc_t:.4f}  PR-AUC={ap_t:.4f}")
    print(f"    lexicon recall={lx_rec:.3f}  precision={lx_pre:.3f}")

# ─────────────────────────────────────────────────────────────────────────────
# 6. SAVE FIGURES
# ─────────────────────────────────────────────────────────────────────────────

# ── Figure 1: PR curve (LGB text model) ─────────────────────────────────────
prec_curve, rec_curve, thresholds_pr = precision_recall_curve(y, oof_text)

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(rec_curve, prec_curve, lw=2, color="#1f77b4", label=f"Text LGB (PR-AUC={text_lgb_ap:.3f})")
prc_v, rec_v, _ = precision_recall_curve(y, oof_vitals)
ax.plot(rec_v, prc_v, lw=2, color="#ff7f0e", linestyle="--", label=f"Vitals LGB (PR-AUC={vitals_ap:.3f})")
prc_c, rec_c, _ = precision_recall_curve(y, oof_combined)
ax.plot(rec_c, prc_c, lw=2, color="#2ca02c", linestyle=":", label=f"Combined (PR-AUC={comb_ap:.3f})")
ax.axhline(y.mean(), color="gray", lw=1, linestyle="--", label=f"Baseline prevalence ({y.mean():.3f})")
ax.set_xlabel("Recall", fontsize=12)
ax.set_ylabel("Precision", fontsize=12)
ax.set_title("Precision-Recall Curve — High Acuity (ESI 1-2)\nText vs Vitals vs Combined (5-fold OOF)", fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("pb_pr_curve.png", dpi=120)
plt.close(fig)
print("\nSaved: pb_pr_curve.png")

# ── Figure 2: Red-flag phrases — flagged count + high-acuity concentration ──
flag_summary = []
for fname, fcol in flag_cols.items():
    cnt = fcol.sum()
    ha_rate = y[fcol == 1].mean() if cnt > 0 else 0.0
    flag_summary.append({"flag": fname.replace("_", " "), "count": cnt, "ha_rate": ha_rate})
flag_summary_df = pd.DataFrame(flag_summary).sort_values("count", ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

# Left: counts
axes[0].barh(flag_summary_df["flag"], flag_summary_df["count"], color="#4c72b0", height=0.65)
axes[0].set_xlabel("Count in training set", fontsize=11)
axes[0].set_title("Red-Flag Phrase Counts", fontsize=12)
axes[0].grid(axis="x", alpha=0.3)

# Right: high-acuity rate
colors_ha = ["#d62728" if r >= 0.5 else "#ff9896" if r >= 0.25 else "#aec7e8"
             for r in flag_summary_df["ha_rate"]]
axes[1].barh(flag_summary_df["flag"], flag_summary_df["ha_rate"], color=colors_ha, height=0.65)
axes[1].axvline(y.mean(), color="black", lw=1.5, linestyle="--", label=f"Base rate ({y.mean():.2f})")
axes[1].set_xlabel("High-Acuity Rate (actual)", fontsize=11)
axes[1].set_title("Red-Flag Phrase → High-Acuity Rate", fontsize=12)
axes[1].legend(fontsize=9)
axes[1].xaxis.set_major_formatter(ticker.PercentFormatter(1.0))
axes[1].grid(axis="x", alpha=0.3)

fig.suptitle("Red-Flag Lexicon: Prevalence and High-Acuity Concentration\n"
             "(red = precision ≥50%, pink = ≥25%, blue = <25%)", fontsize=11, y=1.01)
fig.tight_layout()
fig.savefig("pb_lexicon_flags.png", dpi=120, bbox_inches="tight")
plt.close(fig)
print("Saved: pb_lexicon_flags.png")

# ── Figure 3: Top TF-IDF features for high acuity ───────────────────────────
# Refit LR on all data to extract coefficients cleanly
lr_all = LogisticRegression(
    C=1.0, class_weight="balanced", max_iter=1000,
    solver="lbfgs", random_state=RANDOM_STATE
)
lr_all.fit(X_text, y)
feature_names = (
    list(word_tfidf.get_feature_names_out()) +
    list(char_tfidf.get_feature_names_out())
)
coefs = lr_all.coef_[0]
# Top 25 by absolute coefficient (positive = high acuity)
top_n = 25
top_idx_pos = np.argsort(coefs)[-top_n:][::-1]
top_idx_neg = np.argsort(coefs)[:top_n]

top_features = (
    [(feature_names[i], coefs[i]) for i in top_idx_pos] +
    [(feature_names[i], coefs[i]) for i in top_idx_neg]
)
top_df = pd.DataFrame(top_features, columns=["feature", "coef"]).sort_values("coef")

fig, ax = plt.subplots(figsize=(8, 10))
colors = ["#d62728" if c > 0 else "#1f77b4" for c in top_df["coef"]]
ax.barh(top_df["feature"], top_df["coef"], color=colors, height=0.75)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("LR Coefficient (positive = high acuity, red; negative = low acuity, blue)", fontsize=10)
ax.set_title("Top TF-IDF Features for High Acuity Prediction\n(word 1-2g + char 3-5g, LR)", fontsize=12)
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig("pb_tfidf_features.png", dpi=120)
plt.close(fig)
print("Saved: pb_tfidf_features.png")

# ─────────────────────────────────────────────────────────────────────────────
# 7. SAVE pb_results.json
# ─────────────────────────────────────────────────────────────────────────────
results = {
    "pillar": "B",
    "description": "Chief-complaint NLP red-flag flagger",
    "seed": RANDOM_STATE,
    "n_train": int(len(y)),
    "n_high_acuity": int(y.sum()),
    "high_acuity_prevalence": float(y.mean()),

    "text_only": {
        "model": "LightGBM on TF-IDF (word 1-2g + char 3-5g)",
        "roc_auc": round(text_lgb_auc, 4),
        "pr_auc":  round(text_lgb_ap,  4),
        "recall_at_80pct_threshold": round(recall_hs, 4),
        "precision_at_80pct_threshold": round(prec_hs, 4),
    },
    "text_lr": {
        "roc_auc": round(text_lr_auc, 4),
        "pr_auc":  round(text_lr_ap,  4),
    },
    "marginal_lift": {
        "text_only_roc_auc":    round(text_lgb_auc, 4),
        "text_only_pr_auc":     round(text_lgb_ap,  4),
        "vitals_only_roc_auc":  round(vitals_auc,   4),
        "vitals_only_pr_auc":   round(vitals_ap,    4),
        "combined_roc_auc":     round(comb_auc,     4),
        "combined_pr_auc":      round(comb_ap,      4),
        "text_delta_roc_auc":   round(text_lift_auc, 4),
        "text_delta_pr_auc":    round(text_lift_ap,  4),
    },
    "red_flag_lexicon": {
        "n_patterns": len(RED_FLAGS),
        "n_flagged": int(n_flagged),
        "pct_flagged": round(n_flagged / len(any_flag) * 100, 2),
        "precision": round(flag_prec,   3),
        "recall":    round(flag_recall, 3),
        "roc_auc":   round(flag_auc,    4),
    },
    "subjective_objective_split": perf_rows,
    "figures": [
        "pb_pr_curve.png",
        "pb_lexicon_flags.png",
        "pb_tfidf_features.png"
    ]
}

with open("pb_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved: pb_results.json")

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY PRINT
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("PILLAR B HEADLINE RESULTS")
print("="*60)
print(f"Text-only  ROC-AUC: {text_lgb_auc:.4f}  PR-AUC: {text_lgb_ap:.4f}")
print(f"Vitals-only ROC-AUC: {vitals_auc:.4f}  PR-AUC: {vitals_ap:.4f}")
print(f"Combined   ROC-AUC: {comb_auc:.4f}  PR-AUC: {comb_ap:.4f}")
print(f"Text lift: ΔROC-AUC={text_lift_auc:+.4f}  ΔPR-AUC={text_lift_ap:+.4f}")
print(f"\nRed-flag lexicon (standalone): Precision={flag_prec:.3f}  Recall={flag_recall:.3f}")
print(f"  {n_flagged} flagged ({n_flagged/len(any_flag)*100:.1f}%)")
print("="*60)
print("Pillar B complete.")
