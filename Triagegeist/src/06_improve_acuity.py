"""
06 — Improved Triage-Acuity Model (feedback loop)
Triagegeist Kaggle Hackathon

Diagnosis: the original Pillar-A model DROPPED `chief_complaint_raw` and only saw the
14-way `chief_complaint_system` category (majority-class purity 0.36). But the raw
complaint text determines acuity with 0.9994 purity, and 99.3% of test complaints
appear in train. So the fix is principled (learn the real generative rule, not overfit):
feed the complaint text via in-fold TF-IDF (vocabulary fit on each fold's TRAIN only =>
no leakage) on top of the existing physiology features.

Honest metric = 5-fold OOF. Overfit guard = mean(train acc) - OOF acc gap reported.

Edit CONFIG between iterations.
"""
import json, time, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score, recall_score, confusion_matrix
import lightgbm as lgb

DATA = "/home/fairlander/kaggle/triagegeist/data/"
OUT  = Path("/home/fairlander/Code/Kaggle-Comp/Triagegeist/inspection"); OUT.mkdir(exist_ok=True)
SEED = 42
LEAKAGE = ["disposition", "ed_los_hours"]
TARGET  = "triage_acuity"
DROP_ALWAYS = ["patient_id", TARGET] + LEAKAGE + ["chief_complaint_raw"]

# ── CONFIG (tweak per iteration) ───────────────────────────────────────────
CFG = dict(
    use_text       = True,
    tfidf_max      = 4000,
    tfidf_min_df   = 3,
    tfidf_ngram    = (1, 2),
    tfidf_char     = False,      # add char n-grams (catches full-width punctuation/typos/unseen)
    char_ngram     = (3, 5),
    char_max       = 3000,
    num_leaves     = 127,
    learning_rate  = 0.07,
    n_estimators   = 600,
    early_stop     = 40,
    min_child      = 20,
    class_weight   = {1: 4.0, 2: 1.5, 3: 1.0, 4: 1.0, 5: 1.0},  # cost-sensitive: undertriage is costlier
    tag            = "iter3_safety_weight",
)

def load():
    train = pd.read_csv(DATA + "train.csv")
    cc = pd.read_csv(DATA + "chief_complaints.csv").drop(columns=["chief_complaint_system"])
    ph = pd.read_csv(DATA + "patient_history.csv")
    train = train.merge(cc, on="patient_id", how="left").merge(ph, on="patient_id", how="left")
    train.loc[train["pain_score"] < 0, "pain_score"] = np.nan
    if "pulse_pressure" in train.columns:
        train.loc[train["pulse_pressure"] < 0, "pulse_pressure"] = np.nan
    return train

def build_base(train):
    """Dense base matrix (physiology + categoricals as int codes). Returns X, cat_idx, cols."""
    feat = [c for c in train.columns if c not in DROP_ALWAYS]
    base = train[feat].copy()
    cat_idx = []
    for i, c in enumerate(feat):
        if not pd.api.types.is_numeric_dtype(base[c]):   # object/string/category -> codes
            base[c] = pd.Categorical(base[c]).codes      # -1 for NaN -> LGBM treats as missing
            cat_idx.append(i)
    X = base.to_numpy(dtype=np.float32)
    return X, cat_idx, feat

