"""
Triagegeist EDA — runs on Kaggle kernel at /kaggle/input/triagegeist/
Outputs: eda_summary.json to working dir
"""

import json
import warnings
import numpy as np
import pandas as pd
from collections import Counter
from scipy import stats
from scipy.stats import spearmanr, f_oneway

warnings.filterwarnings("ignore")

DATA_DIR = "/kaggle/input/competitions/triagegeist/"

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 0: LOAD DATA ===")
print("="*70)
# =============================================================================

train = pd.read_csv(DATA_DIR + "train.csv")
test  = pd.read_csv(DATA_DIR + "test.csv")
cc    = pd.read_csv(DATA_DIR + "chief_complaints.csv")
ph    = pd.read_csv(DATA_DIR + "patient_history.csv")

print(f"train shape  : {train.shape}")
print(f"test shape   : {test.shape}")
print(f"cc shape     : {cc.shape}")
print(f"ph shape     : {ph.shape}")

# Merge everything
train_full = (train
    .merge(cc, on="patient_id", how="left", suffixes=("","_cc"))
    .merge(ph, on="patient_id", how="left", suffixes=("","_ph")))
test_full  = (test
    .merge(cc, on="patient_id", how="left", suffixes=("","_cc"))
    .merge(ph, on="patient_id", how="left", suffixes=("","_ph")))

print(f"train_full shape: {train_full.shape}")
print(f"test_full  shape: {test_full.shape}")

summary = {}

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 1: SHAPES, DTYPES, MISSINGNESS ===")
print("="*70)
# =============================================================================

def missingness_report(df, label):
    miss = (df.isnull().mean() * 100).round(2).sort_values(ascending=False)
    miss = miss[miss > 0]
    print(f"\n--- {label} missingness (>0%) ---")
    print(miss.to_string())
    return miss.to_dict()

train_miss = missingness_report(train_full, "train_full")
test_miss  = missingness_report(test_full,  "test_full")

summary["shapes"] = {
    "train": list(train.shape),
    "test":  list(test.shape),
    "cc":    list(cc.shape),
    "ph":    list(ph.shape),
    "train_full": list(train_full.shape),
    "test_full":  list(test_full.shape),
}
summary["missingness_train_pct"] = train_miss
summary["missingness_test_pct"]  = test_miss

dtype_counts = train_full.dtypes.astype(str).value_counts().to_dict()
print(f"\nDtype breakdown (train_full): {dtype_counts}")
summary["dtype_counts"] = dtype_counts

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 2: TARGET DISTRIBUTION ===")
print("="*70)
# =============================================================================

vc = train["triage_acuity"].value_counts().sort_index()
print(f"\ntriage_acuity value counts:\n{vc}")
pct = (vc / len(train) * 100).round(2)
print(f"\nPercentages:\n{pct}")
summary["target_distribution"] = vc.to_dict()
summary["target_distribution_pct"] = pct.to_dict()

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 3: NEWS2 vs ACUITY ===")
print("="*70)
# =============================================================================

if "news2_score" in train_full.columns:
    news2_col = "news2_score"
elif "news2_score_x" in train_full.columns:
    news2_col = "news2_score_x"
else:
    news2_col = None

