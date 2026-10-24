# FAU execution and fallback

Discover the host, accessible clusters, scheduler entrypoint, environment and persistent storage. Use actual account rights; do not assume Alex/Helma access. Run training and heavy preprocessing through Slurm, not a login node. TinyGPU/TinyFat may require wrappers such as `sbatch.tinygpu`; verify the relevant cluster documentation.

Choose GPU type/count, concurrency and job walltime from the experiment and actual scheduler policies. Do not invent campaign GPU-hour, fixed concurrency or total-duration caps. Measure throughput/memory when sizing is uncertain; track resource use to compare methods. Respect any explicit user budget and real account/platform quota. Paid external APIs need a configured spending allowance.

Persist experiment identity, output/checkpoint location and requested resources before launch; record the returned job ID immediately. Follow the existing job. A queued job is not an experimental failure. Inspect bounded log tails and status, back off when unchanged, and do not report every poll.

Stage data where useful. Copy required artifacts to persistent storage before a job ends; node-local temporary storage may be deleted. Checkpoint/resume work that exceeds actual per-job limits.

Use Kaggle Notebook fallback when accessible hardware, queue delay or deadline makes it appropriate and platform quota/rules allow. Do not run duplicate attempts across backends: reconcile the existing job before relaunching, and cancel only the duplicate belonging to that attempt. Never cancel unrelated jobs.

Code competitions require final inference in the prescribed Kaggle environment even if trained on FAU; read [delivery](kaggle-delivery.md).

Current operational sources: [FAU Slurm](https://doc.nhr.fau.de/batch-processing/batch_system_slurm/), [cluster overview](https://doc.nhr.fau.de/clusters/overview/). Read cluster-specific details only when needed.
