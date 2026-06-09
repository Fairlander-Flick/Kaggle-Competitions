"""Square (1:1) thumbnail for the Triagegeist Kaggle writeup. 1024x1024 PNG."""
from PIL import Image, ImageDraw, ImageFont

FT = "/home/fairlander/Code/Kaggle-Comp/Better_Golf/.venv/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf/"
def f(bold, sz): return ImageFont.truetype(FT + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), sz)

S = 1024
BG, INK, SUB, ACCENT = (13, 15, 20), (236, 239, 245), (150, 164, 179), (56, 189, 248)
img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def center(text, y, font, fill, spacing=0):
    if spacing == 0:
        w = d.textbbox((0, 0), text, font=font)[2]
        d.text(((S - w) / 2, y), text, font=font, fill=fill)
        return
    # manual letter-spacing
    widths = [d.textbbox((0, 0), c, font=font)[2] for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = (S - total) / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill); x += w + spacing

# top accent rule
d.rectangle([0, 0, S, 10], fill=ACCENT)

# wordmark
center("TRIAGEGEIST", 132, f(True, 104), INK, spacing=6)
center("Modeling, auditing & a reality check for ED triage", 268, f(False, 31), SUB)

# ESI acuity tiles  (L1 most urgent -> L5 non-urgent, clinical red->green)
labels = [("L1","resus"),("L2","emergent"),("L3","urgent"),("L4","less urgent"),("L5","non-urgent")]
cols   = [(226,59,59),(240,138,36),(232,195,74),(91,180,91),(59,130,196)]
n=5; gap=26; pad=96; tw=(S-2*pad-(n-1)*gap)/n; ty=372; th=150
fL, fS = f(True, 52), f(False, 21)
for i,((lab,desc),c) in enumerate(zip(labels,cols)):
    x0=pad+i*(tw+gap); x1=x0+tw
    d.rounded_rectangle([x0,ty,x1,ty+th], radius=18, fill=c)
    lw=d.textbbox((0,0),lab,font=fL)[2]; d.text((x0+(tw-lw)/2, ty+30), lab, font=fL, fill=(20,22,28))
    dw=d.textbbox((0,0),desc,font=fS)[2]; d.text((x0+(tw-dw)/2, ty+96), desc, font=fS, fill=(20,22,28))
center("ESI acuity   1 = most urgent  →  5 = non-urgent", ty+th+22, f(False,22), SUB)

# headline stat
center("0.855  →  0.9995", 624, f(True, 92), INK)
center("vitals-only model   →   + chief-complaint text  (OOF accuracy)", 740, f(False, 27), SUB)
center("dangerous undertriage cut 566 → 36, with an honest reality check", 786, f(False, 24), ACCENT)

# footer band
d.rectangle([0, S-92, S, S], fill=(18,22,30))
center("calibrated model  ·  NLP red-flag net  ·  equity audit  ·  outcome-anchored second opinion",
       S-62, f(False, 21), SUB)

img.save("/home/fairlander/Code/Kaggle-Comp/Triagegeist/cover_thumbnail_1x1.png")
print("saved cover_thumbnail_1x1.png", img.size)