if news2_col:
    n2 = train_full[news2_col].dropna()
    print(f"\nnews2_score describe:\n{n2.describe()}")

    # Bucket NEWS2: 0 = Low, 1-4 = Low-Medium, 5-6 = Medium, 7+ = High
    def news2_bucket(x):
        if pd.isna(x): return "Missing"
        x = float(x)
        if x == 0:   return "0_Low"
        if x <= 4:   return "1-4_LowMed"
        if x <= 6:   return "5-6_Medium"
        return "7+_High"

    train_full["news2_bucket"] = train_full[news2_col].apply(news2_bucket)

    crosstab = pd.crosstab(train_full["news2_bucket"], train_full["triage_acuity"])
    print(f"\nNEWS2 bucket × triage_acuity crosstab (counts):\n{crosstab}")
    crosstab_pct = crosstab.div(crosstab.sum(axis=1), axis=0).round(3) * 100
    print(f"\nRow-normalised (% across acuity levels):\n{crosstab_pct}")

    # Spearman correlation
    valid_mask = train_full[news2_col].notna() & train_full["triage_acuity"].notna()
    rho, pval = spearmanr(train_full.loc[valid_mask, news2_col],
                          train_full.loc[valid_mask, "triage_acuity"])
    print(f"\nSpearman corr(NEWS2, acuity): rho={rho:.4f}  p={pval:.2e}")

    # Ordinal mapping accuracy: map NEWS2 to an expected acuity using median acuity per NEWS2 value
    news2_to_acuity = (train_full.groupby(news2_col)["triage_acuity"]
                       .median().round().astype(int))
    train_full["news2_pred_acuity"] = train_full[news2_col].map(news2_to_acuity)
    acc = (train_full["news2_pred_acuity"] == train_full["triage_acuity"]).mean()
    print(f"\nNEWS2-median-mapping exact accuracy vs actual acuity: {acc:.4f} ({acc*100:.2f}%)")

    # Residual: actual - news2_expected_median
    train_full["news2_pred_float"] = train_full[news2_col].map(
        train_full.groupby(news2_col)["triage_acuity"].mean())
    train_full["acuity_residual"] = train_full["triage_acuity"] - train_full["news2_pred_float"]
    res_std = train_full["acuity_residual"].std()
    print(f"Residual (actual - NEWS2-expected) std: {res_std:.4f}")

    # Cases where human acuity disagrees with NEWS2 by >=2 levels
    high_news2_low_acuity = ((train_full[news2_col] >= 7) & (train_full["triage_acuity"] >= 4)).sum()
    low_news2_high_acuity = ((train_full[news2_col] <= 2) & (train_full["triage_acuity"] <= 2)).sum()
    print(f"\nHigh NEWS2 (>=7) but low acuity (4-5) [over-NEWS2-ed]: {high_news2_low_acuity}")
    print(f"Low NEWS2 (<=2) but high acuity (1-2) [under-NEWS2-ed]: {low_news2_high_acuity}")

    summary["news2"] = {
        "spearman_rho": round(float(rho), 4),
        "spearman_pval": float(pval),
        "news2_mapping_accuracy": round(float(acc), 4),
        "residual_std": round(float(res_std), 4),
        "high_news2_low_acuity": int(high_news2_low_acuity),
        "low_news2_high_acuity": int(low_news2_high_acuity),
        "crosstab_pct": crosstab_pct.to_dict(),
    }
else:
    print("WARNING: news2_score not found in merged train_full columns")
    summary["news2"] = {"error": "column not found"}

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 4: NUMERIC VITALS — DESCRIBE + MEAN BY ACUITY + FEATURE IMPORTANCE ===")
print("="*70)
# =============================================================================

numeric_vitals = [c for c in [
    "systolic_bp","diastolic_bp","mean_arterial_pressure","pulse_pressure",
    "heart_rate","respiratory_rate","temperature_c","spo2","gcs_total",
    "pain_score","shock_index","news2_score","weight_kg","height_cm","bmi",
    "num_prior_ed_visits_12m","num_prior_admissions_12m",
    "num_active_medications","num_comorbidities","age"
] if c in train_full.columns]

# also check for suffixed versions
for base in ["news2_score"]:
    for suf in ["_x","_y"]:
        cand = base+suf
        if cand in train_full.columns and base not in numeric_vitals:
            numeric_vitals.append(cand)

print(f"\nNumeric vitals found: {numeric_vitals}")

desc = train_full[numeric_vitals].describe().T
print(f"\nDescribe:\n{desc.to_string()}")
summary["vitals_describe"] = {
    col: train_full[col].describe().to_dict() for col in numeric_vitals
    if col in train_full.columns
}

# Mean by acuity
mean_by_acuity = train_full.groupby("triage_acuity")[numeric_vitals].mean().round(3)
print(f"\nMean vitals by acuity level:\n{mean_by_acuity.to_string()}")
summary["vitals_mean_by_acuity"] = mean_by_acuity.to_dict()

# ANOVA F-statistic to rank feature importance vs acuity
f_stats = {}
for col in numeric_vitals:
    groups = [train_full.loc[train_full["triage_acuity"]==a, col].dropna().values
              for a in sorted(train_full["triage_acuity"].unique())]
    groups = [g for g in groups if len(g) > 1]
    if len(groups) >= 2:
        try:
            f_val, p_val = f_oneway(*groups)
            f_stats[col] = {"F": round(float(f_val), 2), "p": float(p_val)}
        except Exception:
            pass

f_sorted = sorted(f_stats.items(), key=lambda x: -x[1]["F"])
print(f"\nANOVA F-statistic ranking (feature vs triage_acuity):")
for feat, vals in f_sorted:
    print(f"  {feat:40s}  F={vals['F']:12.1f}  p={vals['p']:.2e}")
summary["anova_f_by_acuity"] = {k: v for k, v in f_sorted}

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 5: BIAS SIGNALS — PROTECTED ATTRIBUTES ===")
print("="*70)
# =============================================================================

