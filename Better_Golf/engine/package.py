"""Submission packaging + budget-aware Kaggle submit.

Submission = a flat zip of every solved task{NNN}.onnx. Unsolved tasks are
omitted (the grader scores them 0 either way; an absent/garbage file cannot
help). We only ever submit a zip whose every file passed the LOCAL official
verifier, so projected == actual.
"""
from __future__ import annotations

import glob
import os
import subprocess
import zipfile
from typing import List

from .solve import ONNX_DIR, _load_results, _projection

BASE = os.path.dirname(os.path.dirname(__file__))
SUB_ZIP = os.path.join(BASE, "out", "submission.zip")
COMP = "neurogolf-2026"


def build_zip() -> str:
    files: List[str] = sorted(glob.glob(os.path.join(ONNX_DIR, "task*.onnx")))
    if not files:
        raise RuntimeError("no solved ONNX files to package")
    with zipfile.ZipFile(SUB_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for fp in files:
            z.write(fp, arcname=os.path.basename(fp))
    return SUB_ZIP


def submit(message: str, force: bool = False) -> str:
    """Submit only if it beats our best real LB (5480.41) and clears the
    projected bar, unless force=True. Budget is 100/day; we still gate on a
    verified improvement, never spray submissions."""
    results = _load_results()
    n_solved, pts = _projection(results)
    if not force and pts < 5480.41:
        return (f"SKIP: projected {pts:.1f} ≤ best real LB 5480.41 "
                f"({n_solved} solved). Not submitting.")
    path = build_zip()
    cmd = ["kaggle", "competitions", "submit", "-c", COMP,
           "-f", path, "-m", message]
    out = subprocess.run(cmd, capture_output=True, text=True)
    return (f"submitted {n_solved} tasks, projected {pts:.1f}\n"
            f"{out.stdout}\n{out.stderr}").strip()
