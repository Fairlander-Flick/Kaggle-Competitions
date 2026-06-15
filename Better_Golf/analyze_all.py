#!/usr/bin/env python
"""Per-task auto-analysis -> hints for hand-solving. Writes neurogolf-2026/TASKS.md
(score + png + hints per task, lowest-score first) and neurogolf-2026/SOLVING_GUIDE.md
(family breakdown + how-to)."""
import os, sys, json, glob, math, collections, shutil
sys.path.insert(0, ".")
import numpy as np
from engine import dataio

REPO_SUB = "../neurogolf-2026"   # push target folder
os.makedirs(f"{REPO_SUB}/renders", exist_ok=True)

score = {}
for f in glob.glob("logs/basescore/task*.json"):
    d = json.load(open(f)); score[d["task"]] = d


def feats(n):
    t = dataio.load_task(n)
    pr = []
    for k in ("train", "test", "arc-gen"):
        for ex in t.get(k, []):
            pr.append((np.array(ex["input"]), np.array(ex["output"])))
    i0, o0 = pr[0]
    same = all(i.shape == o.shape for i, o in pr)
    inc = sorted({int(c) for i, _ in pr for c in np.unique(i)})
    ouc = sorted({int(c) for _, o in pr for c in np.unique(o)})
    added = sorted(set(ouc) - set(inc))
    removed = sorted(set(inc) - set(ouc))
    # size relation
    ar_in = np.mean([i.size for i, _ in pr]); ar_out = np.mean([o.size for _, o in pr])
    if same:
        rel = "same-shape"
    elif ar_out < ar_in * 0.95:
        rel = "OUTPUT SMALLER (crop/extract/select/downscale)"
    elif ar_out > ar_in * 1.05:
        r = ar_out / ar_in
        rel = f"OUTPUT LARGER x{r:.1f} (tile/upscale/fractal)"
    else:
        rel = "shape changes"
    # recolor (pure per-cell map, same-shape)
    recolor = False
    if same:
        m = {}; ok = True
        for i, o in pr:
            for a, b in zip(i.flat, o.flat):
                if m.get(a, b) != b: ok = False; break
                m[a] = b
            if not ok: break
        recolor = ok
    # changed fraction (same-shape)
    chg = (np.mean([(i != o).mean() for i, o in pr]) if same else None)
    # output symmetry (same on all pairs)
    def sym(fn): return all(o.shape == fn(o).shape and np.array_equal(o, fn(o)) for _, o in pr)
    syms = [s for s, fn in [("H-mirror", lambda a: a[:, ::-1]),
                            ("V-mirror", lambda a: a[::-1]),
                            ("180", lambda a: a[::-1, ::-1])] if sym(fn)]
    # family guess
    if recolor and all(a == b for i, o in pr for a, b in zip(i.flat, o.flat)):
        fam = "identity"
    elif recolor:
        fam = "color-map (per-cell recolor)"
    elif "SMALLER" in rel:
        fam = "crop / extract / select-region"
    elif "LARGER" in rel:
        fam = "tile / upscale / fractal"
    elif not same:
        fam = "restructure / select / assemble"
    elif chg is not None and chg < 0.10:
        fam = "local edit (few cells change: fill/denoise/mark)"
    else:
        fam = "global transform (objects/lines/logic/counting)"
    sc = score.get(n, {})
    return dict(n=n, pts=sc.get("pts", 0.0), cost=sc.get("cost"), ok=sc.get("ok", False),
                npairs=len(pr), rel=rel, inc=inc, ouc=ouc, added=added, removed=removed,
                recolor=recolor, chg=(round(chg, 3) if chg is not None else None),
                syms=syms, fam=fam)


rows = []
for n in range(1, 401):
    try:
        rows.append(feats(n))
    except Exception as e:
        rows.append(dict(n=n, pts=0, fam="ERR " + str(e)[:30], rel="", inc=[], ouc=[],
                         added=[], removed=[], recolor=False, chg=None, syms=[], npairs=0, cost=None, ok=False))
    # copy render
    for g in glob.glob(f"renders/task{n:03d}_*.png"):
        shutil.copy(g, f"{REPO_SUB}/renders/{os.path.basename(g)}")