protected = [c for c in ["language","insurance_type","age_group","sex"]
             if c in train_full.columns]

bias_results = {}
for attr in protected:
    print(f"\n--- {attr} ---")
    grp = train_full.groupby(attr)
    mean_ac   = grp["triage_acuity"].mean().round(4)
    high_ac   = (train_full["triage_acuity"] <= 2).astype(int)
    rate_high = grp.apply(lambda df: (df["triage_acuity"] <= 2).mean()).round(4)
    n_grp     = grp.size()
    dist_ac   = grp["triage_acuity"].value_counts(normalize=True).unstack(fill_value=0).round(4)

    print(f"  Mean acuity by {attr}:\n{mean_ac.to_string()}")
    print(f"  High-acuity rate (1-2) by {attr}:\n{rate_high.to_string()}")
    print(f"  N by group:\n{n_grp.to_string()}")

    # Bias-adjusted residual: residual vs NEWS2-expected, mean by group
    if "acuity_residual" in train_full.columns:
        res_by_grp = train_full.groupby(attr)["acuity_residual"].mean().round(4)
        print(f"  Mean acuity_residual (actual-NEWS2expected) by {attr}:\n{res_by_grp.to_string()}")
        bias_results[attr] = {
            "mean_acuity":    mean_ac.to_dict(),
            "high_acuity_rate": rate_high.to_dict(),
            "n":              n_grp.to_dict(),
            "residual_mean":  res_by_grp.to_dict(),
        }
    else:
        bias_results[attr] = {
            "mean_acuity":    mean_ac.to_dict(),
            "high_acuity_rate": rate_high.to_dict(),
            "n":              n_grp.to_dict(),
        }

summary["bias_signals"] = bias_results

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 6: INTER-RATER VARIABILITY — NURSE ID ===")
print("="*70)
# =============================================================================

if "triage_nurse_id" in train_full.columns:
    nurse_grp = train_full.groupby("triage_nurse_id")
    nurse_mean_ac = nurse_grp["triage_acuity"].mean().round(4)
    print(f"\nNurse mean acuity — describe:\n{nurse_mean_ac.describe().to_string()}")
    print(f"Variance in nurse mean acuity: {nurse_mean_ac.var():.6f}")

    if "acuity_residual" in train_full.columns:
        nurse_residual = train_full.groupby("triage_nurse_id")["acuity_residual"].mean().round(4)
        top5_hot   = nurse_residual.nsmallest(5)   # most negative = assigns lower acuity than NEWS2 implies (hotter = lower number = more urgent)
        top5_cold  = nurse_residual.nlargest(5)    # most positive = assigns higher acuity than NEWS2 implies (colder)
        print(f"\nTop 5 nurses with LOWEST residual (assign more urgent than NEWS2 implies):\n{top5_hot.to_string()}")
        print(f"\nTop 5 nurses with HIGHEST residual (assign less urgent than NEWS2 implies):\n{top5_cold.to_string()}")
        summary["inter_rater"] = {
            "nurse_mean_acuity_var": round(float(nurse_mean_ac.var()), 6),
            "nurse_mean_acuity_std": round(float(nurse_mean_ac.std()), 6),
            "nurse_residual_mean_min": round(float(nurse_residual.min()), 4),
            "nurse_residual_mean_max": round(float(nurse_residual.max()), 4),
            "nurse_residual_std": round(float(nurse_residual.std()), 6),
            "top5_hot_nurses": top5_hot.to_dict(),
            "top5_cold_nurses": top5_cold.to_dict(),
        }
    else:
        summary["inter_rater"] = {
            "nurse_mean_acuity_var": round(float(nurse_mean_ac.var()), 6),
        }
else:
    print("WARNING: triage_nurse_id not in columns")
    summary["inter_rater"] = {"error": "column not found"}

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 7: LEAKAGE CONFIRMATION — disposition & ed_los_hours ===")
print("="*70)
# =============================================================================

if "disposition" in train_full.columns:
    disp_by_ac = train_full.groupby("triage_acuity")["disposition"].value_counts(normalize=True).unstack(fill_value=0).round(4)
    print(f"\nDisposition distribution by acuity:\n{disp_by_ac.to_string()}")
    # admission rate = anything NOT discharge
    if "discharge" in train_full["disposition"].str.lower().values or True:
        admit_cols = [c for c in disp_by_ac.columns if "admit" in c.lower() or "icu" in c.lower() or "hospital" in c.lower()]
        if admit_cols:
            admit_rate = disp_by_ac[admit_cols].sum(axis=1)
            print(f"\nAdmission rate by acuity:\n{admit_rate.to_string()}")
            summary["leakage_validation"] = {
                "disposition_by_acuity": disp_by_ac.to_dict(),
                "admit_rate_by_acuity": admit_rate.to_dict(),
            }
        else:
            print(f"Unique dispositions: {train_full['disposition'].unique()}")
            summary["leakage_validation"] = {
                "disposition_by_acuity": disp_by_ac.to_dict(),
                "unique_dispositions": list(train_full["disposition"].unique()),
            }
