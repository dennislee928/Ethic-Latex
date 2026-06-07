import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from erh.tools.loss import ERHRegularizationLoss

# 1. Generate Synthetic Data
# We create a simple binary classification task where complexity (x) is an input.
# Noise increases with complexity, potentially leading to high error growth (alpha).
np.random.seed(42)
torch.manual_seed(42)

def generate_data(n=2000):
    # Complexity x in [1, 100], then normalized to [0, 1] for the loss function
    complexity_raw = np.random.zipf(a=2.0, size=n)
    complexity_raw = np.clip(complexity_raw, 1, 100)
    complexity_norm = (complexity_raw - 1) / 99.0
    
    # Feature: alignment with ground truth
    # Increase noise even more: up to 10.0 at x=100
    noise_level = 10.0 * (complexity_raw / 100.0)
    v = np.random.choice([-1, 1], size=n)
    features = v + np.random.normal(0, noise_level, size=n)
    
    # Targets: 0 or 1
    targets = (v + 1) // 2
    
    return (torch.tensor(features, dtype=torch.float32).unsqueeze(1),
            torch.tensor(targets, dtype=torch.float32).unsqueeze(1),
            torch.tensor(complexity_norm, dtype=torch.float32).unsqueeze(1),
            complexity_raw)

X, y, complexity_norm, complexity_raw = generate_data()

# 2. Simple Neural Network
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(1, 10),
            nn.ReLU(),
            nn.Linear(10, 1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.fc(x)

def train_model(use_erh=False, epochs=50):
    model = SimpleModel()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    if use_erh:
        # Increase lambda to 10.0
        criterion = ERHRegularizationLoss(lambd=10.0, gamma=0.5)
    else:
        criterion = nn.BCELoss()
        
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X)
        if use_erh:
            loss = criterion(outputs, y, complexity_norm)
        else:
            loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
    
    return model

print("Training Baseline Model...")
model_baseline = train_model(use_erh=False)
print("Training ERH-Regularized Model...")
model_erh = train_model(use_erh=True)

# 3. Evaluation and Alpha Calculation
def evaluate_and_get_alpha(model, name):
    model.eval()
    with torch.no_grad():
        probs = model(X).numpy().flatten()
        preds = (probs > 0.5).astype(float)
        targets = y.numpy().flatten()
        
        # Mistakes identified as "ethical primes" (simplified)
        errors = (preds != targets).astype(float)
        
        # Sort by complexity
        sort_idx = np.argsort(complexity_raw)
        c_sorted = complexity_raw[sort_idx]
        e_sorted = errors[sort_idx]
        
        # Compute Π(x): cumulative count of errors up to complexity x
        unique_x = np.arange(1, 101)
        pi_x = np.zeros(100)
        for i, x in enumerate(unique_x):
            pi_x[i] = np.sum(e_sorted[c_sorted <= x])
            
        # Compute baseline B(x) = beta * x (assuming linear growth for errors)
        # Use average error rate to estimate beta
        beta = np.mean(errors)
        b_x = beta * unique_x
        
        # Error term E(x) = Π(x) - B(x)
        e_x = pi_x - b_x
        abs_e_x = np.abs(e_x)
        
        # Fit alpha: log|E(x)| = alpha * log(x) + log(C)
        # Use regions where |E(x)| > 0 and x > 5
        mask = (abs_e_x > 0) & (unique_x > 5)
        if np.sum(mask) < 5:
            # Fallback if too few errors
            alpha = 0.0
        else:
            res = linregress(np.log(unique_x[mask]), np.log(abs_e_x[mask]))
            alpha = res.slope
        
        print(f"{name} - Accuracy: {np.mean(preds == targets):.4f}, Alpha: {alpha:.4f}")
        return unique_x, abs_e_x, alpha

x_vals, err_baseline, alpha_baseline = evaluate_and_get_alpha(model_baseline, "Baseline")
x_vals, err_erh, alpha_erh = evaluate_and_get_alpha(model_erh, "ERH-Regularized")

# 4. Visualization
plt.figure(figsize=(10, 6))
plt.loglog(x_vals, err_baseline, label=f'Baseline (α={alpha_baseline:.2f})')
plt.loglog(x_vals, err_erh, label=f'ERH-Regularized (α={alpha_erh:.2f})')
plt.loglog(x_vals, x_vals**0.5, '--', color='gray', label='ERH Bound (α=0.5)')
plt.xlabel('Complexity x')
plt.ylabel('|E(x)|')
plt.title('Error Growth Comparison: Baseline vs ERH-Regularized')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.savefig('erh_regularization_comparison.png')
print("Comparison plot saved as 'erh_regularization_comparison.png'")
