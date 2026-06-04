"""
Pillar A — Calibrated Triage-Acuity Model + Rule Reverse-Engineering + Outcome Validation
Triagegeist Kaggle Hackathon  |  seed=42 everywhere  |  NO leakage cols as features

Sections:
  1. Data load + clean (canonical preamble from STRATEGY.md)
  2. Feature matrix construction
  3. StratifiedKFold(5) LightGBM multiclass OOF
  4. Metrics: accuracy, macro-F1, QWK, per-class recall, confusion matrix
  5. Calibration: isotonic, ECE before/after, reliability diagram
  6. SHAP rule reverse-engineering: global importance + per-class + age-blindness
  7. Outcome validation: OOF predicted acuity vs admit/mortality/LOS
  8. Serialize pa_results.json
"""

# ── stdlib + standard ML stack ─────────────────────────────────────────────
import json, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for script kernels
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score, f1_score, cohen_kappa_score,
    recall_score, confusion_matrix
)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
import lightgbm as lgb
import shap

# ── Canonical constants (STRATEGY.md verbatim) ─────────────────────────────
DATA         = "/kaggle/input/competitions/triagegeist/"
RANDOM_STATE = 42
LEAKAGE      = ["disposition", "ed_los_hours"]   # NEVER features
TARGET       = "triage_acuity"

PROTECTED = ["language", "insurance_type", "age_group", "sex"]
VITALS    = ["systolic_bp","diastolic_bp","mean_arterial_pressure","pulse_pressure",
             "heart_rate","respiratory_rate","temperature_c","spo2","gcs_total",
             "pain_score","shock_index","news2_score"]

# ── Canonical load() / clean() from STRATEGY.md ────────────────────────────
def load():
    train = pd.read_csv(DATA + "train.csv")
    test  = pd.read_csv(DATA + "test.csv")
    cc    = pd.read_csv(DATA + "chief_complaints.csv")   # patient_id, chief_complaint_raw, chief_complaint_system
    ph    = pd.read_csv(DATA + "patient_history.csv")    # patient_id + 25 hx_* flags

    # drop the chief_complaint_system duplicate that already lives in train/test
    cc = cc.drop(columns=["chief_complaint_system"])     # keep raw text only
    for df in (train, test):
        pass
    train = train.merge(cc, on="patient_id", how="left").merge(ph, on="patient_id", how="left")
    test  = test.merge(cc,  on="patient_id", how="left").merge(ph, on="patient_id", how="left")
    return train, test


def clean(df):
    df = df.copy()
    df.loc[df["pain_score"] < 0,       "pain_score"]    = np.nan   # sentinel −1 → NaN
    if "pulse_pressure" in df.columns:
        df.loc[df["pulse_pressure"] < 0, "pulse_pressure"] = np.nan   # impossible negatives
    return df


# ── Feature matrix builder ──────────────────────────────────────────────────
DROP_ALWAYS = ["patient_id", TARGET] + LEAKAGE + ["chief_complaint_raw"]
# chief_complaint_system is a category → keep, convert to 'category' dtype

def build_features(train_df):
    """Return X (feature matrix) and y (target) from the training dataframe."""
    feature_cols = [c for c in train_df.columns if c not in DROP_ALWAYS]
    X = train_df[feature_cols].copy()

    # Convert all object columns to pandas 'category' dtype so LightGBM handles
    # them natively without one-hot encoding (faster, handles unseen values gracefully).
    for col in X.select_dtypes(include="object").columns:
        X[col] = X[col].astype("category")

    y = train_df[TARGET].values   # int 1–5
    return X, y, feature_cols


