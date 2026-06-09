"""Reality-check figure for the writeup media gallery. Horizontal bars, 1280x720 PNG."""
from PIL import Image, ImageDraw, ImageFont
FT="/home/fairlander/Code/Kaggle-Comp/Better_Golf/.venv/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf/"
def f(b,s): return ImageFont.truetype(FT+("DejaVuSans-Bold.ttf" if b else "DejaVuSans.ttf"), s)

W,H=1280,720; BG=(13,15,20); INK=(236,239,245); SUB=(150,164,179)
img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
d.rectangle([0,0,W,8],fill=(56,189,248))

d.text((60,40),"Is 0.9995 real, or leakage / memorization?",font=f(True,40),fill=INK)
d.text((60,96),"Out-of-fold accuracy on 80,000 patients. Three controls, one verdict.",font=f(False,24),fill=SUB)

rows=[
 ("Vitals-only model","no complaint text",0.8551,(138,148,163)),
 ("Phrase to majority LOOKUP","random folds: task is a lookup",0.9962,(240,138,36)),
 ("Lookup, UNSEEN phrases","GroupKFold: memorization collapses",0.3615,(226,59,59)),
 ("Model, UNSEEN phrases","GroupKFold: real generalization",0.9976,(91,180,91)),
 ("Text model, out-of-fold","random folds: our reported score",0.9995,(56,189,248)),
]
x0,x1=600,1205; y=190; rh=84
fL,fN,fV=f(True,23),f(False,18),f(True,26)
for lab,note,val,col in rows:
    d.text((60,y+4),lab,font=fL,fill=INK)
    if note: d.text((60,y+38),note,font=fN,fill=SUB)
    d.rounded_rectangle([x0,y,x1,y+44],radius=8,fill=(28,32,42))           # track
    bw=(x1-x0)*val
    d.rounded_rectangle([x0,y,x0+bw,y+44],radius=8,fill=col)                # value
    vs=f"{val:.4f}"; vw=d.textbbox((0,0),vs,font=fV)[2]
    if val<0.9:
        d.text((x0+bw+14,y+9),vs,font=fV,fill=INK)
    else:
        d.text((x0+bw-vw-16,y+9),vs,font=fV,fill=(20,22,28))
    y+=rh

d.line([x0+(x1-x0)*0.8551,180,x0+(x1-x0)*0.8551,y-40],fill=(90,98,112),width=1)
d.text((60,y+8),"Lookup wins when phrases repeat (0.996) but collapses on unseen phrasings (0.36); the model still",
       font=f(False,20),fill=SUB)
d.text((60,y+34),"reaches 0.998 unseen by learning the words, not the phrase. No outcome columns are features.",
       font=f(False,20),fill=SUB)

img.save("/home/fairlander/Code/Kaggle-Comp/Triagegeist/figures/reality_check.png")
print("saved figures/reality_check.png",img.size)