else:
    print("WARNING: disposition not in columns")
    summary["leakage_validation"] = {"error": "column not found"}

if "ed_los_hours" in train_full.columns:
    los_by_ac = train_full.groupby("triage_acuity")["ed_los_hours"].describe().round(3)
    print(f"\nED LOS (hours) by acuity:\n{los_by_ac.to_string()}")
    # Spearman corr between LOS and acuity (expect negative — higher acuity = lower number = longer stay)
    valid = train_full["ed_los_hours"].notna() & train_full["triage_acuity"].notna()
    rho_los, pval_los = spearmanr(train_full.loc[valid,"ed_los_hours"],
                                   train_full.loc[valid,"triage_acuity"])
    print(f"\nSpearman corr(ed_los_hours, acuity): rho={rho_los:.4f}  p={pval_los:.2e}")
    summary["leakage_validation"]["ed_los_by_acuity"] = los_by_ac.to_dict()
    summary["leakage_validation"]["ed_los_spearman_rho"] = round(float(rho_los), 4)

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 8: CHIEF COMPLAINT TEXT ANALYSIS ===")
print("="*70)
# =============================================================================

# Find raw text column
cc_text_col = None
for c in ["chief_complaint_raw","chief_complaint_text","complaint_raw","complaint_text"]:
    if c in train_full.columns:
        cc_text_col = c
        break
if cc_text_col is None:
    # check cc dataframe directly
    for c in cc.columns:
        if "raw" in c or "text" in c:
            cc_text_col = c
            print(f"Found cc text col in cc df: {cc_text_col}")
            break

print(f"CC columns in cc df: {cc.columns.tolist()}")
print(f"CC columns in train_full (cc-related): {[c for c in train_full.columns if 'complaint' in c.lower() or 'cc_' in c.lower()]}")

if cc_text_col and cc_text_col in train_full.columns:
    cc_series = train_full[cc_text_col].fillna("")
    lengths = cc_series.str.len()
    print(f"\nCC text length stats:\n{lengths.describe().to_string()}")

    # Top tokens overall
    all_tokens = " ".join(cc_series.str.lower().values)
    token_counts = Counter(all_tokens.split())
    # Remove stop words
    stopwords = {"the","a","an","and","or","in","of","with","to","for","is","was","on","at","by","from","has","have"}
    top_tokens = [(w,c) for w,c in token_counts.most_common(50) if w not in stopwords and len(w) > 2][:30]
    print(f"\nTop 30 tokens (overall):\n{top_tokens}")

    # Top tokens by acuity 1-2 (high acuity red flags)
    high_ac_cc = train_full.loc[train_full["triage_acuity"] <= 2, cc_text_col].fillna("")
    high_tokens = " ".join(high_ac_cc.str.lower().values)
    high_token_counts = Counter(high_tokens.split())
    top_high = [(w,c) for w,c in high_token_counts.most_common(50) if w not in stopwords and len(w) > 2][:30]
    print(f"\nTop 30 tokens in high-acuity (1-2) complaints:\n{top_high}")

    # Low acuity top tokens
    low_ac_cc = train_full.loc[train_full["triage_acuity"] >= 4, cc_text_col].fillna("")
    low_tokens = " ".join(low_ac_cc.str.lower().values)
    low_token_counts = Counter(low_tokens.split())
    top_low = [(w,c) for w,c in low_token_counts.most_common(50) if w not in stopwords and len(w) > 2][:30]
    print(f"\nTop 30 tokens in low-acuity (4-5) complaints:\n{top_low}")

    summary["chief_complaint"] = {
        "text_col": cc_text_col,
        "length_stats": lengths.describe().to_dict(),
        "top_tokens_overall": top_tokens[:20],
        "top_tokens_high_acuity": top_high[:20],
        "top_tokens_low_acuity": top_low[:20],
    }
else:
    # Try accessing from cc df columns
    print(f"cc df columns: {cc.columns.tolist()}")
    if "chief_complaint_raw" in cc.columns:
        cc_text_col_in_merged = "chief_complaint_raw"
        if cc_text_col_in_merged in train_full.columns:
            print("Found chief_complaint_raw in train_full")
        else:
            print(f"chief_complaint_raw NOT in train_full. Merged cols with 'complaint': {[c for c in train_full.columns if 'complaint' in c.lower()]}")
    summary["chief_complaint"] = {"error": f"text col not found, cc cols: {cc.columns.tolist()}, train_full complaint cols: [c for c in train_full.columns if 'complaint' in c.lower()]"}

