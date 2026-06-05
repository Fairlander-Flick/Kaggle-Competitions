"""
05 — Model Inspection Table (human-eyes review)
Triagegeist Kaggle Hackathon

Reproduces the Pillar-A OOF predictions (LightGBM 5-fold, seed=42, identical
feature construction to 01_pillarA_acuity_model.py) and emits per-patient
review artifacts so a human can scroll the model's calls and spot bad ones:

  inspection/model_inspection_full.csv  — every training row, all key features + verdict
  inspection/model_errors.csv           — misclassified rows only
  inspection/model_inspection.html      — color-coded, sortable, filterable curated view

Acuity convention: 1 = MOST urgent (resus), 5 = LEAST urgent.
  pred > true  -> model rated patient LESS urgent than reality  -> UNDER-TRIAGE (dangerous)
  pred < true  -> model rated patient MORE urgent than reality  -> over-triage (over-cautious)
"""

import json, html, warnings
warnings.filterwarnings("ignore")
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix
import lightgbm as lgb

# ── Paths / constants (mirror 01_pillarA) ──────────────────────────────────
DATA      = "/home/fairlander/kaggle/triagegeist/data/"
OUT       = Path("/home/fairlander/Code/Kaggle-Comp/Triagegeist/inspection")
OUT.mkdir(exist_ok=True)
SEED      = 42
LEAKAGE   = ["disposition", "ed_los_hours"]
TARGET    = "triage_acuity"
DROP_ALWAYS = ["patient_id", TARGET] + LEAKAGE + ["chief_complaint_raw"]

# Columns surfaced in the human-review table (most clinically informative first)
SHOW_COLS = [
    "patient_id", "chief_complaint_raw", "chief_complaint_system",
    "age", "sex", "arrival_mode", "mental_status_triage",
    "news2_score", "gcs_total", "spo2", "heart_rate", "respiratory_rate",
    "systolic_bp", "temperature_c", "pain_score", "shock_index",
]

# ── Load + clean (identical to pipeline) ───────────────────────────────────
print("[1] load + clean")
train = pd.read_csv(DATA + "train.csv")
cc    = pd.read_csv(DATA + "chief_complaints.csv").drop(columns=["chief_complaint_system"])
ph    = pd.read_csv(DATA + "patient_history.csv")
train = train.merge(cc, on="patient_id", how="left").merge(ph, on="patient_id", how="left")
train.loc[train["pain_score"] < 0, "pain_score"] = np.nan
if "pulse_pressure" in train.columns:
    train.loc[train["pulse_pressure"] < 0, "pulse_pressure"] = np.nan
print(f"    train shape: {train.shape}")

feature_cols = [c for c in train.columns if c not in DROP_ALWAYS]
X = train[feature_cols].copy()
for col in X.select_dtypes(include="object").columns:
    X[col] = X[col].astype("category")
y = train[TARGET].values
cat_features = [c for c in X.columns if X[c].dtype.name == "category"]

# ── 5-fold OOF (identical params/seed) ─────────────────────────────────────
print("[2] 5-fold OOF LightGBM")
n_classes  = 5
n_features = len(feature_cols)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
oof_pred = np.zeros(len(y), dtype=int)
oof_prob = np.zeros((len(y), n_classes))
fold_id  = np.full(len(y), -1, dtype=int)   # which fold validated each row
fold_models = []

params = dict(objective="multiclass", num_class=n_classes, num_leaves=127,
              learning_rate=0.05, n_estimators=500, min_child_samples=20,
              subsample=0.8, colsample_bytree=0.8, random_state=SEED,
              verbose=-1, n_jobs=-1)

for fold, (tr, va) in enumerate(skf.split(X, y)):
    m = lgb.LGBMClassifier(**params)
    m.fit(X.iloc[tr], y[tr], eval_set=[(X.iloc[va], y[va])],
          callbacks=[lgb.early_stopping(50, verbose=False)],
          categorical_feature=cat_features)
    p = m.predict_proba(X.iloc[va])
    oof_prob[va] = p
    oof_pred[va] = p.argmax(1) + 1
    fold_id[va]  = fold
    fold_models.append(m)
    print(f"    fold {fold+1}: acc={accuracy_score(y[va], oof_pred[va]):.4f}")