# ── ECE helper ─────────────────────────────────────────────────────────────
def expected_calibration_error(y_true, probs, n_bins=10):
    """
    Multiclass ECE: average over classes of the per-class binary ECE.
    probs shape (N, K); y_true shape (N,) with values in 1..K.
    """
    n_classes = probs.shape[1]
    ece_per_class = []
    for k in range(n_classes):
        label_k  = (y_true == (k + 1)).astype(float)   # 1-vs-rest
        prob_k   = probs[:, k]
        bins     = np.linspace(0, 1, n_bins + 1)
        ece_k    = 0.0
        for lo, hi in zip(bins[:-1], bins[1:]):
            mask = (prob_k >= lo) & (prob_k < hi)
            if mask.sum() == 0:
                continue
            ece_k += (mask.sum() / len(y_true)) * abs(label_k[mask].mean() - prob_k[mask].mean())
        ece_per_class.append(ece_k)
    return float(np.mean(ece_per_class))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("Pillar A — Calibrated Triage-Acuity Model")
print("=" * 70)

# 1. Load & clean ─────────────────────────────────────────────────────────────
print("\n[1] Loading and cleaning data …")
train_raw, _ = load()
train_df      = clean(train_raw)
print(f"    train shape after join+clean: {train_df.shape}")

X, y, feature_cols = build_features(train_df)
print(f"    feature matrix: {X.shape[1]} columns")
print(f"    target distribution:\n{pd.Series(y).value_counts().sort_index().to_string()}")

# Keep leakage cols for outcome-validation (never in feature matrix X)
outcome_df = train_df[["disposition", "ed_los_hours"]].copy()

# 2. StratifiedKFold LightGBM ─────────────────────────────────────────────────
print("\n[2] StratifiedKFold(5) LightGBM multiclass OOF training …")
n_classes  = 5
skf        = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
oof_preds  = np.zeros(len(y), dtype=int)          # predicted class
oof_probs  = np.zeros((len(y), n_classes))        # predicted probabilities
fold_models = []                                  # store trained models per fold

lgb_params = dict(
    objective       = "multiclass",
    num_class       = n_classes,
    num_leaves      = 127,
    learning_rate   = 0.05,
    n_estimators    = 500,
    min_child_samples = 20,
    subsample       = 0.8,
    colsample_bytree= 0.8,
    random_state    = RANDOM_STATE,
    verbose         = -1,
    n_jobs          = -1,
)

# LightGBM needs categorical columns flagged explicitly when using category dtype
cat_features = [c for c in X.columns if X[c].dtype.name == "category"]
print(f"    categorical features ({len(cat_features)}): {cat_features}")

for fold, (tr_idx, va_idx) in enumerate(skf.split(X, y), 1):
    X_tr, X_va = X.iloc[tr_idx], X.iloc[va_idx]
    y_tr, y_va = y[tr_idx], y[va_idx]

    model = lgb.LGBMClassifier(**lgb_params)
    model.fit(
        X_tr, y_tr,
        eval_set=[(X_va, y_va)],
        callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(-1)],
        categorical_feature=cat_features,
    )

    proba = model.predict_proba(X_va)          # (N_val, 5)
    pred  = proba.argmax(axis=1) + 1           # map 0-indexed → 1-based

    oof_probs[va_idx] = proba
    oof_preds[va_idx] = pred
    fold_models.append(model)

    fold_acc = accuracy_score(y_va, pred)
    print(f"    Fold {fold}: acc={fold_acc:.4f}  n_estimators={model.best_iteration_}")

# 3. OOF Metrics ──────────────────────────────────────────────────────────────
print("\n[3] OOF Metrics …")
acc      = accuracy_score(y, oof_preds)
mac_f1   = f1_score(y, oof_preds, average="macro")
qwk      = cohen_kappa_score(y, oof_preds, weights="quadratic")
per_cls  = recall_score(y, oof_preds, average=None, labels=[1,2,3,4,5])
cm       = confusion_matrix(y, oof_preds, labels=[1,2,3,4,5])

print(f"  Accuracy        : {acc:.4f}")
print(f"  Macro-F1        : {mac_f1:.4f}")
print(f"  Quadratic WK    : {qwk:.4f}")
print(f"  Per-class recall (L1..L5): " +
      " | ".join(f"L{i+1}={r:.4f}" for i, r in enumerate(per_cls)))
