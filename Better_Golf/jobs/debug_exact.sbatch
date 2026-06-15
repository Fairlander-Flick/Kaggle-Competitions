#!/bin/bash -l
#SBATCH --job-name=ng_dbg
#SBATCH --partition=rtx3080
#SBATCH --gres=gpu:1
#SBATCH --time=00:25:00
#SBATCH --output=logs/dbg-%j.out
#SBATCH --error=logs/dbg-%j.err
set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"
echo "host=$(hostname) start=$(date)"
$PY debug_exact.py
echo "end=$(date)"
