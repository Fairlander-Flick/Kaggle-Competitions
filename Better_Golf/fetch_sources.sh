#!/bin/bash
cd "$WORK/Kaggle-Competitions/Better_Golf"
export KAGGLE_CONFIG_DIR=~/.kaggle PYTHONIOENCODING=utf-8
log(){ echo "[$(date +%H:%M:%S)] $*"; }

# Current best public KERNEL outputs (contain submission.zip / onnx)
KERNELS=(
  rajathrpai/neurogolf-6372-62
  rajathrpai/neurogolf-2026-6364-85-hybrid-submission
  vyankteshdwivedi/neurogolf-6372-58
  vyankteshdwivedi/neurogolf-multi-source-onnx-solver
  kojimar/6275-09-lb-audited-neurogolf-onnx-overrides
  thbdh5765/6332-87-lb-neurogolf-audited-merge-handcrafts
  wguesdon/6315-04-lb-neurogolf-audited-base-grafts
  octaviograu/6154-71-onnx-rewrites-hand-built-solvers
  seddiktrk/surgical-onnx-precision-parameter-reduction
  seddiktrk/neurogolf-2026-graph-surgeon
  biohack44/neurogolf-current-public-mixes
  mirzayasirabdullah07/best-score-neurogolf-championship-notebook
  souldrive/compile-don-t-train-onnx-golf-that-scores-2x
  jonathanchan/ngc26-constraint-smart-logic-mix-blending
)
for k in "${KERNELS[@]}"; do
  d="sources/k_$(echo $k | tr '/' '_')"
  mkdir -p "$d"
  log "kernel output: $k"
  kaggle kernels output "$k" -p "$d" >/dev/null 2>"$d/_err.log" && log "  OK $k" || log "  FAIL $k ($(tail -1 $d/_err.log))"
done

# Underlying source DATASETS
DSETS=(
  afr1ste/neurogolf-5689-51-current-rules-open-artifact
  konbu17/neurogolf-2026-blend-source-v3-6-0
)
for ds in "${DSETS[@]}"; do
  d="sources/d_$(echo $ds | tr '/' '_')"
  mkdir -p "$d"
  log "dataset: $ds"
  kaggle datasets download "$ds" -p "$d" --unzip >/dev/null 2>"$d/_err.log" && log "  OK $ds" || log "  FAIL $ds ($(tail -1 $d/_err.log))"
done
log "=== FETCH DONE ==="
ls -d sources/*/ | while read s; do n=$(find "$s" -name 'task*.onnx' 2>/dev/null | wc -l); z=$(find "$s" -name '*.zip' 2>/dev/null | wc -l); echo "  $s  onnx=$n zip=$z"; done
