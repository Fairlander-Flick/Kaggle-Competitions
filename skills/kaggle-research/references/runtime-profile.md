# Per-competition runtime profile

Use this as a short workspace note, adapting fields to the task. Discover facts rather than asking the user for information the environment already provides.

## Competition

- Assigned competition, objective/direction, deadline and current rules.
- Submission type, daily team quota and final-selection count.
- Permitted external data, API use, test-time adaptation and internet.
- Final inference hardware, memory, runtime and output format.

## Resources

- Preferred execution: FAU HPC; discover host, account access, scheduler/wrapper, partitions, GPUs and environment.
- Persistent data, code, checkpoint and artifact locations.
- Kaggle Notebook fallback when useful; discover actual remaining quota.
- No skill-imposed GPU-hour, GPU-count, concurrency or campaign-duration cap.
- Choose job walltime and resources within actual scheduler/account policies.
- Apply additional compute limits only when explicitly set by the user.
- Paid external model/API allowance: zero until explicitly configured.

## Decisions

- Submission policy: informative probing when time permits; batch locally verifiable refinements; preserve deployment/recovery time near deadline. No universal reserved-slot count.
- Continue while experiments are worthwhile and resources remain. Stop for user direction, real access/quota limits, deadline or lack of a justified next experiment.
- Output: user language; brief Result / Decision / Next updates.

Writing this profile does not launch jobs or submissions. The bundled source cards work without a separate database; configure a larger research corpus only if available and useful.
