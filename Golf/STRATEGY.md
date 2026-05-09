# STRATEGY - NeuroGolf 2026

## 1. Baseline Model Architecture
- **Input:** [1, 10, H, W] where H, W <= 30. Since shapes must be static, we might need a generic [1, 10, 30, 30] processor or dynamic inputs (wait, rule says "Statically-defined shapes constraint is strictly enforced", but ARC grids vary in size. We must pad them to 30x30 or use [1, 10, 30, 30] statically).
- **Core Architecture:**
  - A simple Fully Convolutional Network (FCN).
  - Use 1x1, 3x3 convolutions.
  - To minimize parameters, use grouped convolutions or depthwise separable convolutions.
  - To minimize memory footprint, avoid large intermediate feature maps. Maintain small channel depths (e.g., 10 -> 16 -> 10).
- **Output:** [1, 10, 30, 30] logits. Argmax over the channel dimension to get [1, 30, 30] and then crop/mask back to original size if needed (or ONNX handles output matching).

## 2. Training Strategy
- Write a PyTorch training loop for a specific task.
- Train the model using CrossEntropyLoss against the expected output grid one-hot.
- Augment data (rotations, flips, color permutations) if necessary to prevent overfitting, though we only have a few examples per task.
- Overfit the training examples perfectly.

## 3. Export & Optimization
- Export PyTorch model to ONNX using 	orch.onnx.export.
- Run ONNX Simplifier (onnxsim) to fold constants and reduce node counts.
- Quantize the model or use half precision (float16) to halve the parameter footprint.

## 4. Submission Pipeline
- Automate training for all 400 tasks.
- For tasks where training fails to converge, use a fallback (e.g., simple identity or majority color).
- Package 400 ONNX files into a submission zip.
