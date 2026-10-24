# Discover and choose experiments

Start from measured errors and the task's structure. A useful experiment changes a research decision; novelty alone and a high experiment count are not objectives.

## Establish the starting point

Reproduce an appropriate strong baseline and verify the metric on examples. Save predictions, split identity, resource usage and representative failures. Inspect relevant public methods without treating their scores as reproduced evidence. Avoid spending the whole campaign optimizing a weak or incorrectly evaluated starting point.

## Question the current formulation

Choose the questions relevant to the bottleneck:

- What information does the current input or representation discard? Can retrieval, alignment, a different unit of prediction or domain structure recover it?
- Are labels, coverage or synthetic targets wrong or incomplete? Which error slice would additional data address, and how would its correctness be checked?
- Is the learning objective aligned with the required decision? Could a ranking, decomposition, deterministic component or different target express it better?
- Can known invariances or constraints reduce the problem? Are we asking a model to learn something that can be computed or verified directly?
- Can costly teacher knowledge be obtained during training and compressed into cheap inference? Is routing or candidate selection the real bottleneck?

Generate a few meaningfully different mechanisms when useful; do not fill a fixed idea quota. Identify which assumption each changes. The precedent need not use the same modality or model.

## Make the next run informative

Keep a compact decision note: **observation → hypothesis → intervention/control → decisive result → next decision**. Add expected resource needs when consequential. Do not invent success thresholds or a numerical ROI score; use measured variation, practical benefit and feasibility.

Use a small faithful prototype where it answers the question. Preserve relevant groups, rare cases and deployment behavior. For a new method requiring coupled components, build the smallest complete pipeline first; label bundled effects and separate them later if important. An incomplete implementation does not refute the method.

| Diagnostic evidence | Direction to investigate |
|---|---|
| Correct candidate missing | Retrieval/data coverage; measure recall and downstream benefit |
| Candidate present but chosen incorrectly | Reranker/selector; separate pool quality from selection quality |
| Teacher target wrong versus student failing on correct targets | Target construction versus learnability/capacity |
| Error concentrated by source, group or document | Coverage, labels, parsing/alignment or split design |
| Better component, unchanged overall score | Interface, downstream bottleneck or total runtime |
| Cost grows while the same structural errors persist | Different representation, decomposition or data strategy |

Validation-only oracle interventions can diagnose missing information or selection failures. Mark them non-deployable; their scores are not necessarily mathematical upper bounds.

## Make three different decisions

- **Continue research:** the proposed mechanism shows evidence, the remaining defect is identifiable and a specific next experiment can resolve it. A lower first end-to-end score need not kill the branch.
- **Scale:** the signal survives a more faithful evaluation and the expected total resource cost is justified.
- **Replace the incumbent:** end-to-end quality, robustness and deployment constraints support the new artifact. Until then keep the reliable parent.

Do not protect speculative branches indefinitely. Stop or redirect when their premise is contradicted, the next run would teach nothing useful, prerequisites fail, or another direction has a stronger case. Retry when the conditions change.

Keep exploration of different assumptions alongside refinement of supported approaches; choose their balance from remaining uncertainty, opportunity and deadline. Cheap predictable tweaks must not automatically crowd out a consequential uncertain idea. Use repeated seeds/folds when uncertainty could reverse a decision. Use ensembles when complementary errors justify the measured deployment cost.
