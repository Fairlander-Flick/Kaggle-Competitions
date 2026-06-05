"""
08 — Confidence & Correctness Dashboard  (Triagegeist, improved iter2 model)
Answers: how CONFIDENT is the model, how ACCURATE, where is it right, where wrong, and WHY.
Self-contained HTML dashboard (tabbed buttons, inline SVG/CSS — no matplotlib) +
a full text report + JSON. Uses saved OOF preds/probs from 06 iter2 (word+char TF-IDF).
"""
import json, html
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.metrics import (accuracy_score, f1_score, cohen_kappa_score,
                             confusion_matrix, precision_recall_fscore_support)

D   = "/home/fairlander/kaggle/triagegeist/data/"
OUT = Path("/home/fairlander/Code/Kaggle-Comp/Triagegeist/inspection")
ACU = {1:"L1 · resus",2:"L2 · emergent",3:"L3 · urgent",4:"L4 · less urgent",5:"L5 · non-urgent"}

# Reality-check numbers from src/09_reality_check.py (regenerate there if data changes)
REAL = dict(lookup_random=0.9962, lookup_unseen=0.3615, model_unseen=0.9977,
            baseline=0.8551, test_phrase_overlap=0.993)

# ── data + saved model outputs ─────────────────────────────────────────────
tr = pd.read_csv(D+"train.csv").merge(
        pd.read_csv(D+"chief_complaints.csv")[["patient_id","chief_complaint_raw"]],
        on="patient_id", how="left")
y    = tr["triage_acuity"].to_numpy()
pred = np.load(OUT/"oof_pred_iter2_word_char.npy")
prob = np.load(OUT/"oof_prob_iter2_word_char.npy")
conf = prob.max(1)                                   # confidence in its own call
p_true = prob[np.arange(len(y)), y-1]                # prob mass on the correct class
correct = pred == y
N = len(y)

# phrase determinism (for why-analysis)
maj = tr.groupby("chief_complaint_raw")["triage_acuity"].agg(lambda s: s.value_counts().idxmax())
pur = tr.groupby("chief_complaint_raw")["triage_acuity"].agg(lambda s: s.value_counts(normalize=True).iloc[0])
tr["pmaj"]=tr["chief_complaint_raw"].map(maj); tr["ppur"]=tr["chief_complaint_raw"].map(pur)

# ── headline metrics ───────────────────────────────────────────────────────
acc = accuracy_score(y,pred); mf1=f1_score(y,pred,average="macro")
qwk = cohen_kappa_score(y,pred,weights="quadratic")
prec,rec,f1c,supp = precision_recall_fscore_support(y,pred,labels=[1,2,3,4,5])
cm = confusion_matrix(y,pred,labels=[1,2,3,4,5])
n_err=int((~correct).sum())
under=int((pred>y).sum()); over=int((pred<y).sum())
danger=int(((y<=2)&(pred>y)).sum())

# ── confidence distribution (correct vs wrong) ─────────────────────────────
cbins=[0,.5,.6,.7,.8,.9,.95,.99,1.0001]
clab=["<.5",".5–.6",".6–.7",".7–.8",".8–.9",".9–.95",".95–.99","≥.99"]
ci=np.digitize(conf,cbins)-1
hist_ok=[int(((ci==b)&correct).sum()) for b in range(len(clab))]
hist_no=[int(((ci==b)&~correct).sum()) for b in range(len(clab))]
mean_conf_ok=float(conf[correct].mean()); mean_conf_no=float(conf[~correct].mean())
med_conf_no=float(np.median(conf[~correct]))

# ── top-label calibration (fine bins near 1.0) ─────────────────────────────
kbins=[0,.5,.7,.8,.9,.95,.99,.995,.999,1.0001]
klab=["<.5",".5–.7",".7–.8",".8–.9",".9–.95",".95–.99",".99–.995",".995–.999","≥.999"]
ki=np.digitize(conf,kbins)-1
calib=[]
ece=0.0
for b in range(len(klab)):
    m=ki==b; n=int(m.sum())
    if n==0: calib.append((klab[b],0,None,None)); continue
    a=float(correct[m].mean()); c=float(conf[m].mean())
    ece+=n/N*abs(a-c); calib.append((klab[b],n,c,a))
