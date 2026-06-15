#!/usr/bin/env python
"""Render ALL 400 tasks to PNGs named with their CURRENT submission score, and
write a score-sorted index (lowest score first = best targets to golf)."""
import os, sys, math, json
sys.path.insert(0, ".")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from engine import dataio

PAL = ["#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00",
       "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF", "#870C25"]
CMAP = ListedColormap(PAL)
COST = json.load(open("logs/vyank_costmap.json"))
OUT = "renders"
os.makedirs(OUT, exist_ok=True)


def draw(ax, grid, title):
    g = np.array(grid)
    ax.imshow(g, cmap=CMAP, vmin=0, vmax=9)
    ax.set_title(title, fontsize=8)
    ax.set_xticks(np.arange(-.5, g.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-.5, g.shape[0], 1), minor=True)
    ax.grid(which="minor", color="#333", linewidth=0.4)
    ax.set_xticks([]); ax.set_yticks([])


rows = []
for n in range(1, 401):
    try:
        t = dataio.load_task(n)
    except Exception:
        continue
    cost = COST.get(str(n))
    pts = max(1.0, 25 - math.log(max(1, cost))) if cost else 0.0
    exs = (t.get("train", []) + t.get("arc-gen", []))[:4]
    if not exs:
        continue
    fig, axes = plt.subplots(len(exs), 2, figsize=(5, 2.4 * len(exs)))
    if len(exs) == 1:
        axes = [axes]
    for i, ex in enumerate(exs):
        draw(axes[i][0], ex["input"], f"ex{i} IN")
        draw(axes[i][1], ex["output"], f"ex{i} OUT")
    fig.suptitle(f"task{n:03d}  —  {pts:.1f}/25 pts  (cost {cost})", fontsize=10)
    fig.tight_layout()
    fname = f"task{n:03d}_{pts:04.1f}of25.png"
    fig.savefig(os.path.join(OUT, fname), dpi=95, bbox_inches="tight")
    plt.close(fig)
    rows.append((n, pts, cost, fname))

rows_sorted = sorted(rows, key=lambda r: r[1])  # lowest score first = best targets
with open("TASKS_BY_SCORE.md", "w") as f:
    f.write("# NeuroGolf-2026 — per-task current score (lowest first = best golf targets)\n\n")
    f.write(f"Current submission ~6373 pts. {len(rows)} tasks. Open the PNG, find a "
            "cheaper way to express the rule, tell the agent.\n\n")
    f.write("| # | task | current pts | cost (mem+params) | image |\n|--|--|--|--|--|\n")
    for rank, (n, pts, cost, fn) in enumerate(rows_sorted, 1):
        f.write(f"| {rank} | task{n:03d} | **{pts:.2f}/25** | {cost} | "
                f"[png](renders/{fn}) |\n")
print(f"rendered {len(rows)} pngs -> {OUT}/ ; wrote TASKS_BY_SCORE.md")
