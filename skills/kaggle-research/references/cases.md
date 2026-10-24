# Selected GOLD solution cards

Reviewed source reports; not independently reproduced. Read matching cards only. Mechanism/transfer statements are research interpretations, not causal guarantees.

## 726654 — Representation changes

2026 · neurogolf-2026 · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/neurogolf-2026/writeups/1st-place-kaggle-agent)

- Observed: The winner reports substantially larger average gains from architectural rewrites than local graph optimization.
- Transfer: Explore a different representation, not just node-level edits.
- Limit: The introductory post does not provide a controlled causal comparison.

## 727356 — Task memory and transfer

2026 · neurogolf-2026 · rank 3 GOLD · [primary writeup](https://www.kaggle.com/competitions/neurogolf-2026/writeups/3rd-place-solution-writeup)

- Observed: Workers receive builders, histories, rejected branches and donor methods; full rewrites precede local optimization.
- Transfer: Keep a reliable incumbent while prototyping and transfer mechanisms across compatible tasks.
- Limit: Consensus-filtered examples can be biased; separate fresh generator examples caught failures.

## 651671 — Synthetic programs and candidate selection

2025 · arc-prize-2025 · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/arc-prize-2025/writeups/nvarc)

- Observed: Separate input/output program generation and consistency filtering support puzzle training; adaptation and search use constrained inference time.
- Transfer: Diagnose generation, selection and execution cost separately.
- Limit: TRM did not improve the large Qwen branch; some stronger rescoring results were post-deadline.

## 574765 — Knowledge versus inference throughput

2025 · ai-mathematical-olympiad-progress-prize-2 · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/ai-mathematical-olympiad-progress-prize-2/writeups/nemoskills-1st-place-solution-nemoskills)

- Observed: CoT/tool-use training is combined with fast inference and early stopping.
- Transfer: Optimize correctly completed problems under actual deployment constraints.
- Limit: Reported training compute is historical, not a minimum requirement or default budget.

## 744980 — End-to-end tracking

2026 · biohub-cell-tracking-during-development · rank 10 GOLD · [primary writeup](https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/writeups/10th-place-solution-grandmaster-powered-agentic-a)

- Observed: Agent-assisted components are developed under whole-embryo validation.
- Transfer: Accept detection/linking changes on final tracking behavior and relevant distribution shift.
- Limit: More detection recall or aggressive gap filling did not automatically improve tracking.

## 551688 — Downstream retrieval and targeted synthesis

2024 · eedi-mining-misconceptions-in-mathematics · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/eedi-mining-misconceptions-in-mathematics/writeups/mth-101-1st-place-detailed-solution)

- Observed: Confused misconceptions guide data generation; retrieval selection prioritizes candidate recall for subsequent rankers.
- Transfer: Choose component metrics from what the next stage actually needs.
- Limit: Some MAP gains did not improve recall; retrospective private ablations include bundled changes.

## 551651 — Allocate inference to the useful stage

2024 · eedi-mining-misconceptions-in-mathematics · rank 2 GOLD · [primary writeup](https://www.kaggle.com/competitions/eedi-mining-misconceptions-in-mathematics/writeups/cqyr-2nd-place-solution)

- Observed: Smaller retriever ensembles leave time for large rerankers; label explanations can be precomputed.
- Transfer: Separate offline information creation from online cost.
- Limit: Larger retrievers/CoT can consume time better used downstream; one late candidate timed out.

## 473295 — Coverage of generation styles

2024 · llm-detect-ai-generated-text · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/llm-detect-ai-generated-text/writeups/comprehensive-1st-place-write-up)

- Observed: Iterative synthetic/perturbed data mixes address detector blind spots; diverse model families contribute.
- Transfer: Inspect errors by source and transformation, not only aggregate score.
- Limit: Public-score selection and transductive text use need task-specific interpretation and rule checks.

## 446422 — Recover missing information

2023 · kaggle-llm-science-exam · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/kaggle-llm-science-exam/writeups/team-h2o-llm-studio-1st-place-solution)

- Observed: A classifier plateau leads to retrieval; corpus rendering/context construction and validation are revisited.
- Transfer: Test whether supplying better information beats further classifier tuning.
- Limit: More training data and reversed context order did not consistently help; the small validation saturated.

## 684353 — Data extraction and alignment

2026 · deep-past-initiative-machine-translation · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/writeups/dpc-1st-data-quality-dictates-everything)

- Observed: OCR/LLM extraction, difficult-document inspection and alignment repair precede model scaling.
- Transfer: Use source-level diagnosis when model errors cluster around documents or length mismatches.
- Limit: Own-training-fold predictions diagnose data quality, not OOF generalization; more synthetic data was not uniformly better.

## 613305 — Decision-token supervision

2025 · jigsaw-agile-community-rules · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/jigsaw-agile-community-rules/writeups/1st-place-solution)

- Observed: Training/inference focus on classification tokens and rank aggregation.
- Transfer: Avoid unnecessary generation when the output is a decision.
- Limit: The author explicitly used public selection; this does not establish a universal validation policy.

## 569902 — Distillation and selective augmentation

2025 · wsdm-cup-multilingual-chatbot-arena · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/wsdm-cup-multilingual-chatbot-arena/writeups/whitefebruary-1st-place-solution)

- Observed: OOF teacher probabilities support student training; expensive response-swap augmentation targets uncertain cases.
- Transfer: Allocate extra inference where it changes decisions.
- Limit: Critique/pruning attempts failed; the author also disclosed an unverified external-data overlap concern.

## 527629 — Compress expensive knowledge

2024 · lmsys-chatbot-arena · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/lmsys-chatbot-arena/writeups/blackpearl-no-leak-1st-place-solution-distill-is-a)

- Observed: Large fold teachers provide soft targets for a smaller quantized student.
- Transfer: Consider training-time knowledge transfer when inference is the bottleneck.
- Limit: An uploaded dependency deletion caused submission failure; intermediate metrics are not final official results.

## 711570 — Target correctness versus imitation

2026 · nvidia-nemotron-model-reasoning-challenge · rank 9 GOLD · [primary writeup](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/writeups/9th-place-solution-human-auditable-cot)

- Observed: Curated deterministic reasoning traces are checked separately from the student’s predictions.
- Transfer: Measure source-correct/student-wrong errors before adding data or changing capacity.
- Limit: Cryptarithm remained weak; consistent formatting did not replace missing solver coverage.

## 494343 — Metric behavior

2024 · llm-prompt-recovery · rank 1 GOLD · [primary writeup](https://www.kaggle.com/competitions/llm-prompt-recovery/writeups/khoi-nguyen-1st-place-solution-adversarial-attack)

- Observed: The solution analyzes evaluator tokenization/embedding behavior in prompt recovery.
- Transfer: Understand the objective and what score improvements represent.
- Limit: A task-specific metric effect is not evidence of general semantic improvement or a transferable recipe.

## 497367 — Synthetic text with programmatic labels

2024 · pii-detection-removal-from-educational-data · rank 4 GOLD · [primary writeup](https://www.kaggle.com/competitions/pii-detection-removal-from-educational-data/writeups/4th-place-solution-llama3-70b-is-all-you-need)

- Observed: LLM-generated examples, programmatic PII labels and false-positive-focused paraphrases support a smaller final model.
- Transfer: Choose synthesis from a measured coverage gap and check alignment.
- Limit: Other synthetic datasets and filtering classifiers did not help; a large generator is not the final predictor.