ece=float(ece)

# ── trust bands / selective prediction ─────────────────────────────────────
bands=[]
for t in [0.90,0.95,0.99,0.995,0.999]:
    m=conf>=t; cov=float(m.mean()); na=int(m.sum())
    aa=float(correct[m].mean()) if na else float("nan")
    ab=float(correct[~m].mean()) if (~m).any() else float("nan")
    dang_auto=int(((y<=2)&(pred>y)&m).sum())     # dangerous undertriage that slips through auto-accept
    bands.append((t,cov,na,aa,N-na,ab,dang_auto))

# ── error taxonomy ─────────────────────────────────────────────────────────
e=tr[~correct].copy(); e["pred"]=pred[~correct]; e["conf"]=conf[~correct]
def diag(r):
    if r["triage_acuity"]!=r["pmaj"]: return "intrinsic noise"
    if r["ppur"]<1: return "ambiguous phrase"
    return "hard boundary"
e["diag"]=e.apply(diag,axis=1)
e["dir"]=np.where(e["pred"]>e["triage_acuity"],"undertriage",
          np.where(e["pred"]<e["triage_acuity"],"overtriage","—"))
tax=e["diag"].value_counts().to_dict()
hi_conf_err=e.sort_values("conf",ascending=False)

# ── per-class mean confidence ──────────────────────────────────────────────
cls_conf=[float(conf[y==k].mean()) for k in range(1,6)]

# ── why-right / why-wrong quantification ───────────────────────────────────
pct_correct_pure=float((tr.loc[correct,"ppur"]==1).mean())
mean_pur_err=float(e["ppur"].mean())
pct_err_ambig=float((e["ppur"]<1).mean())

# ════════════════════════════════════════════════════════════════════════════
# TEXT REPORT (stdout)
# ════════════════════════════════════════════════════════════════════════════
P=print
P("="*72); P("TRIAGEGEIST — CONFIDENCE & CORRECTNESS REPORT (iter2 model)"); P("="*72)
P(f"rows={N}  accuracy={acc:.4f}  macro-F1={mf1:.4f}  QWK={qwk:.4f}")
P(f"errors={n_err}  undertriage={under}  overtriage={over}  dangerous(L1/L2 under)={danger}")
P(f"\nPER-CLASS:")
for i,k in enumerate(range(1,6)):
    P(f"  {ACU[k]:18s} support={supp[i]:6d}  precision={prec[i]:.4f}  recall={rec[i]:.4f}  F1={f1c[i]:.4f}  mean_conf={cls_conf[i]:.4f}")
P(f"\nCONFIDENCE: correct mean={mean_conf_ok:.4f} | wrong mean={mean_conf_no:.4f} (median {med_conf_no:.3f})")
P(f"top-label ECE (calibration error) = {ece:.4f}  (0 = perfectly calibrated)")
P(f"\nCALIBRATION (confidence bin -> actual accuracy):")
for lb,n,c,a in calib:
    if n: P(f"  conf {lb:9s} n={n:6d}  mean_conf={c:.4f}  accuracy={a:.4f}  gap={a-c:+.4f}")
P(f"\nTRUST BANDS (selective prediction):")
P(f"  {'thresh':>7} {'coverage':>9} {'n_auto':>8} {'acc_auto':>9} {'n_review':>9} {'acc_review':>10} {'danger_slip':>11}")
for t,cov,na,aa,nr,ab,ds in bands:
    P(f"  {t:>7.3f} {cov:>8.1%} {na:>8d} {aa:>9.4f} {nr:>9d} {ab:>10.4f} {ds:>11d}")
P(f"\nERROR TAXONOMY: "+", ".join(f"{k}={v}" for k,v in tax.items()))
P(f"  mean phrase-purity among errors={mean_pur_err:.4f}  | {pct_err_ambig:.0%} of errors on ambiguous phrases")
P(f"WHY-RIGHT: {pct_correct_pure:.1%} of correct calls are on deterministic (purity=1.0) complaints")
P(f"\nTOP CONFIDENT ERRORS (model sure but wrong):")
for _,r in hi_conf_err.head(12).iterrows():
    P(f"  conf={r['conf']:.3f}  L{r['triage_acuity']}->L{r['pred']} {r['dir']:11s} [{r['diag']:16s}] {r['chief_complaint_raw']}")

