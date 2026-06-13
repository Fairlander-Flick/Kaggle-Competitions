#!/bin/bash -l
#SBATCH --job-name=ng_blend
#SBATCH --partition=work
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --output=logs/blend-%j.out
#SBATCH --error=logs/blend-%j.err
# CPU-only ONNX official-verify blend. TinyGPU rejects CPU-only jobs, so we
# request 1 GPU and just use CPU cores. Runs the grader-faithful cheapest-valid
# -per-task blend over sources/** (--no-ours: public graded graphs only).

set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"

echo "host=$(hostname) start=$(date)"
# run in a scratch CWD so ORT profiling json files don't clutter the repo,
# but blend.py uses paths relative to its own file, so symlink it in.
RUN="$TMPDIR/blendrun"; mkdir -p "$RUN"; cd "$RUN"
$PY "$WORK/Kaggle-Competitions/Better_Golf/blend.py" --no-ours
# blend.py writes out/submission.zip + logs/blend_results.json relative to BASE
# (=Better_Golf), so artifacts already land in the repo. Clean ORT traces here.
echo "end=$(date)"
ls -la "$WORK/Kaggle-Competitions/Better_Golf/out/submission.zip"
