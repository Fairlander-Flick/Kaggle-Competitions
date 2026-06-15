#!/bin/bash -l
#SBATCH --job-name=nngolf
#SBATCH --partition=rtx3080
#SBATCH --gres=gpu:1
#SBATCH --time=01:30:00
#SBATCH --output=logs/nn/arr-%A_%a.out
#SBATCH --error=logs/nn/arr-%A_%a.err
set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"
LINE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" tasklist_shallow.txt)
set -- $LINE; TASK=$1; MAXCOST=$2
TT=$(printf "%03d" "$TASK")
echo "host=$(hostname) task=$TASK maxcost=$MAXCOST start=$(date)"
$PY nngolf.py "$TASK" --seeds 3 --epochs 3000 --max-cost "$MAXCOST" \
    --out "out/nn/task${TT}.onnx" > "logs/nn/task${TT}.json" 2>>"logs/nn/task${TT}.err"
cat "logs/nn/task${TT}.json"
echo "end=$(date)"