# Chief complaint system × acuity
ccs_col = None
for c in ["chief_complaint_system","complaint_system"]:
    if c in train_full.columns:
        ccs_col = c
        break
    if c+"_x" in train_full.columns:
        ccs_col = c+"_x"
        break

if ccs_col:
    ccs_by_ac = pd.crosstab(train_full[ccs_col], train_full["triage_acuity"])
    print(f"\nChief complaint system × acuity (top rows):\n{ccs_by_ac.to_string()}")
    # High-acuity rate per system
    ccs_high_rate = ((ccs_by_ac[1] + ccs_by_ac.get(2, 0)) / ccs_by_ac.sum(axis=1)).sort_values(ascending=False)
    print(f"\nHigh-acuity rate by chief complaint system:\n{ccs_high_rate.to_string()}")
    summary["chief_complaint_system"] = {
        "high_acuity_rate_by_system": ccs_high_rate.to_dict(),
        "counts_by_system": ccs_by_ac.to_dict(),
    }

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 9: MENTAL STATUS + ARRIVAL MODE vs ACUITY ===")
print("="*70)
# =============================================================================

for cat_col in ["mental_status_triage","arrival_mode","site_id"]:
    if cat_col in train_full.columns:
        ct = pd.crosstab(train_full[cat_col], train_full["triage_acuity"], normalize="index").round(3)*100
        print(f"\n{cat_col} × acuity (row %):\n{ct.to_string()}")
        mean_by_cat = train_full.groupby(cat_col)["triage_acuity"].mean().sort_values()
        print(f"  Mean acuity by {cat_col}:\n{mean_by_cat.to_string()}")

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 10: COMORBIDITY FLAGS vs ACUITY ===")
print("="*70)
# =============================================================================

hx_cols = [c for c in train_full.columns if c.startswith("hx_")]
print(f"\nComorbidity flags found: {hx_cols}")
if hx_cols:
    hx_means = train_full.groupby("triage_acuity")[hx_cols].mean().round(4)
    print(f"\nMean comorbidity presence by acuity level:\n{hx_means.to_string()}")
    # F-stat for each
    hx_f = {}
    for col in hx_cols:
        groups = [train_full.loc[train_full["triage_acuity"]==a, col].dropna().values
                  for a in sorted(train_full["triage_acuity"].unique())]
        groups = [g for g in groups if len(g) > 1]
        if len(groups) >= 2:
            try:
                f_val, p_val = f_oneway(*groups)
                hx_f[col] = {"F": round(float(f_val), 2), "p": float(p_val)}
            except Exception:
                pass
    hx_f_sorted = sorted(hx_f.items(), key=lambda x: -x[1]["F"])
    print(f"\nComorbidity ANOVA F-stat ranking:")
    for feat, vals in hx_f_sorted[:10]:
        print(f"  {feat:35s}  F={vals['F']:10.1f}  p={vals['p']:.2e}")
    summary["comorbidity_f_stats"] = {k: v for k, v in hx_f_sorted}

# =============================================================================
print("\n" + "="*70)
print("=== SECTION 11: KEY SUMMARY STATISTICS ===")
print("="*70)
# =============================================================================

print(f"\nTarget distribution: {summary.get('target_distribution','N/A')}")
if "news2" in summary and "spearman_rho" in summary.get("news2",{}):
    print(f"NEWS2 Spearman rho vs acuity: {summary['news2']['spearman_rho']}")
    print(f"NEWS2 median-mapping accuracy: {summary['news2']['news2_mapping_accuracy']}")
    print(f"Residual std (human judgment beyond NEWS2): {summary['news2']['residual_std']}")
if "inter_rater" in summary and "nurse_mean_acuity_std" in summary.get("inter_rater",{}):
    print(f"Inter-rater variability — nurse mean acuity std: {summary['inter_rater']['nurse_mean_acuity_std']}")

# =============================================================================
# WRITE JSON
# =============================================================================

# Convert any non-serializable numpy types
def convert_np(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_np(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [convert_np(i) for i in obj]
    return obj

summary_clean = convert_np(summary)

with open("eda_summary.json", "w") as f:
    json.dump(summary_clean, f, indent=2, default=str)

print("\n\neda_summary.json written successfully.")
print("\n=== EDA COMPLETE ===\n")