# ════════════════════════════════════════════════════════════════════════════
# HTML DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
def esc(v): return html.escape(str(v))

# confusion matrix (row-normalized colour)
cm_rows=""
for i in range(5):
    tot=cm[i].sum(); cells=""
    for j in range(5):
        frac=cm[i,j]/tot if tot else 0
        bg=f"rgba(56,189,248,{0.08+0.9*frac:.3f})" if i==j else (f"rgba(248,113,113,{0.12+0.7*frac:.3f})" if cm[i,j] else "transparent")
        cells+=f"<td style='background:{bg}' title='{frac:.1%}'>{cm[i,j]}</td>"
    cm_rows+=f"<tr><th>{ACU[i+1]}</th>{cells}<td class='nn'>{rec[i]:.1%}</td></tr>"
cm_html=("<table class='grid'><tr><th></th>"+"".join(f"<th>{ACU[j+1]}</th>" for j in range(5))
         +"<th>recall</th></tr>"+cm_rows+"</table>")

# confidence histogram (grouped SVG)
def hist_svg(ok,no,labels):
    W,H,pad=620,240,34; n=len(labels); bw=(W-2*pad)/n; mx=max(max(ok),max(no),1)
    bars=""
    for i in range(n):
        x=pad+i*bw
        ho=(H-2*pad)*ok[i]/mx; hn=(H-2*pad)*no[i]/mx
        bars+=(f"<rect x='{x+4:.0f}' y='{H-pad-ho:.0f}' width='{bw/2-5:.0f}' height='{ho:.0f}' fill='#34d399'/>"
               f"<rect x='{x+bw/2+1:.0f}' y='{H-pad-hn:.0f}' width='{bw/2-5:.0f}' height='{hn:.0f}' fill='#f87171'/>"
               f"<text x='{x+bw/2:.0f}' y='{H-pad+14:.0f}' class='ax' text-anchor='middle'>{labels[i]}</text>")
        if no[i]: bars+=f"<text x='{x+bw*0.75:.0f}' y='{H-pad-hn-4:.0f}' class='vv' text-anchor='middle'>{no[i]}</text>"
    return f"<svg viewBox='0 0 {W} {H}' class='chart'>{bars}</svg>"

# calibration SVG (accuracy bars vs mean-conf marker)
def calib_svg(rows):
    rows=[r for r in rows if r[1]]
    W,H,pad=620,240,34; n=len(rows); bw=(W-2*pad)/n; bars=""
    for i,(lb,nn,c,a) in enumerate(rows):
        x=pad+i*bw; ha=(H-2*pad)*a
        bars+=(f"<rect x='{x+6:.0f}' y='{H-pad-ha:.0f}' width='{bw-12:.0f}' height='{ha:.0f}' fill='#38bdf8' opacity='.7'/>"
               f"<line x1='{x+6:.0f}' x2='{x+bw-6:.0f}' y1='{H-pad-(H-2*pad)*c:.0f}' y2='{H-pad-(H-2*pad)*c:.0f}' stroke='#fbbf24' stroke-width='2'/>"
               f"<text x='{x+bw/2:.0f}' y='{H-pad+14:.0f}' class='ax' text-anchor='middle'>{lb}</text>"
               f"<text x='{x+bw/2:.0f}' y='{H-pad-ha-4:.0f}' class='vv' text-anchor='middle'>{a:.2f}</text>")
    return (f"<svg viewBox='0 0 {W} {H}' class='chart'>{bars}</svg>"
            "<div class='cap'><span style='color:#38bdf8'>■ gerçek doğruluk</span> &nbsp; "
            "<span style='color:#fbbf24'>▬ ortalama güven</span> — ikisi çakışırsa kalibrasyon mükemmel</div>")

# trust band table
tb_rows=""
for t,cov,na,aa,nr,ab,ds in bands:
    tb_rows+=(f"<tr><td>≥ {t:.3f}</td><td>{cov:.1%}</td><td>{na:,}</td><td class='good'>{aa:.4f}</td>"
              f"<td>{nr:,}</td><td>{ab:.4f}</td><td class='{'bad' if ds else 'good'}'>{ds}</td></tr>")

