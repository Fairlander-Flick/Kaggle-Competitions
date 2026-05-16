"""Task IO + exact one-hot encode/decode.

Mirrors the official neurogolf_utils.convert_to_numpy / convert_from_numpy so
that anything we verify locally behaves byte-identically to the Kaggle grader.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

CHANNELS, HEIGHT, WIDTH = 10, 30, 30
GRID_SHAPE = (1, CHANNELS, HEIGHT, WIDTH)

Grid = List[List[int]]
Pair = Tuple[Grid, Grid]


def task_path(task_num: int) -> str:
    return os.path.join(DATA_DIR, f"task{task_num:03d}.json")


def load_task(task_num: int) -> Dict:
    with open(task_path(task_num)) as f:
        return json.load(f)


def all_pairs(task: Dict) -> List[Pair]:
    """Every (input, output) the grader checks: train + test + arc-gen.

    The grader (neurogolf_utils.verify_network) requires an EXACT match on
    every one of these. A solution is only valid if it reproduces all of them.
    """
    pairs: List[Pair] = []
    for key in ("train", "test", "arc-gen"):
        for ex in task.get(key, []):
            pairs.append((ex["input"], ex["output"]))
    return pairs


def train_pairs(task: Dict) -> List[Pair]:
    return [(ex["input"], ex["output"]) for ex in task.get("train", [])]


def to_onehot(grid: Grid) -> np.ndarray:
    """Exact copy of neurogolf_utils.convert_to_numpy semantics.

    Grids larger than 30x30 return None there; such examples are skipped by the
    grader, so a solver never needs to satisfy them.
    """
    t = np.zeros(GRID_SHAPE, dtype=np.float32)
    if max(len(grid), len(grid[0])) > 30:
        return None  # grader skips (verify_subset: `if not benchmark: continue`)
    for r, row in enumerate(grid):
        for c, color in enumerate(row):
            t[0][color][r][c] = 1.0
    return t


def from_onehot(t: np.ndarray) -> Grid:
    """Exact copy of neurogolf_utils.convert_from_numpy semantics."""
    _, channels, height, width = t.shape
    example: Grid = []
    for row in range(height):
        cells = []
        for col in range(width):
            colors = [c for c in range(channels) if t[0][c][row][col] == 1]
            cells.append(colors[0] if len(colors) == 1 else (11 if colors else 10))
        while cells and cells[-1] == 10:
            cells.pop(-1)
        example.append(cells)
    while example and not example[-1]:
        example.pop(-1)
    return example


def grid_shapes(task: Dict) -> Dict[str, object]:
    """Quick structural summary used by the analyzer / task index."""
    pairs = all_pairs(task)
    in_shapes = {(len(i), len(i[0])) for i, _ in pairs}
    out_shapes = {(len(o), len(o[0])) for _, o in pairs}
    same_shape = all(len(i) == len(o) and len(i[0]) == len(o[0]) for i, o in pairs)
    in_colors, out_colors = set(), set()
    for i, o in pairs:
        in_colors |= {c for row in i for c in row}
        out_colors |= {c for row in o for c in row}
    return {
        "n_pairs": len(pairs),
        "n_train": len(task.get("train", [])),
        "n_test": len(task.get("test", [])),
        "n_arcgen": len(task.get("arc-gen", [])),
        "input_shapes": sorted(in_shapes),
        "output_shapes": sorted(out_shapes),
        "same_shape": same_shape,
        "input_colors": sorted(in_colors),
        "output_colors": sorted(out_colors),
    }
