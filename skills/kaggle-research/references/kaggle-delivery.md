# Notebook execution and submissions

Read current competition rules: classic/code type, metric, deadline, team quota, final-selection count, required output, hardware/runtime/internet constraints and permitted external data. Do not assume fixed daily limits, two final selections or a particular public/private ratio.

Keep notebook execution, scored submission and final selection distinct. A successful notebook run is not a scored submission; a scored version is not necessarily selected for the final evaluation. Classic competitions may accept prediction files; code competitions require the prescribed Kaggle Notebook route. Verify the supported tool/CLI interface before use.

## Candidate and execution check

Check candidate identity, pinned notebook/model/data versions, dependencies, output IDs/order/schema and valid values. Rehearse the exact inference pipeline under realistic workload and Kaggle constraints. Successful visible execution does not prove the hidden rerun will succeed.

Read remote team quota and history. Record intent before submit and store the returned ID immediately. If connectivity fails or acceptance is uncertain, reconcile remote history by candidate/version before retrying; do not spend duplicate slots. Monitor the existing evaluation until terminal state and distinguish runtime errors from low scores.

## Adaptive probing

- Strong local verifier: batch refinements; submit milestone bundles or consequential hidden-distribution/deployment checks.
- Useful but uncertain CV: choose differentiated probes that test important assumptions; preserve local and public evidence separately.
- Objective poorly measurable locally: use quota actively for well-formed alternatives with named questions.
- Plenty of time: use available slots aggressively when results can change a decision. No informative candidate means no obligation to spend a slot.
- Near deadline: prioritize reliable deployment and final selection, allowing realistic time/slots for recovery.

Reassess from actual feedback, quota and remaining time. No universal reserved-slot count or public-score threshold.

Select final candidates using defensible evaluation, robustness, deployment reliability and useful diversity among allowed selections. Public scores are contextual evidence, not an automatic maximum-score rule. Freeze dependencies and verify selected version IDs before the deadline.

Source: [Kaggle competition documentation](https://www.kaggle.com/docs/competitions).
