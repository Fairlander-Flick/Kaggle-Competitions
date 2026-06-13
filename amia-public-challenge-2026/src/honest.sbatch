#!/bin/bash -l
#SBATCH --job-name=amia-honest
#SBATCH --gres=gpu:a100:1
#SBATCH --partition=a100
#SBATCH --time=12:00:00
#SBATCH --output=logs/honest-%j.out
#SBATCH --error=logs/honest-%j.err
#SBATCH --export=NONE
unset SLURM_EXPORT_ENV
set -euo pipefail
echo "node=$(hostname) jobid=$SLURM_JOB_ID start=$(date -Is)"
RUN="$SLURM_SUBMIT_DIR"; cd "$RUN"
module load python/3.12-conda
source activate /home/woody/dsaa/dsaa115h/software/private/conda/envs/kaggle
export HF_HOME=$HOME/.cache/huggingface
export YOLO_CONFIG_DIR=$TMPDIR/ultra
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
# stage data to node-local $TMPDIR (fast I/O)
echo "staging data -> $TMPDIR ..."
mkdir -p "$TMPDIR/data"
cp "$RUN"/data/*.csv "$TMPDIR/data/"
cp -r "$RUN"/data/train "$TMPDIR/data/train"
cp -r "$RUN"/data/test  "$TMPDIR/data/test"
echo "staged: $(ls $TMPDIR/data/train/train | wc -l) train, $(ls $TMPDIR/data/test/test | wc -l) test"
export DATA_DIR="$TMPDIR/data" JOB_TMP="$TMPDIR"
export MODEL="$RUN/yolo11l.pt" IMGSZ=1024 EPOCHS=60 BATCH=16
export CLS_ARCH=tf_efficientnet_b3.ns_jft_in1k CLS_IMG=512 CLS_EP=12 CLS_BS=48
export DET_THR=0.05 NF_POW=1.0
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
python jobs/honest_train.py
echo "done=$(date -Is)"
