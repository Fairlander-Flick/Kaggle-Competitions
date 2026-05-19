# NeuroGolf 2026 — INTELLIGENCE (2026-05-19)

> **⚠ CORRECTION (2026-05-19, post-submit):** the "Assets in hand" scores
> below are the artifacts' *named* scores and are **FAKE**. beicicc6645
> submitted verbatim scored **1128.42** on the real grader, not 6645.39.
> Dataset-name scores = authors' local projected fantasy / cost-gaming
> tricks (`dummy_cost_scalar`). Our strict `engine.verify` correctly
> rejected them (17/20, nfail=0). **Trust only our official verifier.**
> Genuine best stays 5706.97. The one verified-real lever is Octaviograu's
> 3 fusion patterns (his notebook is in this dir). Treat the table below
> as candidate *fodder* names only, never as scores.

## The real game (corrected — this overrides the per-task-solve thesis)

NeuroGolf 2026 is **not** "hand-build the smallest ONNX for each of 400
tasks". Notebook intel from the LB leaders proves it is a **public-bundle
blend + grader-faithful rewrite** game. Octaviograu's
`5743-35-canonical-onnx-fusions` notebook, verbatim:

> "no human ONNX hand-building, no models trained. Sources reused verbatim
> from public CC0 bundles."

LB context (from notebooks): "5.5 or 4.7?" 7441 · David 7380 ·
keymoon 7271 · Octaviograu 5744→6042. None hand-solve tasks. Their edge is
**(a) freshest/strongest public bundles + (b) per-task cheapest-valid
selection + (c) the 3 grader-faithful fusion rewrites.** The 7441↔5744 gap
is bundle quality, not solving cleverness.

## The grader-faithfulness law (explains our ~7% projected↔actual gap)

Octaviograu's local oracle predicts grader cost **to the hundredth** for
well-formed ONNX. His two negative results define the boundary:

- **Grader-faithful (projected == actual):** rewrites that *remove nodes*
  or *narrow dtypes within the same op vocabulary*. Also: any ONNX taken
  **verbatim from an already-graded public bundle** (it earned its score).
- **Diverges (passes local verify, 0 LB):** rewrites that *introduce new
  op chains that did not previously exist* (Or/And trees — and by extension
  **our hand-built Where/Greater/Conv graphs**).

⇒ Our 77 hand-built + Phase-2 family ONNX are the 0-LB class. They inflate
projected and realize ~nothing. **Drop them from the blend candidate pool.**

## Assets in hand (downloaded to `sources/hunt/`, gitignored)

| ref | actual LB | files | note |
|---|---|---|---|
| `beicicc6645` | **6645.39** | 401 in `submission/` + manifest | strongest single |
| `afr6335` | 6335.19 | 401 loose | afr1ste controlled |
| `jsrdcht6029` | 6029.09 | 400 loose | fresh 2026-05-18 |
| `octavia6042` | 6042.85 | `submission.zip` (+3 loose) | hand-built solvers |

Recipe source (not yet pulled): `octaviograu/5743-35-canonical-onnx-fusions`
— full reproducible scanner+rewriter for the 3 fusion patterns
(ReduceSum-chain fusion · Cast-chain collapse · bool-reduction dtype
narrowing). `octaviograu/neurogolf-2026-block-lb-drilling-5740-30` =
prior step. Earlier stale source we used = `afr5689` (5689.51).

## Action plan (positive-EV, in order)

1. **Re-blend on graded bundles only.** Candidate pool =
   {beicicc6645, afr6335, jsrdcht6029, octavia6042, prior afr5689 etc.} —
   **exclude our hand-built 77 / Phase-2 onnx** (0-LB class). Per-task
   cheapest-valid via the official local oracle (`blend.py`). Lower bound
   ≈ 6645 (beicicc verbatim); blend only improves per task.
2. **Sanity baseline:** beicicc6645 verbatim is a known **6645.39** — a
   single submit beats our 5706.97 by +938 with near-zero risk.
3. **Apply the 3 grader-faithful fusion patterns** (Octaviograu recipe) on
   the blended bundle. Bounded but legit gains; local oracle exact.
4. **Submit, gated.** Budget 100/day, A/B single change, no spray. With a
   ~all-verbatim blend the ~7% gap collapses (projected ≈ actual).

## Open questions / next intel

- Current LB top-10 cutoff (was ≈7001; re-pull live LB before targeting).
- Is there a public artifact >6645 (afr1ste/others may post fresher)?
  Re-run the dataset hunt before each submit cycle.
- Octaviograu's 6042 hand-built kernel: are its per-task onnx grader-faithful
  (he claims no hand-building — verify they're bundle-derived) before trusting.

See memory: [[neurogolf-real-game-strategy]],
[[neurogolf-projected-actual-gap]], [[neurogolf-public-bundle-leads]].
