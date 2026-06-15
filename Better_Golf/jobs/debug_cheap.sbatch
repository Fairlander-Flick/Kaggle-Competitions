#!/bin/bash -l
#SBATCH --job-name=ng_cheap
#SBATCH --partition=rtx3080
#SBATCH --gres=gpu:1
#SBATCH --time=00:40:00
#SBATCH --output=logs/cheap-%j.out
#SBATCH --error=logs/cheap-%j.err
set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"
echo "start=$(date)"; $PY debug_cheap.py; echo "end=$(date)"