acc = accuracy_score(y, oof_pred)
cm  = confusion_matrix(y, oof_pred, labels=[1, 2, 3, 4, 5])
print(f"    overall OOF acc={acc:.4f}")

# ── Assemble review dataframe ──────────────────────────────────────────────
print("[3] assemble review table")
conf   = oof_prob.max(1)                                   # confidence in its own call
p_true = oof_prob[np.arange(len(y)), y - 1]               # prob it gave the correct class
err    = oof_pred - y                                      # >0 under-triage, <0 over-triage

def verdict(e):
    if e == 0:  return "correct"
    return "UNDER-TRIAGE" if e > 0 else "over-triage"

rev = train[SHOW_COLS].copy()
rev["true_acuity"]  = y
rev["pred_acuity"]  = oof_pred
rev["error"]        = err
rev["abs_error"]    = np.abs(err)
rev["verdict"]      = [verdict(e) for e in err]
# dangerous = a genuinely sick patient (true 1/2) under-rated by the model
rev["danger"]       = ((rev["true_acuity"] <= 2) & (rev["error"] > 0)).astype(int)
rev["confidence"]   = conf.round(3)
rev["p_true_class"] = p_true.round(3)
rev["disposition"]  = train["disposition"].values
rev["ed_los_hours"] = train["ed_los_hours"].round(2).values

# round vitals/shock for readability
for c in ["shock_index", "temperature_c", "age"]:
    if c in rev.columns:
        rev[c] = pd.to_numeric(rev[c], errors="coerce").round(2)

# ── Curated set for the HTML (importance-ranked, capped for browser speed) ──
print("[4] build curated review set")
danger_rows = rev[rev["danger"] == 1]
big_rows    = rev[(rev["abs_error"] >= 2) & (rev["danger"] == 0)]
# confidently-wrong 1-step errors (model sure but wrong) — high review value
sure_wrong  = rev[(rev["abs_error"] == 1) & (rev["confidence"] >= 0.60)].sort_values(
    "confidence", ascending=False)
sample_ok   = rev[rev["verdict"] == "correct"].sample(
    min(250, (rev["verdict"] == "correct").sum()), random_state=SEED)

curated = pd.concat([
    danger_rows.sort_values(["abs_error", "confidence"], ascending=False),
    big_rows.sort_values(["abs_error", "confidence"], ascending=False),
    sure_wrong.head(1200),
    sample_ok,
]).drop_duplicates(subset="patient_id")
CAP = 4000
if len(curated) > CAP:
    # keep all danger + big, then fill remaining capacity
    keep = pd.concat([danger_rows, big_rows]).drop_duplicates(subset="patient_id")
    rest = curated[~curated["patient_id"].isin(keep["patient_id"])].head(CAP - len(keep))
    curated = pd.concat([keep, rest]).drop_duplicates(subset="patient_id")
print(f"    curated HTML rows: {len(curated)}")

# ── Per-prediction explanations: "what did we say & why" ───────────────────
# LightGBM pred_contrib gives per-feature, per-class margin contributions.
# For an error we rank features by (contrib_to_PRED − contrib_to_TRUE):
#   most positive  -> signals that pushed the model toward its (wrong) PRED
#   most negative  -> signals that argued for the TRUE class but were outweighed
print("[5] per-prediction explanations (LightGBM pred_contrib)")

def fmt_val(v):
    if pd.isna(v):                                   return "NaN"
    if isinstance(v, (bool, np.bool_)):              return str(int(v))
    if isinstance(v, (int, np.integer)):             return str(int(v))
    if isinstance(v, (float, np.floating)):
        return str(int(v)) if float(v).is_integer() else f"{v:.2f}"
    return str(v)

pid_loc   = train.columns.get_loc("patient_id")
need_idx  = np.union1d(np.where(rev["verdict"].values != "correct")[0],
                       curated.index.values)
