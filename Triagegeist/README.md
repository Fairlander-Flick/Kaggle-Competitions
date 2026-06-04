# Triagegeist — Modeling, Red-Flag NLP & Equity Audit for ED Triage

A submission to the **Triagegeist** hackathon (Laitinen-Fredriksson Foundation): an AI decision-support
analysis for emergency-department triage. We treat the provided `triage_acuity` label as a *triage
policy* and do what a hospital clinical-AI team actually needs — **predict it, reverse-engineer the rule
it encodes, build a text-based safety net, and audit it for bias and inconsistency.**

> ⚕️ **Data is synthetic** (no PHI). We state this prominently: the acuity label is a near-deterministic
> physiological function, demographically unbiased and age-blind. We turn each such property into a
> teaching contrast with real-world ED data and a validated audit methodology, rather than hiding it.

📓 **Public Kaggle notebook (runs end-to-end):** https://www.kaggle.com/code/fairlanderflick/triagegeist-ed-triage-toolkit
📝 **Writeup:** [`writeup.md`](writeup.md)

---

## Three pillars

| Pillar | What it does | Headline result |
|---|---|---|
| **A — Calibrated acuity model** | LightGBM (5-fold OOF) → ESI acuity 1–5; isotonic calibration; SHAP rule reverse-engineering; leakage-safe outcome validation | **Acc 0.855 · macro-F1 0.870 · QWK 0.930**; safety recall **L1 0.92 / L2 0.97**; **ECE 0.0067 → 0.0014**; outcomes monotone (admit 71%→4%, mortality 8%→0%) |
| **B — Chief-complaint red-flag NLP** | TF-IDF + 15-pattern clinical lexicon over free-text complaints; honest marginal-lift analysis; subjective/objective split | 8/15 lexicon patterns = **100% high-acuity triggers**; text lift over vitals reported honestly (AUC 1.0 flagged as a synthetic artefact) |
| **C — Equity & reliability audit** | Reusable `NEWS2-residual` audit toolkit with **negative + positive controls**; inter-rater outlier detection; literature contrast | Null bias on provided data (all CIs ∋ 0); **positive control detects injected bias at effect size 0.05**; 1/50 outlier nurse flagged |

**Headline insight:** SHAP shows the synthetic triage policy is **age-blind** (mean |SHAP| ≈ 0 for age/BMI/
weight/height) — reassuring for fairness here, but the exact failure mode behind real-world geriatric
undertriage (>22%). The reusable audit toolkit (Pillar C) is the impact pathway: it runs unmodified on
**MIMIC-IV-ED** or a hospital's own triage logs.

## Reproduce

The entire analysis is one CPU-only Kaggle notebook, seed 42, no internet, ~15–18 min:

1. Open the [public notebook](https://www.kaggle.com/code/fairlanderflick/triagegeist-ed-triage-toolkit) and **Run All** (competition data auto-mounts at `/kaggle/input/competitions/triagegeist/`), **or**
2. Locally: the per-pillar source scripts in [`src/`](src/) reproduce each section. Requires `lightgbm`,
   `scikit-learn`, `shap`, `scipy`, `matplotlib`, `pandas`. Each expects the competition CSVs (adjust the
   `DATA` path at the top).

## Repository layout

```
triagegeist.ipynb   # the integrated, end-to-end notebook (the submission)
writeup.md          # ≤2000-word project writeup
src/
  00_eda.py                      # exploratory data analysis
  01_pillarA_acuity_model.py     # calibrated model + SHAP + outcome validation
  02_pillarB_nlp_redflag.py      # chief-complaint NLP red-flag flagger
  03_pillarC_equity_audit.py     # equity & inter-rater audit toolkit
figures/            # all generated figures
```

## Leakage protocol

`disposition` and `ed_los_hours` are post-triage outcomes absent from the test set. They are **never**
used as model features — only as independent validators that predicted acuity tracks real severity.

## Limitations

Synthetic data: deterministic physiological label, text-AUC≈1.0 encoding artefact, near-zero inter-rater
noise, no injected demographic bias. Findings are proof-of-concept; **external validation on MIMIC-IV-ED
and NHAMCS** (which carry the human-judgment residual, real text signal, and genuine disparities this data
lacks) is the necessary next step.

---
*Seed 42 · CPU-only · reproducible end-to-end. Built for the Triagegeist hackathon.*
