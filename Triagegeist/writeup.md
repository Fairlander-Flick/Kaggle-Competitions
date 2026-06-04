# Triagegeist: Modeling, Reverse-Engineering, and Auditing an Emergency Triage Policy
### A calibrated acuity model, an NLP red-flag safety net, and a reusable triage-equity audit toolkit

*Track: Triagegeist — AI in Emergency Triage. Public notebook + code repository linked below.*

---

## Clinical Problem Statement

Emergency department triage compresses a life-or-death judgment into ninety seconds. A nurse assigns each arriving patient an acuity level — in the Emergency Severity Index (ESI), Level 1 is *resuscitation* and Level 5 is *non-urgent* — under cognitive load, with incomplete information, in chronically understaffed rooms. The cardinal error is **undertriage**: under-prioritising a critically ill patient, which directly delays life-saving care. Undertriage is not a symmetric mistake. Overtriage wastes capacity; undertriage kills. The literature shows it is also *unequally distributed*: elderly patients face undertriage rates above 22%, patients with limited English proficiency are admitted at higher rates than their triage level predicts (OR 1.16), Black patients receive lower-acuity triage at equivalent severity (aOR 0.76), and women with atypical cardiac presentations are systematically under-recognised.

A triage decision-support tool that is merely *accurate* is therefore insufficient and potentially dangerous. To be trustworthy it must be **calibrated** (its confidence must mean something to a nurse), **interpretable** (its reasoning must be auditable), and **fair** (it must not encode the disparities above). We address all three. We treat the provided `triage_acuity` label as a *triage policy* and do what a hospital clinical-AI team would actually need: predict it, reverse-engineer the rule it encodes, build an independent text-based safety net, and — most importantly — build a reusable toolkit to **audit any triage policy for bias and inconsistency**.

## Methodology

**Data.** The competition provides synthetic Finnish ED data: 80,000 training and 20,000 test encounters joined on `patient_id`, with structured vitals, demographics, 25 comorbidity flags, free-text chief complaints, and post-triage outcomes (`disposition`, `ed_los_hours`). We state plainly that the data is synthetic; this shapes our interpretation throughout.

**Leakage protocol (non-negotiable).** `disposition` and `ed_los_hours` are post-triage outcomes absent from the test set. They are *never* used as model features. They appear only as independent validators of predicted acuity.

**Cross-validation.** All metrics are out-of-fold from `StratifiedKFold(5, shuffle=True, random_state=42)`. Level 1 is only 4% of cases, so stratification is essential to keep the safety-critical class represented in every fold. Every random process is seeded (42); the notebook runs end-to-end on a CPU-only Kaggle kernel in under twenty minutes.

**Pillar A — Calibrated acuity model.** A LightGBM multiclass model on vitals, comorbidities, utilisation, and chief-complaint system. We report accuracy, macro-F1, quadratic-weighted kappa, and *per-class recall* — emphasising L1–L2 recall as the safety metric. We measure Expected Calibration Error before and after **isotonic recalibration**, and use **SHAP** to recover the policy's implicit decision rule.

**Pillar B — NLP red-flag flagger.** TF-IDF (word + character n-grams) over `chief_complaint_raw`, plus a 15-pattern, clinically-grounded red-flag lexicon (thunderclap headache, cardiac arrest, aortic dissection, meningeal signs, …). We honestly quantify the *marginal* lift of text over vitals and split performance by subjective vs. objective complaint — the category where real-world bias concentrates.

**Pillar C — Equity & reliability audit.** Four reusable functions built around the **NEWS2 residual**: the gap between assigned acuity and the acuity expected from vital signs alone. A systematically positive residual for a subgroup is the operational signature of undertriage. We validate the toolkit with a **negative control** (the provided data) and a **positive control** (synthetically injecting known bias and measuring the detection threshold), and apply it across 50 nurses to surface inter-rater outliers.

## Results & Findings

**The model is accurate — and that is the least interesting result.** The calibrated model reaches 0.855 accuracy, 0.870 macro-F1, and **quadratic-weighted kappa 0.930**, with safety recall of **92% at L1** and **97% at L2**; errors concentrate on the clinically forgiving L3/L4/L5 boundary. Isotonic recalibration cuts ECE from **0.0067 to 0.0014**, making the model's probabilities safe to surface to a nurse.