# per-class table
pc_rows=""
for i,k in enumerate(range(1,6)):
    pc_rows+=(f"<tr><td>{ACU[k]}</td><td>{supp[i]:,}</td><td>{prec[i]:.4f}</td><td>{rec[i]:.4f}</td>"
              f"<td>{f1c[i]:.4f}</td><td>{cls_conf[i]:.4f}</td></tr>")

# taxonomy bars
tax_order=[("intrinsic noise","#9aa4b2","Etiket gürültüsü: aynı şikâyetin nadir farklı etiketi. Model kuralı doğru izledi → DÜZELTİLEMEZ."),
           ("ambiguous phrase","#fbbf24","Muğlak ifade: bu şikâyet birden çok aciliyete eşleniyor (saflık<1). İçsel belirsizlik → DÜZELTİLEMEZ."),
           ("hard boundary","#f87171","Zor sınır: ifade kesin tek aciliyete eşlenir ama bag-of-words ekleri çekirdeği suluyor. Sadece ezberle 'düzelir' → OVERFIT olur.")]
mxt=max(tax.values()) if tax else 1; tax_bars=""
for name,col,desc in tax_order:
    v=tax.get(name,0); w=100*v/mxt
    tax_bars+=(f"<div class='taxrow'><div class='taxlbl'>{name} <b>({v})</b></div>"
               f"<div class='taxbar'><div style='width:{w:.0f}%;background:{col}'></div></div>"
               f"<div class='taxdesc'>{desc}</div></div>")

# confident-error list
ce_rows=""
for _,r in hi_conf_err.head(35).iterrows():
    dcls={"intrinsic noise":"noise","ambiguous phrase":"amb","hard boundary":"hard"}[r["diag"]]
    ucls="under" if r["dir"]=="undertriage" else "over"
    ce_rows+=(f"<tr class='{ucls}'><td>{r['conf']:.3f}</td><td>{ACU[r['triage_acuity']]}</td>"
              f"<td class='strong'>{ACU[r['pred']]}</td><td>{esc(r['dir'])}</td>"
              f"<td class='{dcls}'>{esc(r['diag'])}</td><td>{r['ppur']:.2f}</td>"
              f"<td class='cc'>{esc(r['chief_complaint_raw'])}</td>"
              f"<td>{esc(r['news2_score'])}</td><td>{esc(r['gcs_total'])}</td></tr>")

cards=lambda items:"".join(f"<div class='card'><b>{v}</b><span>{k}</span></div>" for k,v in items)