why_pred_map, why_true_map = {}, {}

for fold in range(5):
    sel = need_idx[fold_id[need_idx] == fold]
    if len(sel) == 0:
        continue
    contrib = np.asarray(fold_models[fold].predict(X.iloc[sel], pred_contrib=True))
    contrib = contrib.reshape(len(sel), n_classes, n_features + 1)   # +1 = bias term
    for j, ridx in enumerate(sel):
        pc, tc = oof_pred[ridx] - 1, y[ridx] - 1
        cv  = contrib[j]
        pid = train.iat[ridx, pid_loc]
        if pc == tc:                                  # correct call
            c     = cv[pc, :n_features]
            order = np.argsort(c)[::-1]
            why_pred_map[pid] = "; ".join(
                f"{feature_cols[k]}={fmt_val(X.iat[ridx, k])} ({c[k]:+.2f})"
                for k in order[:3] if c[k] > 0)
            why_true_map[pid] = ""
        else:                                         # error
            diff = cv[pc, :n_features] - cv[tc, :n_features]
            asc_ = np.argsort(diff)
            why_pred_map[pid] = "; ".join(
                f"{feature_cols[k]}={fmt_val(X.iat[ridx, k])} ({diff[k]:+.2f})"
                for k in asc_[::-1][:3] if diff[k] > 0)
            why_true_map[pid] = "; ".join(
                f"{feature_cols[k]}={fmt_val(X.iat[ridx, k])} ({diff[k]:+.2f})"
                for k in asc_[:3] if diff[k] < 0)

# ── CSV outputs ────────────────────────────────────────────────────────────
print("[6] write CSVs")
full_cols = (["patient_id", "true_acuity", "pred_acuity", "verdict", "error",
              "danger", "confidence", "p_true_class", "disposition", "ed_los_hours"]
             + [c for c in SHOW_COLS if c != "patient_id"])
rev[full_cols].to_csv(OUT / "model_inspection_full.csv", index=False)

err_df = rev[rev["verdict"] != "correct"].sort_values(
    ["danger", "abs_error", "confidence"], ascending=[False, False, False]).copy()
err_df["why_pred_over_true"]     = err_df["patient_id"].map(why_pred_map)
err_df["why_true_underweighted"] = err_df["patient_id"].map(why_true_map)
err_df[full_cols + ["why_pred_over_true", "why_true_underweighted"]].to_csv(
    OUT / "model_errors.csv", index=False)
print(f"    full rows: {len(rev)}  | errors: {(rev['verdict']!='correct').sum()}"
      f"  | dangerous undertriage: {rev['danger'].sum()}")

# ── Render HTML ─────────────────────────────────────────────────────────────
print("[7] build HTML")

# ── Render HTML ────────────────────────────────────────────────────────────
ACUITY_DESC = {1: "1 · resus", 2: "2 · emergent", 3: "3 · urgent",
               4: "4 · less urgent", 5: "5 · non-urgent"}

cm_html = "<table class='cm'><tr><th></th>" + "".join(
    f"<th>pred {i}</th>" for i in range(1, 6)) + "<th>recall</th></tr>"
for i in range(5):
    row_tot = cm[i].sum()
    rec = cm[i, i] / row_tot if row_tot else 0
    cells = "".join(
        f"<td class='{'diag' if i==j else ''}'>{cm[i,j]}</td>" for j in range(5))
    cm_html += f"<tr><th>true {i+1}</th>{cells}<td>{rec:.1%}</td></tr>"
cm_html += "</table>"

n_err   = int((rev["verdict"] != "correct").sum())
n_under = int((rev["verdict"] == "UNDER-TRIAGE").sum())
n_over  = int((rev["verdict"] == "over-triage").sum())
n_dang  = int(rev["danger"].sum())

headers = ["chief complaint", "system", "age", "sex", "arrival", "mental",
           "TRUE", "PRED", "Δ", "conf", "p(true)", "news2", "gcs", "spo2",
           "hr", "rr", "sbp", "shock", "pain", "disposition"]