**Reverse-engineering the policy.** SHAP attributes almost all signal to `gcs_total`, `pain_score`, and `news2_score`. Strikingly, **`age`, `BMI`, `weight`, and `height` carry essentially zero importance** (mean |SHAP| ≈ 0.007; ANOVA F for age = 0.53, p = 0.71). The synthetic triage policy is a *pure physiological function*. This is reassuring for fairness here, but clinically incomplete — and it is our sharpest teaching contrast: real geriatric patients are undertriaged *precisely because* compensated physiology hides severity, yet this policy would never learn that risk because it ignores age entirely.

**Outcome validation (leakage-safe).** Predicted acuity tracks real outcomes monotonically: admission rate falls 71% → 4% from L1 to L5, mortality 8% → 0%, mean length-of-stay 7.9h → 1.2h. The model captures genuine severity, not a label artefact.

**The NLP safety net, reported honestly.** Text-only ROC-AUC is ≈ 1.0 — but we flag this as a **synthetic artefact**: the generator embeds severity adjectives ("severe", "acute", "mild") directly into the complaint text. In real data we would expect 0.65–0.75. The marginal lift of text over the already near-perfect vitals model is small (+0.003 AUC), reported without apology. The lexicon's value is independent of AUC: 8 of 15 patterns fire with 100% high-acuity concentration — non-discretionary L1 triggers — providing a last-resort catch precisely where vitals can be deceptively normal.

**The equity audit — a validated null result.** Across language, insurance, age, and sex, every subgroup's NEWS2-residual falls within ±0.019 acuity units and every 95% bootstrap CI straddles zero: **no detectable bias**, exactly as expected for a physiology-only generator. Rather than treat this as a dead end, we prove the toolkit *works* with a positive control: injecting one-level undertriage into just 5% of one language cohort is reliably detected (effect size 0.05; residual +0.019, CI 0.013–0.025), while smaller effects correctly remain undetected. The audit is calibrated, not trigger-happy. Inter-rater analysis across 50 nurses (residual SD 0.014) flags one systematic outlier; in real data, where ESI κ is 0.71–0.91, the same plot would flag many.

## Limitations & Reproducibility

The dataset is synthetic, and four properties bound our claims: (1) the label is near-deterministic physiology, so accuracy is an upper bound, not a realistic benchmark; (2) the text AUC of 1.0 is an encoding artefact; (3) inter-rater variability is near-zero, unlike real triage; and (4) there is no demographic bias to find — our null audit result is a *property of the data*, not a statement about real EDs. We treat each limitation as a teaching contrast rather than hiding it.

Everything is reproducible: a single public Kaggle notebook, seed 42 throughout, CPU-only, no internet, standard libraries (LightGBM, scikit-learn, SHAP, SciPy), reading from `/kaggle/input/competitions/triagegeist/`. The leakage guarantee is enforced in code. The full source is mirrored in the linked GitHub repository.

## Impact & Future Work

The deliverable that matters is **Pillar C's audit toolkit**. Its four functions (`audit_by_group`, `inject_undertriage`, `audit_inter_rater`, and the literature-contrast builder) require only `triage_acuity`, `news2_score`, and `triage_nurse_id` columns, so they run **without modification** on MIMIC-IV-ED (~425k stays, identical triage schema) or a hospital's own triage logs. On real data they would (a) detect protected-attribute disparities, (b) quantify them in interpretable NEWS2-residual units, (c) flag individual nurses for targeted re-training, and (d) benchmark against the published literature — with a demonstrated detection floor (~0.05 acuity units) finer than any effect size documented in the disparity literature.

The immediate next step is external validation on MIMIC-IV-ED and NHAMCS, where the human-judgment residual, real text signal, and genuine demographic bias the synthetic data lacks will all be present — and where this toolkit is designed to find them.

---

*Notebook: `kaggle.com/code/fairlanderflick/triagegeist-ed-triage-toolkit` · Code: GitHub repository linked in submission · Seed 42 · CPU-only, reproducible end-to-end.*