print(f"  *** Safety recall L1={per_cls[0]:.4f}, L2={per_cls[1]:.4f} ***")
print(f"\n  Confusion matrix (rows=true, cols=pred, labels=1..5):")
cm_df = pd.DataFrame(cm, index=[f"True {i}" for i in range(1,6)],
                     columns=[f"Pred {i}" for i in range(1,6)])
print(cm_df.to_string())

# Save confusion matrix plot
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks(range(5)); ax.set_yticks(range(5))
ax.set_xticklabels([f"Pred {i}" for i in range(1,6)], fontsize=9)
ax.set_yticklabels([f"True {i}" for i in range(1,6)], fontsize=9)
for r in range(5):
    for c in range(5):
        ax.text(c, r, str(cm[r, c]), ha="center", va="center",
                color="white" if cm[r,c] > cm.max()*0.5 else "black", fontsize=8)
ax.set_title("OOF Confusion Matrix — Pillar A", fontsize=12)
ax.set_xlabel("Predicted acuity"); ax.set_ylabel("True acuity")
plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig("pa_confusion_matrix.png", dpi=120)
plt.close()
print("\n  [saved] pa_confusion_matrix.png")

# 4. Calibration ──────────────────────────────────────────────────────────────
print("\n[4] Calibration analysis …")

ece_before = expected_calibration_error(y, oof_probs)
print(f"  ECE (before calibration): {ece_before:.5f}")

# Isotonic calibration: refit per-fold on the OOF hold-out slice itself
# (use the OOF probs as input to a simple post-hoc isotonic regression per class)
from sklearn.isotonic import IsotonicRegression

oof_probs_cal = oof_probs.copy()
for k in range(n_classes):
    label_k = (y == (k + 1)).astype(float)
    ir = IsotonicRegression(out_of_bounds="clip")
    ir.fit(oof_probs[:, k], label_k)
    oof_probs_cal[:, k] = ir.transform(oof_probs[:, k])

# re-normalise rows
row_sums = oof_probs_cal.sum(axis=1, keepdims=True)
row_sums = np.where(row_sums == 0, 1, row_sums)
oof_probs_cal /= row_sums

ece_after  = expected_calibration_error(y, oof_probs_cal)
print(f"  ECE (after  calibration): {ece_after:.5f}")
print(f"  ECE improvement: {ece_before - ece_after:.5f}")

# Reliability diagram (per-class overlay, before vs after, class 1 & 2 highlighted)
fig, axes = plt.subplots(2, 3, figsize=(13, 8))
axes = axes.flatten()
colors_b = ["#d62728","#1f77b4","#2ca02c","#ff7f0e","#9467bd"]   # before
colors_a = ["#ffaaaa","#aec7e8","#98df8a","#ffbb78","#c5b0d5"]   # after

for k in range(n_classes):
    ax     = axes[k]
    label_k = (y == (k + 1)).astype(float)
    frac_b, mean_b = calibration_curve(label_k, oof_probs[:, k],    n_bins=10, strategy="uniform")
    frac_a, mean_a = calibration_curve(label_k, oof_probs_cal[:, k], n_bins=10, strategy="uniform")
    ax.plot([0,1],[0,1], "k--", lw=1, label="Perfect")
    ax.plot(mean_b, frac_b, "o-", color=colors_b[k], label=f"Before (ECE={expected_calibration_error(y, oof_probs):.4f})", lw=1.5)
    ax.plot(mean_a, frac_a, "s-", color=colors_a[k], label=f"After  (ECE={expected_calibration_error(y, oof_probs_cal):.4f})", lw=1.5)
    ax.set_title(f"Class {k+1}{'  ← safety' if k<2 else ''}", fontsize=10, fontweight="bold" if k<2 else "normal")
    ax.set_xlabel("Mean predicted prob"); ax.set_ylabel("Fraction positives")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

