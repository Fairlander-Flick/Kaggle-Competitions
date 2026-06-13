#!/bin/bash -l
#SBATCH --job-name=ng_convgolf
#SBATCH --partition=work
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --output=logs/convgolf-%j.out
#SBATCH --error=logs/convgolf-%j.err
set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"
echo "host=$(hostname) start=$(date)"
RUN="$TMPDIR/cg"; mkdir -p "$RUN"; cd "$RUN"
$PY "$WORK/Kaggle-Competitions/Better_Golf/golf_conv.py" 1 400
echo "end=$(date)"
