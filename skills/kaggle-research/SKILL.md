---
name: kaggle-research
description: Research and iterate on Kaggle solutions, discover alternative approaches, evaluate experiments, and deliver submissions using FAU HPC or Kaggle Notebooks.
---

# Kaggle research

Improve the competition objective through informative experiments. Choose methods, tools and implementations freely within the user's task and competition rules. Do not require a sandbox, fixed experiment count, long reporting template or invented GPU-hour/GPU-count ceiling.

Read or create the workspace `runtime-profile.md` using the [template](references/runtime-profile.md). Discover actual resource access and platform constraints. Execute the requested phase; a planning/review request does not launch jobs or submissions.

## Research loop

- Establish a reproducible, competitive baseline, a trustworthy evaluator and concrete error examples. Distinguish reproduced results from published claims.
- Ask which assumption currently limits progress: available information, data coverage, representation, target, learning, candidate generation/selection or inference cost.
- Consider genuinely different approaches early. Revisit them when structural errors persist, even if small score gains continue. Model/seed variants alone are not distinct research directions.
- Choose an experiment that can change the next decision. State briefly what it tests, what result would matter and what happens next. New hypotheses need a plausible mechanism, not an existing winning precedent.
- Separate **continue research**, **scale the approach** and **replace the incumbent**. An incomplete prototype can justify further investigation without becoming the submission candidate. Preserve the incumbent while exploring.
- Save the finding, its conditions and the next decision. Transfer useful mechanisms where their assumptions match. Continue while worthwhile experiments and resources remain.

Seed repeats resolve uncertainty or support a justified ensemble. Avoid seed shopping and unexplained sweeps. Short user output must not reduce evaluation quality.

## Load details only when relevant

| Need | Reference |
|---|---|
| Choose an experiment, discover an approach or reconsider assumptions | [decisions.md](references/decisions.md) |
| Build evaluation or accept a candidate | [validation.md](references/validation.md) |
| Run/recover FAU jobs or choose a fallback | [fau-runtime.md](references/fau-runtime.md) |
| Rehearse, submit or select final versions | [kaggle-delivery.md](references/kaggle-delivery.md) |
| Resume work or save findings | [state-and-output.md](references/state-and-output.md) |
| Find a relevant precedent | [evidence.md](references/evidence.md) |

User updates: up to three short lines in the user's language, **Result / Decision / Next**, at meaningful transitions. Keep logs and reproducible evidence in files; do not dump them into chat. Final: a few concise bullets and artifact links.