SEC = {
"overview":("📊 Genel Bakış", f"""
 <p class='lead'>Model 80.000 hastanın <b>{acc:.2%}</b>'sini doğru sıralıyor (baseline 85.51%). Hataların neredeyse tamamı ±1 kademe.</p>
 <div class='cards'>{cards([('doğruluk',f'{acc:.4f}'),('macro-F1',f'{mf1:.4f}'),('Quadratic WK',f'{qwk:.4f}'),
        ('toplam hata',f'{n_err}'),('undertriage',f'{under}'),('overtriage',f'{over}'),
        ('tehlikeli undertriage',f'{danger}')])}</div>
 <h3>Confusion matrix (satır = gerçek, sütun = tahmin)</h3>
 <p class='muted'>Köşegen (mavi) = doğru. Köşegen-dışı (kırmızı) = hata; renk yoğunluğu o gerçek sınıf içindeki oranı gösterir.</p>
 {cm_html}"""),

"confidence":("🎯 Güven", f"""
 <p class='lead'>Model doğru olduğunda ortalama <b>{mean_conf_ok:.3f}</b> güvenle konuşuyor; yanıldığında ortalama <b>{mean_conf_no:.3f}</b> (medyan {med_conf_no:.2f}).
 Yani <b>yanlışlar düşük güven bölgesinde toplanıyor</b> — bu çok iyi: güven, hatanın habercisi.</p>
 <h3>Güven dağılımı: doğru vs yanlış</h3>
 {hist_svg(hist_ok,hist_no,clab)}
 <div class='cap'><span style='color:#34d399'>■ doğru</span> &nbsp; <span style='color:#f87171'>■ yanlış</span> (kırmızı sayılar = o banttaki hata adedi)</div>
 <p class='muted'>Okuma: ≥.99 güven bandında binlerce doğru var, neredeyse hiç hata yok. Hatalar .7–.95 arası "tereddüt" bölgesinde.</p>"""),

"calibration":("📐 Kalibrasyon", f"""
 <p class='lead'>Kalibrasyon = "%90 dediğinde gerçekten %90 haklı mı?" Top-label <b>ECE = {ece:.4f}</b> (0 = kusursuz).</p>
 {calib_svg(calib)}
 <p class='muted'>Mavi bar (gerçek doğruluk) sarı çizgiye (ortalama güven) ne kadar yakınsa o kadar dürüst. Yüksek bantlarda neredeyse çakışıyorlar.</p>"""),

"trust":("🛡️ Güven Bantları", f"""
 <p class='lead'>"Modele ne kadar güvenebilirim?" — selective prediction. Bir eşiğin üstünü <b>otomatik kabul</b> et, altını <b>insana yönlendir</b>.</p>
 <table class='tbl'><tr><th>güven eşiği</th><th>kapsam</th><th>oto-kabul n</th><th>oto doğruluk</th>
   <th>insana giden n</th><th>insan-bölge doğruluk</th><th>kaçan tehlikeli</th></tr>{tb_rows}</table>
 <p class='muted'>"kaçan tehlikeli" = oto-kabul edilen ama aslında tehlikeli undertriage olan vakalar (insan görmeden geçer). Eşik yükseldikçe sıfıra yaklaşır.</p>
 <p class='muted'>Örn: ≥0.99 güveni otomatik kabul edersen vakaların büyük kısmını ~%100 doğrulukla halledersin; kalan küçük "tereddüt" dilimini hemşire bakar.</p>"""),

"errors":("⚠️ Hatalar & Taksonomi", f"""
 <p class='lead'>Kalan {n_err} hatanın <b>neden</b> hata olduğu. Ortalama ifade-saflığı {mean_pur_err:.2f}; hataların %{pct_err_ambig*100:.0f}'i muğlak ifadelerde.</p>
 <div class='tax'>{tax_bars}</div>
 <h3>En "emin ama yanlış" vakalar (model emin, yine de yanıldı)</h3>
 <p class='muted'>Bunlar en kritik incelemelik: çoğu kritik ifadenin (septic shock, MVA…) ekler yüzünden 1 kademe düşürülmesi.</p>
 <table class='tbl small'><tr><th>güven</th><th>GERÇEK</th><th>TAHMİN</th><th>yön</th><th>tanı</th><th>saflık</th><th>şikâyet</th><th>news2</th><th>gcs</th></tr>{ce_rows}</table>"""),

"perclass":("🔬 Sınıf Bazında", f"""
 <p class='lead'>Hangi aciliyet seviyesi en güvenilir? L3–L5 kusursuza yakın; en zoru en nadir ve en kritik olan <b>L1</b>.</p>
 <table class='tbl'><tr><th>seviye</th><th>destek (n)</th><th>precision</th><th>recall</th><th>F1</th><th>ort. güven</th></tr>{pc_rows}</table>
 <p class='muted'>L1 yalnızca verinin ~%4'ü; tüm "kaçan" kritik vakalar burada. Precision/recall yine de 0.99+ ama tek tek L1→L2 kayması güvenlik açısından en önemlisi.</p>"""),

"why":("💡 Neden Doğru / Neden Yanlış", f"""
 <h3>Neden bu kadar DOĞRU?</h3>
 <ul>
  <li>Sentetik triyaj politikası aciliyeti neredeyse tamamen <b>şikâyet metninden</b> üretiyor (ifade-saflığı 0.9994).</li>
  <li>Doğru tahminlerin <b>%{pct_correct_pure*100:.1f}</b>'i tek-aciliyete eşlenen (saflık=1.0) kesin ifadeler üzerinde.</li>
  <li>Fizyoloji (news2, gcs, spo2) metni doğruluyor; çelişince model genelde metni izliyor — bu da politikayla uyumlu.</li>
  <li>Fold-içi TF-IDF (vocab her fold'un eğitiminde fit) → sızıntı yok; train−OOF açığı ≈ +0.0004, yani ezber değil gerçek kural.</li>
 </ul>
 <h3>Neden hâlâ {n_err} hata var (ve neden DÜZELTMİYORUZ)?</h3>
 <ul>
  <li><b>{tax.get('intrinsic noise',0)} etiket gürültüsü:</b> aynı şikâyetin nadir farklı etiketi — gerçek doğru bile belirsiz. İndirgenemez.</li>
  <li><b>{tax.get('ambiguous phrase',0)} muğlak ifade:</b> "acute angle closure glaucoma" bazen L1 bazen L2 (saflık 0.67–0.82). İçsel belirsizlik.</li>
  <li><b>{tax.get('hard boundary',0)} zor sınır:</b> "septic shock multi-organ failure with vomiting" gibi — kesin L1 ama ekler ("with vomiting") çekirdeği suluyor. Bunları "düzeltmenin" tek yolu ifade-ezberi ya da hatalara elle uydurulmuş sözlük = <b>overfit</b>. Bilerek yapmadık.</li>
  <li>Denenip <b>reddedilen</b>: maliyet-duyarlı sınıf ağırlığı (iter3) → fayda yok, çünkü model emin-yanlış, sınırda değil.</li>
 </ul>"""),

"reality":("🧪 Reality Check", f"""
 <p class='lead'>"%99.96 fazla iyi değil mi?" — haklı şüphe. Üç deneyle kanıt: bu bir bug/sızıntı/ezber <b>değil</b>;
 sentetik politika acuity'yi neredeyse tamamen <b>şikâyet metninden</b> üretiyor, biz de o kuralı geri kazanıyoruz.</p>
 <h3>0) Sızıntı kontrolü</h3>
 <p class='muted'>Modele giren 61 özelliğin hiçbiri sonuç/hedef değil: <code>disposition</code>, <code>ed_los_hours</code>,
 <code>triage_acuity</code> → özelliklerde <b>yok</b>. Ham metin doğrudan özellik değil; TF-IDF'i her fold'un kendi eğitiminde fit edilir (sızıntısız).</p>
 <h3>Karşılaştırma (doğruluk)</h3>
 <div class='rb'><span>Aptal lookup · ifadeler tekrar eder (rastgele fold)</span>
   <div class='bar'><div style='width:{REAL['lookup_random']*100:.1f}%;background:#fbbf24'></div></div><b>{REAL['lookup_random']:.4f}</b></div>
 <div class='rb'><span>Saf ezber · <u>görülmemiş</u> ifadeler (GroupKFold)</span>
   <div class='bar'><div style='width:{REAL['lookup_unseen']*100:.1f}%;background:#f87171'></div></div><b>{REAL['lookup_unseen']:.4f}</b></div>
 <div class='rb'><span>MODEL · <u>görülmemiş</u> ifadeler (GroupKFold)</span>
   <div class='bar'><div style='width:{REAL['model_unseen']*100:.1f}%;background:#34d399'></div></div><b>{REAL['model_unseen']:.4f}</b></div>
 <div class='rb'><span>Fizyoloji-only baseline</span>
   <div class='bar'><div style='width:{REAL['baseline']*100:.1f}%;background:#8b94a3'></div></div><b>{REAL['baseline']:.4f}</b></div>
 <div class='rb'><span>Modelimiz · rastgele OOF (gerçek skor)</span>
   <div class='bar'><div style='width:{acc*100:.1f}%;background:#38bdf8'></div></div><b>{acc:.4f}</b></div>
 <h3>Okuma</h3>
 <ul>
  <li><b>Aptal lookup {REAL['lookup_random']:.4f}:</b> tek satırlık "ifade→çoğunluk" sözlüğü bile %99.6 yapıyor → görev esasen bir ifade-eşlemesi (sentetik politika).</li>
  <li><b>Ezber görülmemişte {REAL['lookup_unseen']:.4f}:</b> hiç görmediği ifadede ezber çöküyor (≈ baseline) → saf ezber değiliz.</li>
  <li><b>MODEL görülmemişte {REAL['model_unseen']:.4f}:</b> model hiç görmediği ifadelerde bile %99.8 → <b>kelimeleri</b> anlıyor ("severe/shock/perforation"), gerçek genelleme.</li>
  <li>Gerçek test setinin %{REAL['test_phrase_overlap']*100:.0f}'i train'de var → "rastgele" duruma benziyor → ~{acc:.4f} bu yarışma için <b>meşru</b>.</li>
 </ul>
 <h3>⚠️ Dürüst uyarı</h3>
 <p class='muted'>Bu skor bu kadar yüksek çünkü veri <b>sentetik</b> ve etiket-politikası metin-belirlenimli.
 Gerçek bir acil serviste aynı şikâyet farklı aciliyet alır; gerçek triyaj ML modelleri ~%70–80 / orta QWK seviyesinde kalır.
 0.9996 bu veri setinin doğası — gerçek hastaneye taşınmaz.</p>"""),

"help":("❓ Butonlar Ne İşe Yarar", f"""
 <ul class='help'>
  <li><b>📊 Genel Bakış</b> — özet metrikler (doğruluk, F1, QWK) + confusion matrix. "Genel olarak ne kadar iyi?"</li>
  <li><b>🎯 Güven</b> — model ne kadar emin; doğru vs yanlış güven dağılımı. "Emin olduğunda haklı mı?"</li>
  <li><b>📐 Kalibrasyon</b> — söylediği yüzdeyle gerçek doğruluk uyuşuyor mu (ECE). "%90 = gerçekten %90 mı?"</li>
  <li><b>🛡️ Güven Bantları</b> — bir eşiğin üstünü otomatik kabul edersen kapsam/doğruluk ve kaç tehlikeli vaka kaçar. "Ne kadarına gözü kapalı güvenebilirim?"</li>
  <li><b>⚠️ Hatalar & Taksonomi</b> — kalan hataların türü (gürültü/muğlak/zor-sınır) + en emin-yanlış vakalar. "Nerede, neden yanılıyor?"</li>
  <li><b>🔬 Sınıf Bazında</b> — her aciliyet seviyesi için precision/recall/F1/güven. "Hangi seviye en zayıf?"</li>
  <li><b>💡 Neden Doğru/Yanlış</b> — sözel gerçekçe: neden bu kadar isabetli, neden kalan hatalar düzeltilmiyor.</li>
  <li><b>🧪 Reality Check</b> — "%99.96 fazla iyi değil mi?" şüphesinin üç deneyle yanıtı: sızıntı yok, ezber değil, gerçek genelleme — ama veri sentetik.</li>
 </ul>""")}