NCOL = len(headers)

def esc(v):
    return html.escape(str(v))

def row_html(r, k):
    cls = ({"correct": "ok", "UNDER-TRIAGE": "under", "over-triage": "over"})[r["verdict"]]
    if r["danger"] == 1:
        cls = "danger"
    cc_txt = esc(r["chief_complaint_raw"])
    pid    = r["patient_id"]
    def cell(v):
        if pd.isna(v): return "<td class='na'>·</td>"
        return f"<td>{esc(v)}</td>"

    main = (
        f"<tr class='r {cls}' data-verdict='{r['verdict']}' data-danger='{r['danger']}' "
        f"data-abserr='{r['abs_error']}' onclick='tog({k})'>"
        f"<td class='cc' title='{cc_txt}'>▸ {cc_txt}</td>"
        f"<td>{esc(r['chief_complaint_system'])}</td>"
        f"{cell(r['age'])}{cell(r['sex'])}{cell(r['arrival_mode'])}{cell(r['mental_status_triage'])}"
        f"<td class='num'>{ACUITY_DESC[r['true_acuity']]}</td>"
        f"<td class='num strong'>{ACUITY_DESC[r['pred_acuity']]}</td>"
        f"<td class='num err'>{r['error']:+d}</td>"
        f"<td class='num'>{r['confidence']:.2f}</td>"
        f"<td class='num'>{r['p_true_class']:.2f}</td>"
        f"{cell(r['news2_score'])}{cell(r['gcs_total'])}{cell(r['spo2'])}{cell(r['heart_rate'])}"
        f"{cell(r['respiratory_rate'])}{cell(r['systolic_bp'])}{cell(r['shock_index'])}{cell(r['pain_score'])}"
        f"<td>{esc(r['disposition'])}</td>"
        f"</tr>")

    wp = esc(why_pred_map.get(pid, "") or "—")
    wt = esc(why_true_map.get(pid, "") or "—")
    if r["verdict"] == "correct":
        why_block = (f"<div class='wp'><b>✔ Doğru sıraladı — bu kararın ana sürücüleri "
                     f"(L{r['pred_acuity']} lehine):</b> {wp}</div>")
    else:
        why_block = (
            f"<div class='wp'><b>▶ Model <u>L{r['pred_acuity']}</u> dedi (gerçek "
            f"<u>L{r['true_acuity']}</u>) — bu sinyaller modeli L{r['pred_acuity']}'e itti:</b> {wp}</div>"
            f"<div class='wt'><b>◀ L{r['true_acuity']} lehine olup ezilen sinyaller:</b> {wt}</div>")

    detail = (
        f"<tr class='d' id='d{k}' style='display:none'><td colspan='{NCOL}' class='detail'>"
        f"<div class='full'><b>Chief complaint:</b> {cc_txt}</div>"
        f"{why_block}"
        f"<div class='muted'>confidence={r['confidence']:.3f} · p(true L{r['true_acuity']})="
        f"{r['p_true_class']:.3f} · disposition={esc(r['disposition'])} · "
        f"ed_los={fmt_val(r['ed_los_hours'])}h &nbsp;|&nbsp; "
        f"news2={fmt_val(r['news2_score'])} gcs={fmt_val(r['gcs_total'])} "
        f"spo2={fmt_val(r['spo2'])} hr={fmt_val(r['heart_rate'])} "
        f"rr={fmt_val(r['respiratory_rate'])} sbp={fmt_val(r['systolic_bp'])} "
        f"shock={fmt_val(r['shock_index'])} pain={fmt_val(r['pain_score'])}</div>"
        f"<div class='hint'>(katkı ağırlıkları log-odds uzayında: +/− işaret ve sıralama yorumlanır)</div>"
        f"</td></tr>")
    return main + "\n" + detail

rows_html = "\n".join(row_html(r, k) for k, (_, r) in enumerate(curated.iterrows()))

thead = "".join(f"<th onclick='sortBy({i})'>{h}</th>" for i, h in enumerate(headers))