rows.sort(key=lambda r: r["pts"])
fam_count = collections.Counter(r["fam"].split(" (")[0] for r in rows)

with open(f"{REPO_SUB}/TASKS.md", "w") as f:
    f.write("# NeuroGolf-2026 — all 400 tasks: score + hints (lowest score first)\n\n")
    f.write("Goal per task: build the **smallest correct ONNX** (cost = memory+params; "
            "input/output free; narrow dtype + few ops = cheap). Current per-task score below is the "
            "base graph graded locally (strict). Solve = find a cheaper correct rule.\n\n")
    f.write("See SOLVING_GUIDE.md for families + method.\n\n")
    f.write("| task | pts | cost | family | shape | colors in→out (Δ) | hints | png |\n")
    f.write("|--|--|--|--|--|--|--|--|\n")
    for r in rows:
        png = glob.glob(f"renders/task{r['n']:03d}_*.png")
        png = os.path.basename(png[0]) if png else ""
        hints = []
        if r["recolor"]: hints.append("pure per-cell recolor")
        if r["added"]: hints.append(f"adds color {r['added']}")
        if r["removed"]: hints.append(f"removes color {r['removed']}")
        if r["chg"] is not None: hints.append(f"{r['chg']*100:.0f}% cells change")
        if r["syms"]: hints.append("out sym:" + ",".join(r["syms"]))
        st = "⛔UNSOLVED" if (not r["ok"]) else ("✅max" if r["pts"] >= 24.9 else "")
        f.write(f"| **{r['n']:03d}** | {r['pts']:.1f} {st} | {r['cost']} | {r['fam']} | {r['rel']} "
                f"| {r['inc']}→{r['ouc']} | {'; '.join(hints)} | [img](renders/{png}) |\n")

with open(f"{REPO_SUB}/SOLVING_GUIDE.md", "w") as f:
    f.write("# NeuroGolf-2026 — Solving Guide (read me first)\n\n")
    f.write("## Are all solutions the same? NO.\n")
    f.write("The 400 tasks span many transformation **families**. There is no single solver. "
            "Auto-classified family counts (rough):\n\n")
    for fam, c in fam_count.most_common():
        f.write(f"- **{fam}** — {c} tasks\n")
    f.write("\n## How scoring works (what 'solve' means here)\n")
    f.write("- score/task = max(1, 25 − ln(memory + params)); 400 tasks, max 10000.\n"
            "- memory = Σ bytes of every intermediate tensor (input & output are FREE); "
            "narrow dtype (bool/uint8=1 byte) wins. params = Σ initializer + Constant elements. "
            "Node **attributes are FREE** (Transpose perm; old-opset Slice/Pad/Reshape params).\n"
            "- ALL shapes must be static. The cheapest graph = fewest, smallest intermediates, "
            "final op writing straight to `output`.\n\n")
    f.write("## How to hand-solve a task\n")
    f.write("1. Open its PNG (renders/). Work out the EXACT rule from the examples.\n"
            "2. Tell the agent the rule in plain words (+ a cheap-op idea if you have one).\n"
            "3. Agent builds minimal ONNX, verifies on all ~268 pairs, and if cheaper than the base "
            "AND it's the TRUE rule, it realizes on the leaderboard (learned/overfit graphs do NOT — proven).\n\n")
    f.write("## Where the points are\n")
    f.write("- Tasks already at ~25 pts: leave them.\n"
            "- Tasks at 12–17 pts where the rule is SIMPLE but base graph is heavy = the wins.\n"
            "- 1 task scores 0 (UNSOLVED): see the ⛔ in TASKS.md — a correct graph there is up to +25.\n")
print("wrote", f"{REPO_SUB}/TASKS.md", "and SOLVING_GUIDE.md; families:", dict(fam_count))
