import torch
import torch.nn as nn
import torch.nn.functional as F

class ERHRegularizationLoss(nn.Module):
    """
    Ethical Riemann Hypothesis (ERH) Regularization Loss.
    
    This loss function penalizes errors on high-complexity inputs more heavily,
    forcing the model to maintain structural stability (low alpha) during training.
    
    Formula:
        Total Loss = Task Loss + lambda * (Task Loss * complexity^gamma)
    """
    def __init__(self, task_loss_fn=nn.BCELoss(reduction='none'), lambd=0.1, gamma=0.5):
        super(ERHRegularizationLoss, self).__init__()
        self.task_loss_fn = task_loss_fn
        self.lambd = lambd
        self.gamma = gamma

    def forward(self, outputs, targets, complexity):
        """
        Args:
            outputs (Tensor): Model predictions (e.g., probabilities).
            targets (Tensor): Ground truth labels.
            complexity (Tensor): Normalized complexity values [0, 1] for each sample.
        """
        # Ensure complexity is a tensor and has the same shape as targets
        if not isinstance(complexity, torch.Tensor):
            complexity = torch.tensor(complexity, device=outputs.device, dtype=outputs.dtype)
        
        # Calculate base task loss per sample
        base_loss = self.task_loss_fn(outputs, targets)
        
        # Calculate ERH penalty: weight errors by complexity^gamma
        # High complexity (near 1.0) gets full lambd penalty, 
        # Low complexity gets lower penalty.
        erh_penalty = base_loss * torch.pow(complexity, self.gamma)
        
        # Total loss is the mean of (base_loss + lambd * erh_penalty)
        total_loss = torch.mean(base_loss + self.lambd * erh_penalty)
        
        return total_loss

def erh_weighted_cross_entropy(outputs, targets, complexity, lambd=0.1, gamma=0.5):
    """Functional version of ERHRegularizationLoss for CrossEntropy."""
    base_loss = F.cross_entropy(outputs, targets, reduction='none')
    erh_penalty = base_loss * torch.pow(complexity, self.gamma)
    return torch.mean(base_loss + lambd * erh_penalty)
