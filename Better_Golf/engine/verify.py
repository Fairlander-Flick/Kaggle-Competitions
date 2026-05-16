"""Local verifier — runs the OFFICIAL neurogolf_utils scoring path verbatim.

It reuses neurogolf_utils.verify_subset / score_network exactly as the Kaggle
grader's verify_network does (same ONNX Runtime profiling, same disqualification
rules, same points formula), but returns a structured result instead of
printing/plotting. Local result == Kaggle result, deterministically.
"""
from __future__ import annotations

import contextlib
import io
import math
import os
import sys
import tempfile
from typing import Dict, List

import numpy as np
import onnx
import onnxruntime

from . import dataio

sys.path.insert(0, os.path.join(dataio.DATA_DIR, "neurogolf_utils"))
import neurogolf_utils as ng  # noqa: E402


def verify(model: onnx.ModelProto, task: Dict, task_num: int) -> dict:
    """Mirror neurogolf_utils.verify_network's measurement path.

    Returns {ok, n_pass, n_fail, memory, params, points, disqualified, err}.
    `ok` means every train+test+arc-gen example matches exactly AND the model
    is measurable — i.e. exactly the condition under which Kaggle awards points.
    """
    examples = {
        "train": task.get("train", []),
        "test": task.get("test", []),
        "arc-gen": task.get("arc-gen", []),
    }
    work = tempfile.mkdtemp(prefix=f"bg_{task_num:03d}_")
    cwd = os.getcwd()
    res = {"ok": False, "n_pass": 0, "n_fail": 0, "memory": None,
           "params": None, "points": 0.0, "disqualified": False, "err": ""}
    try:
        os.chdir(work)
        fname = f"task{task_num:03d}.onnx"
        onnx.save(model, fname)
        if not ng.check_network(fname):
            res["err"] = "filesize/exists check failed"
            return res
        sanitized = onnx.load(fname)
        for node in sanitized.graph.node:
            node.name = node.output[0]
            if "kernel_time" in node.name:
                res["err"] = "reserved 'kernel_time' in tensor name"
                return res
        opts = onnxruntime.SessionOptions()
        opts.enable_profiling = True
        opts.graph_optimization_level = (
            onnxruntime.GraphOptimizationLevel.ORT_DISABLE_ALL)
        opts.profile_file_prefix = f"{task_num:03}"
        with contextlib.redirect_stdout(io.StringIO()):
            session = onnxruntime.InferenceSession(
                sanitized.SerializeToString(), opts)
            ar, aw, _ = ng.verify_subset(
                session, examples["train"] + examples["test"])
            gr, gw, _ = ng.verify_subset(session, examples["arc-gen"])
            trace = session.end_profiling()
            memory, params = ng.score_network(sanitized, trace)
        res["n_pass"] = ar + gr
        res["n_fail"] = aw + gw
        if memory is None or params is None or memory < 0 or params < 0:
            res["disqualified"] = True
            res["err"] = "network not measurable (disqualified)"
            return res
        res["memory"], res["params"] = int(memory), int(params)
        if res["n_fail"] == 0:
            res["ok"] = True
            res["points"] = max(1.0, 25.0 - math.log(max(1.0, memory + params)))
        return res
    except Exception as e:  # noqa: BLE001 — surface, never crash the loop
        res["err"] = f"{type(e).__name__}: {e}"
        return res
    finally:
        os.chdir(cwd)
        with contextlib.suppress(Exception):
            for f in os.listdir(work):
                os.remove(os.path.join(work, f))
            os.rmdir(work)


def quick_apply_check(family, spec, pairs: List[dataio.Pair]) -> int:
    """Fast pre-filter: how many pairs the family's pure-python apply() gets
    right. Used to reject a family before the (slower) ONNX verify."""
    bad = 0
    for i, o in pairs:
        if max(len(i), len(i[0])) > 30:
            continue  # grader skips >30 grids
        try:
            if family.apply(spec, i) != o:
                bad += 1
        except Exception:  # noqa: BLE001
            bad += 1
    return bad
