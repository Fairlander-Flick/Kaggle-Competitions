#!/bin/bash -l
#SBATCH --job-name=ng_render
#SBATCH --partition=rtx3080
#SBATCH --gres=gpu:1
#SBATCH --time=00:30:00
#SBATCH --output=logs/render-%j.out
#SBATCH --error=logs/render-%j.err
set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"
echo "start=$(date)"; $PY render_all.py; echo "end=$(date)"
