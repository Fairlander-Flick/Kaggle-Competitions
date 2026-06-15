#!/bin/bash -l
#SBATCH --job-name=ng_sweep
#SBATCH --partition=rtx3080
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --output=logs/sweep-%j.out
#SBATCH --error=logs/sweep-%j.err
set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"
echo "host=$(hostname) start=$(date) cores=$(nproc)"
seq 1 400 | xargs -P 16 -I{} $PY solve_task.py {} > /dev/null 2>>logs/sweep/errors.log
echo "solved jsons: $(ls logs/sweep/task*.json 2>/dev/null | wc -l)"
echo "end=$(date)"
