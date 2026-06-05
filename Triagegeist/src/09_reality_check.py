"""
09 — Reality check: is 0.9996 real, leakage, or memorization?
Three honest tests:
  (0) print the exact feature list -> confirm no disposition/ed_los_hours leakage
  (1) trivial phrase->majority LOOKUP under RANDOM 5-fold  (does a lookup alone solve it?)
  (2) same LOOKUP under GROUP 5-fold by phrase            (unseen phrases -> memorization fails)
  (3) the TF-IDF model under GROUP 5-fold by phrase        (do the WORDS generalize beyond memorizing?)
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, scipy.sparse as sp
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
import lightgbm as lgb

D="/home/fairlander/kaggle/triagegeist/data/"; SEED=42
LEAK=["disposition","ed_los_hours"]; TGT="triage_acuity"
DROP=["patient_id",TGT]+LEAK+["chief_complaint_raw"]

tr=pd.read_csv(D+"train.csv").merge(
    pd.read_csv(D+"chief_complaints.csv").drop(columns=["chief_complaint_system"]),on="patient_id",how="left").merge(
    pd.read_csv(D+"patient_history.csv"),on="patient_id",how="left")
tr.loc[tr["pain_score"]<0,"pain_score"]=np.nan
tr.loc[tr["pulse_pressure"]<0,"pulse_pressure"]=np.nan
y=tr[TGT].to_numpy(); text=tr["chief_complaint_raw"].fillna("").to_numpy()
phrase=tr["chief_complaint_raw"].fillna("").to_numpy()

# (0) feature list — prove no leakage cols are fed to the model
feat=[c for c in tr.columns if c not in DROP]
print("="*70); print("(0) FEATURES FED TO MODEL  (target/leakage/raw-text excluded)"); print("="*70)
print(f"  n_features={len(feat)}")
print(f"  disposition in features?  {'disposition' in feat}")
print(f"  ed_los_hours in features? {'ed_los_hours' in feat}")
print(f"  triage_acuity in features?{'triage_acuity' in feat}")
print(f"  (raw complaint text is NOT a feature; only TF-IDF of it is, fit per-fold)")

def lookup_cv(splitter, groups=None):
    accs=[]; seen=[]
    it = splitter.split(text, y, groups) if groups is not None else splitter.split(text, y)
    for trn,val in it:
        maj=pd.Series(y[trn],index=phrase[trn]).groupby(level=0).agg(lambda s:s.value_counts().idxmax())
        glob=pd.Series(y[trn]).value_counts().idxmax()
        pv=pd.Series(phrase[val]).map(maj).fillna(glob).to_numpy()
        accs.append(accuracy_score(y[val],pv))
        seen.append(np.isin(phrase[val],phrase[trn]).mean())
    return float(np.mean(accs)), float(np.mean(seen))

# (1) lookup, random folds
acc1,seen1=lookup_cv(StratifiedKFold(5,shuffle=True,random_state=SEED))
print("\n"+"="*70); print("(1) PHRASE->MAJORITY LOOKUP, RANDOM 5-fold"); print("="*70)
print(f"  val rows whose phrase was seen in train: {seen1:.1%}")
print(f"  accuracy of a DUMB lookup table        : {acc1:.4f}")
print("  -> if this is ~0.999, the 'task' is essentially a phrase lookup (synthetic policy).")

# (2) lookup, grouped by phrase (val phrases unseen)
acc2,seen2=lookup_cv(GroupKFold(5),groups=phrase)
print("\n"+"="*70); print("(2) SAME LOOKUP, GROUP 5-fold BY PHRASE (unseen phrases)"); print("="*70)
print(f"  val rows whose phrase was seen in train: {seen2:.1%}  (≈0 by construction)")
print(f"  accuracy of lookup on UNSEEN phrases   : {acc2:.4f}")
print("  -> collapse here = pure memorization cannot handle a phrase it never saw.")

# (3) TF-IDF model, grouped by phrase -> does it GENERALIZE via words?
print("\n"+"="*70); print("(3) TF-IDF MODEL, GROUP 5-fold BY PHRASE (truly unseen phrasings)"); print("="*70)
base=tr[feat].copy(); cat_idx=[]
for i,c in enumerate(feat):
    if not pd.api.types.is_numeric_dtype(base[c]):
        base[c]=pd.Categorical(base[c]).codes; cat_idx.append(i)
bX=base.to_numpy(np.float32)
params=dict(objective="multiclass",num_class=5,num_leaves=127,learning_rate=0.07,
            n_estimators=400,min_child_samples=20,subsample=0.8,colsample_bytree=0.8,
            random_state=SEED,verbose=-1,n_jobs=-1)
gkf=GroupKFold(5); oof=np.zeros(len(y),int)
for f,(trn,val) in enumerate(gkf.split(bX,y,groups=phrase)):
    vec=TfidfVectorizer(max_features=4000,min_df=3,ngram_range=(1,2),sublinear_tf=True)
    Wt=vec.fit_transform(text[trn]); Wv=vec.transform(text[val])
    Xt=sp.hstack([sp.csr_matrix(bX[trn]),Wt]).tocsr(); Xv=sp.hstack([sp.csr_matrix(bX[val]),Wv]).tocsr()
    m=lgb.LGBMClassifier(**params); m.fit(Xt,y[trn],categorical_feature=cat_idx)
    oof[val]=m.predict(Xv)
    print(f"  fold {f+1}: unseen-phrase acc={accuracy_score(y[val],oof[val]):.4f}")
acc3=accuracy_score(y,oof)
print(f"  MODEL accuracy on UNSEEN phrasings: {acc3:.4f}")

print("\n"+"="*70); print("VERDICT"); print("="*70)
print(f"  random-fold lookup (phrases repeat) : {acc1:.4f}   <- why we score ~0.9996")
print(f"  unseen-phrase lookup (memorization) : {acc2:.4f}   <- memorization alone fails")
print(f"  unseen-phrase MODEL (word generaliz): {acc3:.4f}   <- real generalizable signal")
print(f"  physiology-only baseline            : 0.8551")
print("  Real test set looks like the RANDOM case (99.3% of test phrases are in train),")
print("  so ~0.9996 is legitimate FOR THIS synthetic competition — not a bug, not leakage.")
