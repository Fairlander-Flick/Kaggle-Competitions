# INTELLIGENCE REPORT - NeuroGolf 2026

> **Purpose:** Gathered by Gemini (Architect & Implementer) via web search and rules analysis.

## 1. Competition Mechanics
- **Goal:** Solve ARC-AGI tasks using Neural Networks saved as ONNX files. Minimize network size (Memory Footprint + Parameter Count).
- **Format:** Submissions must be exactly one ONNX file per task (max 1.44 MB).
- **Metric:** Cost = Cumulative Memory Footprint + Parameter Count. MACs were removed from the metric due to exploits.
- **Constraints:**
  - Banned Ops: Loop, Scan, NonZero, Unique, Script, Function, Compress.
  - Statically defined shapes enforced. No sequences or non-positive tensor dimensions.
  - Multi-input/multi-output graphs disallowed.

## 2. Input/Output Setup
- Input grids (max 30x30) are converted to [1, 10, 30, 30] one-hot encoded tensors.
- Exact match is required.
- The 
eurogolf_utils.py contains the validator and scoring function.

## 3. Discussion Insights & "Magic" Tricks
- **Cost Metric Update:** May 4th update removed MACs. Only memory and params matter.
- **Architecture Idea:** Use standard CNNs with depthwise separable convolutions or tiny MLPs. 
- **Optimization:** Constant folding is enabled on the server. Weight quantization (e.g., int8) might be beneficial if supported, but typically float32/float16 are used depending on ONNX constraints. We should check if we can store weights as float16/int8.
- **Starting Tasks:** The organizers suggest starting with #6, #95, #127, #261, #331.

