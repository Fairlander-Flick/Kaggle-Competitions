"""Per-task orchestrator + logging.

solve_one(n): try families cheapest-correct-first; accept the first whose
pure-python apply() reproduces EVERY train+test+arc-gen pair AND whose ONNX
passes the official verifier. Persist result, ONNX, and human logs.

All markdown is regenerated from results.json (single source of truth) so
re-running a task is idempotent — no duplicate log entries.
"""
from __future__ import annotations

import json
import os
from typing import Dict, Optional

import onnx

from . import dataio, verify
from .families import REGISTRY

BASE = os.path.dirname(os.path.dirname(__file__))
ONNX_DIR = os.path.join(BASE, "out", "onnx")
LOG_DIR = os.path.join(BASE, "logs")
RESULTS = os.path.join(LOG_DIR, "results.json")


def _load_results() -> Dict[str, dict]:
    if os.path.exists(RESULTS):
        with open(RESULTS) as f:
            return json.load(f)
    return {}


def _save_results(r: Dict[str, dict]) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(RESULTS, "w") as f:
        json.dump(r, f, indent=2, sort_keys=True)


def _ascii(grid) -> str:
    if len(grid) > 16 or len(grid[0]) > 16:
        return f"<{len(grid)}x{len(grid[0])} grid>"
    return "\n".join("".join(str(c) for c in row) for row in grid)


def solve_one(n: int, persist: bool = True) -> dict:
    task = dataio.load_task(n)
    summ = dataio.grid_shapes(task)
    train = dataio.train_pairs(task)
    pairs = dataio.all_pairs(task)

    rec = {
        "task": n, "status": "unsolved", "family": None,
        "points": 0.0, "memory": None, "params": None,
        "n_pass": 0, "n_fail": summ["n_pairs"],
        "summary": summ, "note": "no family fit",
    }
    ex0 = task["train"][0]
    rec["sample"] = {"in": _ascii(ex0["input"]), "out": _ascii(ex0["output"])}

    for fam in REGISTRY:
        spec = fam.detect(train)
        if spec is None:
            continue
        if verify.quick_apply_check(fam, spec, pairs) != 0:
            continue  # explains train but not arc-gen/test -> not the true rule
        model = fam.build_onnx(spec)
        vr = verify.verify(model, task, n)
        if vr["ok"]:
            os.makedirs(ONNX_DIR, exist_ok=True)
            onnx.save(model, os.path.join(ONNX_DIR, f"task{n:03d}.onnx"))
            rec.update(status="solved", family=fam.name,
                       points=round(vr["points"], 3),
                       memory=vr["memory"], params=vr["params"],
                       n_pass=vr["n_pass"], n_fail=0,
                       note=f"{fam.name}: passes all {summ['n_pairs']} examples")
            break
        if vr["disqualified"]:
            rec["note"] = f"{fam.name} fit but ONNX disqualified: {vr['err']}"

    if persist:
        results = _load_results()
        results[f"{n:03d}"] = rec
        _save_results(results)
        render_all(results)
    return rec


def sweep(start: int, end: int) -> Dict[str, dict]:
    results = _load_results()
    for n in range(start, end + 1):
        rec = solve_one(n, persist=False)
        results[f"{n:03d}"] = rec
        s = rec["status"]
        tag = (f"{rec['family']} {rec['points']}pt"
               if s == "solved" else rec["note"])
        print(f"task{n:03d}: {s:8s} | {tag}")
    _save_results(results)
    render_all(results)
    return results


# --------------------------------------------------------------------------- #
# Markdown rendering (regenerated wholly from results.json)
# --------------------------------------------------------------------------- #
def render_all(results: Optional[Dict[str, dict]] = None) -> None:
    results = results or _load_results()
    _render_index(results)
    _render_log(results)


def _projection(results):
    solved = [r for r in results.values() if r["status"] == "solved"]
    pts = sum(r["points"] for r in solved)
    return len(solved), pts


def _render_index(results):
    solved, pts = _projection(results)
    n_done = len(results)
    lines = [
        "# NeuroGolf 2026 — Task Index",
        "",
        f"- Tasks attempted: **{n_done}/400**",
        f"- Tasks solved (full match, scored): **{solved}**",
        f"- Projected points: **{pts:.1f} / 10000**  "
        f"(target ≥ 7500)",
        "",
        "Click a task to jump to its analysis + solution in "
        "[`SOLVE_LOG.md`](SOLVE_LOG.md).",
        "",
        "| Task | Status | Type / Family | Points | Mem | Params | "
        "In→Out | Detail |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for k in sorted(results):
        r = results[k]
        s = r["summary"]
        io_s = (f"{s['input_shapes'][0] if len(s['input_shapes'])==1 else 'var'}"
                f"→{s['output_shapes'][0] if len(s['output_shapes'])==1 else 'var'}")
        badge = {"solved": "✅", "unsolved": "⬜",
                 "disqualified": "⚠️"}.get(r["status"], "⬜")
        lines.append(
            f"| task{k} | {badge} {r['status']} | {r['family'] or '—'} | "
            f"{r['points'] or '—'} | {r['memory'] if r['memory'] is not None else '—'} | "
            f"{r['params'] if r['params'] is not None else '—'} | {io_s} | "
            f"[task{k}](SOLVE_LOG.md#task{k}) |")
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "TASK_INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _render_log(results):
    solved, pts = _projection(results)
    out = [
        "# NeuroGolf 2026 — Solve Log",
        "",
        f"Projected **{pts:.1f}/10000** from **{solved}** solved tasks. "
        "One section per task: what it is, what we used, how we solved it.",
        "",
    ]
    for k in sorted(results):
        r = results[k]
        s = r["summary"]
        out += [
            f"## task{k}",
            "",
            f"- **Status:** {r['status']}",
            f"- **Examples:** {s['n_pairs']} "
            f"(train {s['n_train']}, test {s['n_test']}, arc-gen {s['n_arcgen']})",
            f"- **Shapes:** input {s['input_shapes']} → output "
            f"{s['output_shapes']}  | same-shape: {s['same_shape']}",
            f"- **Colors:** input {s['input_colors']} → output "
            f"{s['output_colors']}",
            f"- **Family used:** {r['family'] or '— (none yet)'}",
            f"- **Score:** {r['points']} pts  "
            f"(memory {r['memory']}, params {r['params']})",
            f"- **How solved:** {r['note']}",
            "",
            "Train example 0 (input → output):",
            "",
            "```",
            r["sample"]["in"],
            "→",
            r["sample"]["out"],
            "```",
            "",
        ]
    with open(os.path.join(LOG_DIR, "SOLVE_LOG.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
