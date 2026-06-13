#!/bin/bash -l
#SBATCH --job-name=ng_fusion
#SBATCH --partition=work
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --output=logs/fusion-%j.out
#SBATCH --error=logs/fusion-%j.err
set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"
echo "host=$(hostname) start=$(date)"
RUN="$TMPDIR/fus"; mkdir -p "$RUN"; cd "$RUN"
$PY "$WORK/Kaggle-Competitions/Better_Golf/fusion_rewrite.py"
echo "end=$(date)"