def run(cfg):
    t0 = time.time()
    print("=" * 70); print(f"ITERATION: {cfg['tag']}"); print("=" * 70)
    train = load()
    y = train[TARGET].to_numpy()
    base_X, cat_idx, feat = build_base(train)
    text = train["chief_complaint_raw"].fillna("").to_numpy()
    print(f"  rows={len(y)}  base_feats={base_X.shape[1]}  cat={len(cat_idx)}  use_text={cfg['use_text']}")

    n_classes = 5
    skf = StratifiedKFold(5, shuffle=True, random_state=SEED)
    oof_pred = np.zeros(len(y), dtype=int)
    oof_prob = np.zeros((len(y), n_classes))
    train_accs, vocab_sizes = [], []

    params = dict(objective="multiclass", num_class=n_classes, num_leaves=cfg["num_leaves"],
                  learning_rate=cfg["learning_rate"], n_estimators=cfg["n_estimators"],
                  min_child_samples=cfg["min_child"], subsample=0.8, colsample_bytree=0.8,
                  random_state=SEED, verbose=-1, n_jobs=-1)
    if cfg.get("class_weight"):
        params["class_weight"] = cfg["class_weight"]

    for fold, (tr, va) in enumerate(skf.split(base_X, y)):
        if cfg["use_text"]:
            vec = TfidfVectorizer(max_features=cfg["tfidf_max"], min_df=cfg["tfidf_min_df"],
                                  ngram_range=cfg["tfidf_ngram"], sublinear_tf=True, lowercase=True)
            Ttr = vec.fit_transform(text[tr]); Tva = vec.transform(text[va])
            mats_tr = [sp.csr_matrix(base_X[tr]), Ttr]
            mats_va = [sp.csr_matrix(base_X[va]), Tva]
            if cfg["tfidf_char"]:
                cvec = TfidfVectorizer(analyzer="char_wb", ngram_range=cfg["char_ngram"],
                                       max_features=cfg["char_max"], min_df=cfg["tfidf_min_df"])
                mats_tr.append(cvec.fit_transform(text[tr])); mats_va.append(cvec.transform(text[va]))
            Xtr = sp.hstack(mats_tr).tocsr(); Xva = sp.hstack(mats_va).tocsr()
            vocab_sizes.append(Ttr.shape[1])
        else:
            Xtr, Xva = base_X[tr], base_X[va]

        m = lgb.LGBMClassifier(**params)
        m.fit(Xtr, y[tr], eval_set=[(Xva, y[va])],
              callbacks=[lgb.early_stopping(cfg["early_stop"], verbose=False)],
              categorical_feature=cat_idx)
        p = m.predict_proba(Xva)
        oof_prob[va] = p; oof_pred[va] = p.argmax(1) + 1
        # overfit probe: train acc on a 8k subsample
        sub = np.random.default_rng(SEED).choice(len(tr), size=min(8000, len(tr)), replace=False)
        tr_acc = accuracy_score(y[tr][sub], m.predict(Xtr[sub]) if cfg["use_text"] else m.predict(Xtr[sub]))
        train_accs.append(tr_acc)
        print(f"  fold {fold+1}: OOF acc={accuracy_score(y[va], oof_pred[va]):.4f}  "
              f"train acc≈{tr_acc:.4f}  trees={m.best_iteration_}  vocab={vocab_sizes[-1] if cfg['use_text'] else 0}")

    acc = accuracy_score(y, oof_pred)
    mf1 = f1_score(y, oof_pred, average="macro")
    qwk = cohen_kappa_score(y, oof_pred, weights="quadratic")
    rec = recall_score(y, oof_pred, average=None, labels=[1,2,3,4,5])
    cm  = confusion_matrix(y, oof_pred, labels=[1,2,3,4,5])
    danger = int(((y <= 2) & (oof_pred > y)).sum())
    gap = float(np.mean(train_accs) - acc)

    print("\n  ── RESULTS ──────────────────────────────────────────────")
    print(f"  OOF accuracy : {acc:.4f}   (baseline physiology-only = 0.8551)")
    print(f"  macro-F1     : {mf1:.4f}")
    print(f"  quadratic WK : {qwk:.4f}")
    print(f"  per-class rec: " + " ".join(f"L{i+1}={r:.3f}" for i, r in enumerate(rec)))
    print(f"  dangerous undertriage (true L1/L2 under-rated): {danger}  (baseline 566)")
    print(f"  overfit gap  : train≈{np.mean(train_accs):.4f} - OOF {acc:.4f} = {gap:+.4f}")
    print(f"  confusion matrix (rows=true 1..5):")
    print(pd.DataFrame(cm, index=[f"T{i}" for i in range(1,6)],
                       columns=[f"P{i}" for i in range(1,6)]).to_string())
    print(f"  elapsed: {time.time()-t0:.0f}s")

    res = dict(tag=cfg["tag"], oof_accuracy=round(acc,4), macro_f1=round(mf1,4),
               qwk=round(qwk,4), per_class_recall={f"L{i+1}":round(float(r),4) for i,r in enumerate(rec)},
               dangerous_undertriage=danger, overfit_gap=round(gap,4),
               config={k:v for k,v in cfg.items()})
    log = OUT / "improve_log.jsonl"
    with open(log, "a") as f: f.write(json.dumps(res) + "\n")
    np.save(OUT / f"oof_pred_{cfg['tag']}.npy", oof_pred)
    np.save(OUT / f"oof_prob_{cfg['tag']}.npy", oof_prob)
    print(f"  [logged] {log}")
    return res

if __name__ == "__main__":
    run(CFG)
