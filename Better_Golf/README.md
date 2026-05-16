# Better_Golf — NeuroGolf 2026

Clean-room solver for the [NeuroGolf 2026](https://www.kaggle.com/competitions/neurogolf-2026)
Kaggle competition. Per task, build the **smallest correct ONNX** graph that
exactly reproduces every known input→output pair, verified locally with the
**official** `neurogolf_utils` grader (local score == Kaggle score).

```
Better_Golf/
  skill/SKILL.md     reusable agent skill (the method, the cost model, the loop)
  WORKFLOW.md        operating playbook
  run.py             CLI: solve / sweep / render / package / submit
  engine/            dataio · families · verify · solve · package
  data/              official 400 task JSONs + neurogolf_utils (git-ignored)
  out/onnx/          solved task{NNN}.onnx (the submission artifacts)
  logs/              results.json (truth) → TASK_INDEX.md · SOLVE_LOG.md
```

Start: `python run.py solve 1` — or read `skill/SKILL.md`. Browse progress in
[`logs/TASK_INDEX.md`](logs/TASK_INDEX.md).

Scoring: `points = max(1, 25 - ln(memory + params))` per task, 400 tasks,
max 10000. Outputs are knowable, so we know — we do not predict.