doc = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Triagegeist — Model Inspection</title>
<style>
 body{{font:13px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0f1115;color:#e6e6e6}}
 header{{padding:16px 20px;background:#161922;border-bottom:1px solid #2a2f3a;position:sticky;top:0;z-index:5}}
 h1{{margin:0 0 4px;font-size:18px}} .sub{{color:#9aa4b2;font-size:12px}}
 .stats{{display:flex;gap:18px;flex-wrap:wrap;margin-top:10px}}
 .stat{{background:#1c2029;border:1px solid #2a2f3a;border-radius:8px;padding:8px 12px}}
 .stat b{{font-size:18px;display:block}}
 .cm{{border-collapse:collapse;margin-top:10px;font-size:11px}}
 .cm th,.cm td{{border:1px solid #2a2f3a;padding:3px 7px;text-align:center}}
 .cm .diag{{background:#1b3a2b;font-weight:bold}}
 .legend{{margin-top:10px;font-size:12px}} .legend span{{padding:2px 8px;border-radius:4px;margin-right:8px}}
 .filters{{margin-top:12px}} .filters button{{background:#222733;color:#cbd3df;border:1px solid #353c4a;
   padding:5px 11px;border-radius:6px;cursor:pointer;margin-right:6px;font-size:12px}}
 .filters button.active{{background:#3b82f6;color:#fff;border-color:#3b82f6}}
 .wrap{{overflow:auto;max-height:calc(100vh - 230px)}}
 table.main{{border-collapse:collapse;width:100%;font-size:12px}}
 table.main th{{position:sticky;top:0;background:#1c2029;padding:6px 8px;text-align:left;
   border-bottom:2px solid #2a2f3a;cursor:pointer;white-space:nowrap;z-index:2}}
 table.main td{{padding:4px 8px;border-bottom:1px solid #20242e;white-space:nowrap}}
 td.cc{{max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
 td.num{{text-align:right;font-variant-numeric:tabular-nums}} td.strong{{font-weight:bold}}
 td.err{{font-weight:bold}} td.na{{color:#555;text-align:center}}
 tr.r{{cursor:pointer}}
 tr.ok{{}} tr.over{{background:#1a2740}} tr.under{{background:#3a2a1a}}
 tr.danger{{background:#4a1d1d}} tr.danger td.err{{color:#ff7676}}
 tr.r:hover{{filter:brightness(1.3)}}
 .pill-ok{{background:#1b3a2b}} .pill-over{{background:#1a2740}}
 .pill-under{{background:#3a2a1a}} .pill-danger{{background:#4a1d1d}}
 td.detail{{background:#13161d;white-space:normal;padding:10px 16px;border-bottom:2px solid #2a2f3a}}
 td.detail .full{{margin-bottom:6px}}
 td.detail .wp{{color:#ffd9a8;margin:3px 0}} td.detail .wp b{{color:#ffb061}}
 td.detail .wt{{color:#bfe6c8;margin:3px 0}} td.detail .wt b{{color:#7CFC9E}}
 td.detail .muted{{color:#8b94a3;margin-top:6px;font-size:11px;font-family:monospace}}
 td.detail .hint{{color:#5b6373;margin-top:2px;font-size:10px}}
</style></head><body>
<header>
 <h1>Triagegeist — Model Inspection Table</h1>
 <div class="sub">OOF predictions (LightGBM 5-fold, seed 42). Acuity 1 = most urgent … 5 = least urgent.
   &nbsp; <b>UNDER-TRIAGE</b> (pred &gt; true) = model under-rated patient = dangerous direction.</div>
 <div class="stats">
   <div class="stat"><b>{len(rev):,}</b>total patients</div>
   <div class="stat"><b>{acc:.1%}</b>overall accuracy</div>
   <div class="stat"><b>{n_err:,}</b>errors</div>
   <div class="stat"><b>{n_under:,}</b>under-triage</div>
   <div class="stat"><b>{n_over:,}</b>over-triage</div>
   <div class="stat"><b style="color:#ff7676">{n_dang:,}</b>dangerous (true&nbsp;1/2 under-rated)</div>
 </div>
 {cm_html}
 <div class="legend">
   <span class="pill-danger">dangerous undertriage</span>
   <span class="pill-under">under-triage</span>
   <span class="pill-over">over-triage</span>
   <span class="pill-ok">correct (sample)</span>
 </div>
 <div class="filters">
   <button class="active" onclick="filt(this,'all')">all ({len(curated):,})</button>
   <button onclick="filt(this,'danger')">dangerous only</button>
   <button onclick="filt(this,'UNDER-TRIAGE')">under-triage</button>
   <button onclick="filt(this,'over-triage')">over-triage</button>
   <button onclick="filt(this,'big')">|Δ|≥2</button>
   <button onclick="filt(this,'correct')">correct</button>
 </div>
 <div class="sub" style="margin-top:8px">👉 <b>Bir satıra tıkla</b> → modelin o vakada <b>ne dediği ve niye</b> dediği açılır
   (PRED'e iten sinyaller vs TRUE lehine ezilen sinyaller). Sütun başlığına tıkla → sırala.
   <br>Showing a clinically-ranked subset of {len(curated):,} rows
   (all dangerous + all |Δ|≥2 + confidently-wrong + a correct sample).
   The complete {len(rev):,}-row table is in <code>model_inspection_full.csv</code>;
   per-error "why" reasoning is in <code>model_errors.csv</code>.</div>
</header>
<div class="wrap"><table class="main" id="t">
<thead><tr>{thead}</tr></thead>
<tbody>
{rows_html}
</tbody></table></div>
<script>
const tb=document.querySelector('#t tbody');
function det(m){{ return document.getElementById('d'+m.getAttribute('onclick').match(/\\d+/)[0]); }}
function tog(k){{ const d=document.getElementById('d'+k);
  d.style.display = d.style.display==='table-row' ? 'none' : 'table-row'; }}
function filt(btn,mode){{
  document.querySelectorAll('.filters button').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  for(const m of tb.querySelectorAll('tr.r')){{
    let show = mode==='all' ? true
      : mode==='danger'  ? m.dataset.danger==='1'
      : mode==='big'     ? parseInt(m.dataset.abserr)>=2
      : mode==='correct' ? m.dataset.verdict==='correct'
      : m.dataset.verdict===mode;
    m.style.display = show?'':'none';
    det(m).style.display='none';                 // collapse detail when (un)filtering
  }}
}}
let asc=true,last=-1;
function sortBy(col){{
  const mains=[...tb.querySelectorAll('tr.r')]; asc=(col===last)?!asc:true; last=col;
  mains.sort((a,b)=>{{
    let x=a.cells[col].innerText.trim(), y=b.cells[col].innerText.trim();
    let nx=parseFloat(x.replace(/[^0-9.\\-]/g,'')), ny=parseFloat(y.replace(/[^0-9.\\-]/g,''));
    if(!isNaN(nx)&&!isNaN(ny)) return asc?nx-ny:ny-nx;
    return asc?x.localeCompare(y):y.localeCompare(x);
  }});
  const frag=document.createDocumentFragment();
  for(const m of mains){{ frag.appendChild(m); frag.appendChild(det(m)); }}
  tb.appendChild(frag);
}}
</script>
</body></html>"""

(OUT / "model_inspection.html").write_text(doc, encoding="utf-8")

# small summary json
json.dump({
    "oof_accuracy": round(float(acc), 4),
    "n_total": int(len(rev)),
    "n_errors": n_err, "n_under_triage": n_under, "n_over_triage": n_over,
    "n_dangerous_undertriage": n_dang,
    "confusion_matrix_true_rows": cm.tolist(),
}, open(OUT / "inspection_summary.json", "w"), indent=2)

print("[done] wrote:")
for f in ["model_inspection.html", "model_inspection_full.csv",
          "model_errors.csv", "inspection_summary.json"]:
    print("   inspection/" + f)
