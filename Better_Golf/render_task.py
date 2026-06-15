#!/usr/bin/env python
"""Render a task's input->output example pairs as a PNG you open in VS Code.
Usage: render_task.py <task_num> [n_examples]"""
import sys, os
sys.path.insert(0, ".")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from engine import dataio

# standard ARC palette (0..9)
PAL = ["#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00",
       "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF", "#870C25"]
CMAP = ListedColormap(PAL)


def draw(ax, grid, title):
    g = np.array(grid)
    ax.imshow(g, cmap=CMAP, vmin=0, vmax=9)
    ax.set_title(title, fontsize=9)
    ax.set_xticks(np.arange(-.5, g.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-.5, g.shape[0], 1), minor=True)
    ax.grid(which="minor", color="#333", linewidth=0.5)
    ax.set_xticks([]); ax.set_yticks([])


def main():
    n = int(sys.argv[1]); ne = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    t = dataio.load_task(n)
    exs = t.get("train", []) + t.get("arc-gen", [])
    exs = exs[:ne]
    fig, axes = plt.subplots(len(exs), 2, figsize=(6, 3 * len(exs)))
    if len(exs) == 1:
        axes = [axes]
    for i, ex in enumerate(exs):
        draw(axes[i][0], ex["input"], f"ex{i} INPUT")
        draw(axes[i][1], ex["output"], f"ex{i} OUTPUT")
    fig.suptitle(f"task{n:03d}", fontsize=11)
    fig.tight_layout()
    os.makedirs("renders", exist_ok=True)
    out = f"renders/task{n:03d}.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