# overall summary in last panel
ax = axes[5]
ax.axis("off")
summary_text = (
    f"Calibration Summary\n\n"
    f"ECE before: {ece_before:.5f}\n"
    f"ECE after:  {ece_after:.5f}\n"
    f"Improvement: {ece_before - ece_after:.5f}\n\n"
    f"Method: per-class isotonic\n"
    f"regression on OOF probabilities"
)
ax.text(0.1, 0.5, summary_text, fontsize=11, va="center", family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", fc="#f0f0f0"))
plt.suptitle("Reliability Diagrams — Before vs After Isotonic Calibration", fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig("pa_reliability_curves.png", dpi=120, bbox_inches="tight")
plt.close()
print("  [saved] pa_reliability_curves.png")

# 5. SHAP Rule Reverse-Engineering ────────────────────────────────────────────
print("\n[5] SHAP rule reverse-engineering …")

# Use first-fold model; subsample 2000 rows from its validation set for speed
fold1_model    = fold_models[0]
shap_idx       = list(skf.split(X, y))[0][1]   # validation indices of fold 1
shap_sample    = np.random.default_rng(RANDOM_STATE).choice(shap_idx, size=min(2000, len(shap_idx)), replace=False)
X_shap         = X.iloc[shap_sample]

explainer      = shap.TreeExplainer(fold1_model)
shap_values    = explainer.shap_values(X_shap)   # list of C arrays (N,F)  OR  ndarray (N,F,C)

# Global feature importance (mean |SHAP| across all classes and samples) → length == n_features
if isinstance(shap_values, list):
    mean_abs_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
else:
    sv_arr = np.abs(np.asarray(shap_values))
    mean_abs_shap = sv_arr.mean(axis=(0, 2)) if sv_arr.ndim == 3 else sv_arr.mean(axis=0)
mean_abs_shap = np.asarray(mean_abs_shap).ravel()
assert len(mean_abs_shap) == len(feature_cols), f"shap len {len(mean_abs_shap)} != feats {len(feature_cols)}"

# Normalize into a list of per-class (N, F) arrays for the per-class plots below
if isinstance(shap_values, list):
    shap_by_class = [np.asarray(sv) for sv in shap_values]
else:
    _sv = np.asarray(shap_values)
    shap_by_class = [_sv[:, :, c] for c in range(_sv.shape[2])] if _sv.ndim == 3 else [_sv]
shap_importance= pd.Series(mean_abs_shap, index=feature_cols).sort_values(ascending=False)

print("\n  Top-20 features by mean |SHAP|:")
print(shap_importance.head(20).round(4).to_string())

# Confirm age/bmi/weight/height ≈ 0
age_bmi_cols   = [c for c in ["age","bmi","weight_kg","height_cm"] if c in shap_importance.index]
print("\n  *** Age/BMI/body-size features (should be ≈ 0) ***")
for c in age_bmi_cols:
    print(f"    {c:20s}  |SHAP| = {shap_importance.get(c, 0.0):.6f}")

# Global importance bar chart (top 25)
top25 = shap_importance.head(25)
fig, ax = plt.subplots(figsize=(9, 6))
colors_bar = ["#d62728" if f in VITALS else "#1f77b4" for f in top25.index]
bars = ax.barh(top25.index[::-1], top25.values[::-1], color=colors_bar[::-1])
ax.set_xlabel("Mean |SHAP| (all classes)", fontsize=11)
ax.set_title("Global Feature Importance — Pillar A\n(red = vital sign, blue = other)", fontsize=12)
# annotate age/bmi if present in top 25
for bar, feat in zip(bars, top25.index[::-1]):
    if feat in age_bmi_cols:
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                "← ≈0", va="center", fontsize=8, color="gray")
plt.tight_layout()
plt.savefig("pa_shap_global.png", dpi=120)
plt.close()
print("  [saved] pa_shap_global.png")

# Per-class SHAP summary (beeswarm style via shap.summary_plot) — save one image per class 1 & 2
for cls_idx in [0, 1]:   # class 1 and 2 (most clinically critical)
    sv   = shap_by_class[cls_idx]   # (N_shap, n_features)
    fig, ax = plt.subplots(figsize=(9, 6))
    # Build a mini-summary as a barplot of top-15 features for this class
    cls_imp = pd.Series(np.abs(sv).mean(axis=0), index=feature_cols).sort_values(ascending=False).head(15)
    colors_cls = ["#d62728" if f in VITALS else "#1f77b4" for f in cls_imp.index]
    ax.barh(cls_imp.index[::-1], cls_imp.values[::-1], color=colors_cls[::-1])
    ax.set_xlabel(f"Mean |SHAP| — Class {cls_idx+1}", fontsize=11)
    ax.set_title(f"SHAP Importance for Class {cls_idx+1} (most critical)\n"
                 f"Top drivers: {', '.join(cls_imp.index[:3])}", fontsize=11)
    plt.tight_layout()
    plt.savefig(f"pa_shap_class{cls_idx+1}.png", dpi=120)
    plt.close()
    print(f"  [saved] pa_shap_class{cls_idx+1}.png")

top3_global   = list(shap_importance.head(3).index)
top3_class1   = list(pd.Series(np.abs(shap_by_class[0]).mean(axis=0),
                               index=feature_cols).sort_values(ascending=False).head(3).index)
print(f"\n  Top-3 global SHAP drivers : {top3_global}")
print(f"  Top-3 class-1 SHAP drivers: {top3_class1}")
print(f"  Age-blindness confirmed    : {all(shap_importance.get(c, 0) < 0.01 for c in age_bmi_cols)}")

# 6. Outcome Validation ───────────────────────────────────────────────────────
print("\n[6] Outcome validation (leakage-safe) …")

validation_df = pd.DataFrame({
    "predicted_acuity": oof_preds,
    "disposition"     : outcome_df["disposition"].values,
    "ed_los_hours"    : outcome_df["ed_los_hours"].values,
})

# Admit = any disposition that contains 'admit' or 'inpatient' (case-insensitive)
# Mortality = 'deceased'
# Use raw strings as provided in dataset
validation_df["admitted"] = validation_df["disposition"].str.lower().str.contains(
    r"admit|inpatient", na=False).astype(float)
validation_df["deceased"] = (validation_df["disposition"].str.lower() == "deceased").astype(float)

ov_table = (
    validation_df.groupby("predicted_acuity")
    .agg(
        n            = ("predicted_acuity", "count"),
        admit_rate   = ("admitted",    "mean"),
        mortality    = ("deceased",    "mean"),
        mean_los_hrs = ("ed_los_hours","mean"),
    )
    .round(4)
)
print(ov_table.to_string())

# Check monotonicity (admit rate and los should decrease from L1→L5)
admit_mono = all(ov_table["admit_rate"].iloc[i] >= ov_table["admit_rate"].iloc[i+1]
                 for i in range(len(ov_table)-1))
los_mono   = all(ov_table["mean_los_hrs"].iloc[i] >= ov_table["mean_los_hrs"].iloc[i+1]
                 for i in range(len(ov_table)-1))
print(f"\n  Admit-rate monotone (L1→L5): {admit_mono}")
print(f"  LOS monotone       (L1→L5): {los_mono}")

# Outcome validation plot
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
acuity_labels = [f"L{i}" for i in ov_table.index]

# Admit rate
axes[0].bar(acuity_labels, ov_table["admit_rate"]*100, color=["#d62728","#ff7f0e","#2ca02c","#1f77b4","#9467bd"])
axes[0].set_ylabel("Admission rate (%)", fontsize=11)
axes[0].set_title("Admit Rate by\nPredicted Acuity", fontsize=11)
axes[0].set_ylim(0, 100)
for i, v in enumerate(ov_table["admit_rate"]*100):
    axes[0].text(i, v+1.5, f"{v:.1f}%", ha="center", fontsize=9)

# Mortality
axes[1].bar(acuity_labels, ov_table["mortality"]*100, color=["#d62728","#ff7f0e","#2ca02c","#1f77b4","#9467bd"])
axes[1].set_ylabel("Mortality rate (%)", fontsize=11)
axes[1].set_title("Mortality Rate by\nPredicted Acuity", fontsize=11)
axes[1].set_ylim(0, max(ov_table["mortality"].max()*130, 1))
for i, v in enumerate(ov_table["mortality"]*100):
    axes[1].text(i, v + ov_table["mortality"].max()*0.03, f"{v:.2f}%", ha="center", fontsize=9)

# Mean LOS
axes[2].bar(acuity_labels, ov_table["mean_los_hrs"], color=["#d62728","#ff7f0e","#2ca02c","#1f77b4","#9467bd"])
axes[2].set_ylabel("Mean ED LOS (hours)", fontsize=11)
axes[2].set_title("Mean LOS by\nPredicted Acuity", fontsize=11)
for i, v in enumerate(ov_table["mean_los_hrs"]):
    axes[2].text(i, v+0.05, f"{v:.1f}h", ha="center", fontsize=9)

plt.suptitle("Outcome Validation Panel — Predicted Acuity vs Real Outcomes\n"
             "(leakage-safe: disposition/ed_los_hours used only here, never as features)",
             fontsize=11, y=1.02)
plt.tight_layout()
plt.savefig("pa_outcome_validation.png", dpi=120, bbox_inches="tight")
plt.close()
print("  [saved] pa_outcome_validation.png")

# 7. Serialize results ────────────────────────────────────────────────────────
print("\n[7] Saving pa_results.json …")

results = {
    "oof_accuracy"          : round(acc, 6),
    "oof_macro_f1"          : round(mac_f1, 6),
    "oof_quadratic_wk"      : round(qwk, 6),
    "per_class_recall"      : {f"L{i+1}": round(float(r), 6) for i, r in enumerate(per_cls)},
    "ece_before_calibration": round(ece_before, 6),
    "ece_after_calibration" : round(ece_after, 6),
    "ece_improvement"       : round(ece_before - ece_after, 6),
    "top3_global_shap"      : top3_global,
    "top3_class1_shap"      : top3_class1,
    "age_bmi_importance_near_zero": {
        c: round(float(shap_importance.get(c, 0.0)), 6) for c in age_bmi_cols
    },
    "outcome_validation"    : {
        f"L{acuity}": {
            "n"           : int(row["n"]),
            "admit_rate"  : round(float(row["admit_rate"]), 4),
            "mortality"   : round(float(row["mortality"]), 4),
            "mean_los_hrs": round(float(row["mean_los_hrs"]), 4),
        }
        for acuity, row in ov_table.iterrows()
    },
    "admit_rate_monotone"   : bool(admit_mono),
    "los_monotone"          : bool(los_mono),
    "figures"               : [
        "pa_confusion_matrix.png",
        "pa_reliability_curves.png",
        "pa_shap_global.png",
        "pa_shap_class1.png",
        "pa_shap_class2.png",
        "pa_outcome_validation.png",
    ],
    "n_features"            : int(X.shape[1]),
    "n_train_rows"          : int(len(y)),
    "lgb_params"            : lgb_params,
}

with open("pa_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("  [saved] pa_results.json")

# ── Final summary ────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("PILLAR A — COMPLETE")
print("=" * 70)
print(f"  OOF Accuracy   : {acc:.4f}")
print(f"  Macro-F1       : {mac_f1:.4f}")
print(f"  Quadratic WK   : {qwk:.4f}")
print(f"  Safety recall  : L1={per_cls[0]:.4f}  L2={per_cls[1]:.4f}")
print(f"  ECE before/after: {ece_before:.5f} → {ece_after:.5f}")
print(f"  Top SHAP drivers: {top3_global}")
print(f"  Age/BMI ≈ 0    : {age_bmi_cols}")
print(f"  Outcome validation monotone: admit={admit_mono} LOS={los_mono}")
print("=" * 70)