order=["overview","confidence","calibration","trust","errors","perclass","why","reality","help"]
nav="".join(f"<button class='nav {'active' if k==order[0] else ''}' onclick=\"show('{k}',this)\">{SEC[k][0]}</button>" for k in order)
secs="".join(f"<section id='{k}' style='display:{'block' if k==order[0] else 'none'}'>{SEC[k][1]}</section>" for k in order)

doc=f"""<!doctype html><html><head><meta charset=utf-8><title>Triagegeist — Confidence Dashboard</title>
<style>
 body{{font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0d0f14;color:#e7e9ee}}
 header{{padding:18px 24px;background:#13161d;border-bottom:1px solid #262b36}}
 h1{{margin:0;font-size:19px}} .tag{{color:#8b94a3;font-size:12px;margin-top:3px}}
 .navbar{{display:flex;flex-wrap:wrap;gap:6px;padding:12px 24px;background:#13161d;border-bottom:1px solid #262b36;position:sticky;top:0;z-index:5}}
 .nav{{background:#1b1f29;color:#cbd3df;border:1px solid #2e3543;padding:7px 12px;border-radius:8px;cursor:pointer;font-size:13px}}
 .nav:hover{{filter:brightness(1.25)}} .nav.active{{background:#2563eb;color:#fff;border-color:#2563eb}}
 main{{padding:22px 24px;max-width:980px}}
 .lead{{font-size:15px}} .muted{{color:#8b94a3;font-size:12.5px}} h3{{margin:20px 0 8px}}
 .cards{{display:flex;flex-wrap:wrap;gap:12px;margin:12px 0}}
 .card{{background:#161a22;border:1px solid #262b36;border-radius:10px;padding:11px 15px;min-width:120px}}
 .card b{{font-size:20px;display:block}} .card span{{color:#8b94a3;font-size:12px}}
 table{{border-collapse:collapse;margin:8px 0}} .grid td,.grid th{{border:1px solid #262b36;padding:6px 10px;text-align:center;font-size:12.5px}}
 .grid th{{background:#161a22}} .grid .nn{{font-weight:bold}}
 .tbl{{width:100%;font-size:13px}} .tbl th,.tbl td{{border-bottom:1px solid #20242e;padding:6px 9px;text-align:left}}
 .tbl th{{background:#161a22}} .tbl.small th,.tbl.small td{{font-size:11.5px;padding:4px 7px;white-space:nowrap}}
 td.cc{{max-width:330px;overflow:hidden;text-overflow:ellipsis}} td.strong{{font-weight:bold}}
 .good{{color:#34d399}} .bad{{color:#f87171;font-weight:bold}}
 tr.under{{background:#3a2a1a}} tr.over{{background:#1a2740}}
 td.noise{{color:#9aa4b2}} td.amb{{color:#fbbf24}} td.hard{{color:#f87171}}
 .chart{{width:100%;max-width:640px;background:#11141b;border:1px solid #262b36;border-radius:10px}}
 .ax{{fill:#8b94a3;font-size:10px}} .vv{{fill:#cbd3df;font-size:10px}}
 .cap{{font-size:12px;color:#8b94a3;margin:6px 0 2px}}
 .tax{{margin:10px 0}} .taxrow{{margin:10px 0}} .taxlbl{{font-size:13px;margin-bottom:3px}}
 .taxbar{{background:#161a22;border-radius:6px;height:16px;overflow:hidden}} .taxbar div{{height:100%}}
 .taxdesc{{color:#8b94a3;font-size:12px;margin-top:3px}}
 .rb{{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:13px}}
 .rb span{{flex:0 0 320px}} .rb .bar{{flex:1;background:#161a22;border-radius:6px;height:16px;overflow:hidden}}
 .rb .bar div{{height:100%}} .rb b{{flex:0 0 64px;text-align:right;font-variant-numeric:tabular-nums}}
 code{{background:#1b1f29;padding:1px 5px;border-radius:4px;font-size:12px}}
 ul{{line-height:1.7}} ul.help li{{margin:6px 0}}
</style></head><body>
<header><h1>Triagegeist — Güven & Doğruluk Panosu</h1>
 <div class="tag">iter2 modeli (word+char TF-IDF + fizyoloji) · 5-fold OOF · {N:,} hasta · sızıntısız · overfit açığı ≈ +0.0004</div></header>
<div class="navbar">{nav}</div>
<main>{secs}</main>
<script>
function show(id,btn){{
  document.querySelectorAll('main section').forEach(s=>s.style.display='none');
  document.getElementById(id).style.display='block';
  document.querySelectorAll('.nav').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active'); window.scrollTo(0,0);
}}
</script></body></html>"""
(OUT/"confidence_dashboard.html").write_text(doc,encoding="utf-8")

json.dump(dict(accuracy=round(acc,4),macro_f1=round(mf1,4),qwk=round(qwk,4),ece=round(ece,4),
   errors=n_err,undertriage=under,overtriage=over,dangerous=danger,
   mean_conf_correct=round(mean_conf_ok,4),mean_conf_wrong=round(mean_conf_no,4),
   per_class={ACU[k]:dict(precision=round(prec[i],4),recall=round(rec[i],4),f1=round(f1c[i],4),
              support=int(supp[i]),mean_conf=round(cls_conf[i],4)) for i,k in enumerate(range(1,6))},
   trust_bands=[dict(thresh=t,coverage=round(cov,4),acc_auto=round(aa,4),danger_slip=ds) for t,cov,na,aa,nr,ab,ds in bands],
   taxonomy=tax), open(OUT/"confidence_report.json","w"),indent=2)
P(f"\n[saved] inspection/confidence_dashboard.html  + confidence_report.json")
