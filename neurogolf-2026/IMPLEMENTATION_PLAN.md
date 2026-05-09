# IMPLEMENTATION PLAN - NeuroGolf 2026

## Phase 1: Baseline for Task 6
1. **Analyze Task 6 Data**: Read 	ask006.json, understand grid sizes and logic.
2. **Build PyTorch Baseline**: Create a tiny FCN in PyTorch.
3. **Train on Task 6**: Write a loop to perfectly memorize the examples in Task 6.
4. **ONNX Export & Validate**: Export the model to 	ask006.onnx, run it through 
eurogolf_utils.py to get the score and verify correctness.

## Phase 2: Pipeline Automation
1. **Generalize Training**: Make the PyTorch script work for any 	askXXX.json.
2. **Hyperparameter Search**: Automate finding the smallest working network per task.
3. **Batch Export**: Script to train and export all 400 tasks.
4. **Submission**: Zip and submit to Kaggle.
