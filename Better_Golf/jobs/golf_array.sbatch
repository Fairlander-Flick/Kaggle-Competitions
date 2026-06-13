#!/bin/bash -l
#SBATCH --job-name=ng_golf
#SBATCH --partition=work
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH --array=0-39%16
#SBATCH --output=logs/golf-%A_%a.out
#SBATCH --error=logs/golf-%A_%a.err
# Fan 400 tasks across the cluster: chunk = 10 tasks/element, 40 elements, <=16 concurrent.
set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"
CHUNK=10
A=$(( SLURM_ARRAY_TASK_ID * CHUNK + 1 ))
B=$(( A + CHUNK - 1 ))
echo "host=$(hostname) array=$SLURM_ARRAY_TASK_ID tasks=$A..$B start=$(date)"
RUN="$TMPDIR/golf_$SLURM_ARRAY_TASK_ID"; mkdir -p "$RUN"; cd "$RUN"
$PY "$WORK/Kaggle-Competitions/Better_Golf/golf2.py" "$A" "$B"
echo "end=$(date)"
