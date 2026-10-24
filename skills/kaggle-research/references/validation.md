# Evaluation and candidate acceptance

Determine the independent unit from the data-generating process: person, document, embryo, well, time, source or task family. Choose grouped, temporal or random splits accordingly and save membership. Verify the metric and representative failure examples before optimizing.

Separate development from confirmation. Repeatedly consulted holdouts become development evidence; track that exposure and preserve a suitable confirmation check when feasible. A tiny saturated validation set may need better measurement rather than more tuning.

Keep learned preprocessing within fold boundaries. Trace synthetic examples, near-duplicates, teacher labels and external data to their sources. Distinguish OOF targets from predictions on a model's own training fold. The latter can diagnose data issues but do not measure generalization. Test-time adaptation and test-text use must satisfy actual competition rules.

## Research progress versus candidate acceptance

A prototype can demonstrate a mechanism without beating the incumbent. Use that to decide a specific next research step; read [decisions](decisions.md). Do not submit it on that basis alone.

Accept a candidate using the same eligible evaluation as its parent: overall objective, relevant slices, uncertainty where consequential, and actual inference cost. A component metric alone is insufficient. Rebuild/evaluate the actual artifact; an agent narrative or stale metric file is not evidence. Retain a working parent until acceptance.

Record whether effects are supported, uncertain or confounded and which scores were visible at decision time. Retrospective private results cannot guide a live decision. Public feedback helps diagnose deployment/distribution differences but repeated selection consumes information.

After recipe selection, full-data training may be appropriate. Preserve the recipe's validation evidence; its final training score is not a new held-out result.
