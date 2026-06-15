#!/bin/bash -l
#SBATCH --job-name=nnwinb
#SBATCH --partition=rtx3080
#SBATCH --gres=gpu:1
#SBATCH --time=12:00:00
#SBATCH --output=logs/nn/winb-%A_%a.out
#SBATCH --error=logs/nn/winb-%A_%a.err
set -e
cd "$WORK/Kaggle-Competitions/Better_Golf"
PY="$WORK/software/private/conda/envs/kaggle/bin/python"
LINE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" tasklist_nnwin_b.txt)
set -- $LINE; TASK=$1; MAXCOST=$2; TT=$(printf "%03d" "$TASK")
echo "host=$(hostname) task=$TASK maxcost=$MAXCOST start=$(date)"
$PY nngolf.py "$TASK" --seeds 16 --epochs 30000 --maxwidth 6 --max-cost "$MAXCOST" \
    --out "out/search/task${TT}.onnx" > "logs/nn/win${TT}.json" 2>>"logs/nn/win${TT}.err"
cat "logs/nn/win${TT}.json"; echo "end=$(date)"
