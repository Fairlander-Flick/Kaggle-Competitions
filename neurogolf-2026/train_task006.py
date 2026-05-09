import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
import os
import sys

# Add utils to path
sys.path.append(os.path.abspath("datasets/neurogolf-2026/neurogolf_utils"))
import neurogolf_utils

class BaselineModel(nn.Module):
    def __init__(self, channels=10):
        super(BaselineModel, self).__init__()
        # Deeper model for larger receptive field (at least 7x7 needed for Task 006)
        self.net = nn.Sequential(
            nn.Conv2d(channels, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, channels, kernel_size=1)
        )
    
    def forward(self, x):
        return self.net(x)

def train_task(task_id):
    # Load data
    with open(f"datasets/neurogolf-2026/task{task_id:03d}.json", "r") as f:
        task_data = json.load(f)
    
    # Combine train, test, and arc-gen for overfitting
    all_examples = task_data["train"] + task_data["test"] + task_data.get("arc-gen", [])
    
    X_train = []
    Y_train = []
    
    for ex in all_examples:
        bench = neurogolf_utils.convert_to_numpy(ex)
        if bench:
            X_train.append(bench["input"])
            # Convert one-hot output to labels for CrossEntropy
            output_labels = np.argmax(bench["output"].squeeze(0), axis=0)
            Y_train.append(output_labels)
    
    X_train = torch.tensor(np.array(X_train)).squeeze(1) # [N, 10, 30, 30]
    Y_train = torch.tensor(np.array(Y_train)).long() # [N, 30, 30]
    
    model = BaselineModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"Training Task {task_id} with {len(X_train)} examples...")
    for epoch in range(1000):
        optimizer.zero_grad()
        outputs = model(X_train) # [N, 10, 30, 30]
        loss = criterion(outputs, Y_train)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 100 == 0:
            # Check accuracy
            preds = torch.argmax(outputs, dim=1)
            correct = (preds == Y_train).all().item()
            print(f"Epoch {epoch+1}, Loss: {loss.item():.6f}, Perfect Match: {correct}")
            if correct and loss.item() < 0.0001:
                break
    
    # Export to ONNX
    model.eval()
    dummy_input = torch.randn(1, 10, 30, 30)
    onnx_path = f"task{task_id:03d}.onnx"
    torch.onnx.export(model, dummy_input, onnx_path, 
                      input_names=['input'], output_names=['output'],
                      dynamic_axes=None) # Shapes must be static
    print(f"Model exported to {onnx_path}")
    
    # Load for verification
    import onnx
    onnx_model = onnx.load(onnx_path)
    
    # Verify using the competition utils
    neurogolf_utils.verify_network(onnx_model, task_id, task_data)
    
if __name__ == "__main__":
    train_task(6)
