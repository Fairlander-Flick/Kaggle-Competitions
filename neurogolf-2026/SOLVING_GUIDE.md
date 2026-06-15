# NeuroGolf-2026 — Solving Guide (read me first)

## Are all solutions the same? NO.
The 400 tasks span many transformation **families**. There is no single solver. Auto-classified family counts (rough):

- **global transform** — 168 tasks
- **crop / extract / select-region** — 102 tasks
- **local edit** — 90 tasks
- **tile / upscale / fractal** — 36 tasks
- **color-map** — 4 tasks

## How scoring works (what 'solve' means here)
- score/task = max(1, 25 − ln(memory + params)); 400 tasks, max 10000.
- memory = Σ bytes of every intermediate tensor (input & output are FREE); narrow dtype (bool/uint8=1 byte) wins. params = Σ initializer + Constant elements. Node **attributes are FREE** (Transpose perm; old-opset Slice/Pad/Reshape params).
- ALL shapes must be static. The cheapest graph = fewest, smallest intermediates, final op writing straight to `output`.

## How to hand-solve a task
1. Open its PNG (renders/). Work out the EXACT rule from the examples.
2. Tell the agent the rule in plain words (+ a cheap-op idea if you have one).
3. Agent builds minimal ONNX, verifies on all ~268 pairs, and if cheaper than the base AND it's the TRUE rule, it realizes on the leaderboard (learned/overfit graphs do NOT — proven).

## Where the points are
- Tasks already at ~25 pts: leave them.
- Tasks at 12–17 pts where the rule is SIMPLE but base graph is heavy = the wins.
- 1 task scores 0 (UNSOLVED): see the ⛔ in TASKS.md — a correct graph there is up to +25.
