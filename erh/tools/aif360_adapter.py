from typing import List, Any, Dict
import pandas as pd
import numpy as np

try:
    from aif360.datasets import BinaryLabelDataset, StandardDataset
    from aif360.metrics import BinaryLabelDatasetMetric
    AIF360_AVAILABLE = True
except ImportError:
    AIF360_AVAILABLE = False

class AIF360Adapter:
    """
    Adapter to convert ERH simulation data into AIF360-compatible datasets
    for fairness analysis.
    """
    
    def __init__(self):
        if not AIF360_AVAILABLE:
            print("Warning: aif360 package not found. Adapter functionality limited.")

    def to_dataset(self, actions: List[Any], protected_attribute: str = 'complexity_group') -> Any:
        """
        Convert a list of Action objects to an AIF360 StandardDataset.
        
        We treat:
        - Features: complexity, random factors
        - Protected Attribute: 'complexity_group' (e.g., High vs Low complexity)
        - Label: 'mistake' (1 if mistake made, 0 otherwise)
        """
        if not AIF360_AVAILABLE:
            raise ImportError("aif360 is required for this functionality")

        data = []
        for a in actions:
            # Synthetic feature generation for demo purposes
            # grouped into Low (<= 50) and High (> 50) complexity
            complexity_group = 1.0 if a.complexity > 50 else 0.0
            
            row = {
                'complexity': a.complexity,
                'complexity_group': complexity_group,
                'mistake': 1.0 if a.mistake_flag else 0.0
            }
            data.append(row)
            
        df = pd.DataFrame(data)
        
        # Define AIF360 dataset
        ds = StandardDataset(
            df,
            label_name='mistake',
            favorable_classes=[0.0], # 0 (no mistake) is favorable
            protected_attribute_names=[protected_attribute],
            privileged_classes=[[0.0]], # Low complexity is usually "privileged" (easier)
        )
        return ds

    def calculate_metrics(self, actions: List[Any]) -> Dict[str, float]:
        """
        Calculate basic fairness metrics on the simulation actions.
        """
        if not AIF360_AVAILABLE:
            return {"error": "aif360 not installed"}

        ds = self.to_dataset(actions)
        
        metric = BinaryLabelDatasetMetric(
            ds, 
            unprivileged_groups=[{'complexity_group': 1.0}], 
            privileged_groups=[{'complexity_group': 0.0}]
        )
        
        return {
            "mean_difference": metric.mean_difference(),
            "disparate_impact": metric.disparate_impact()
        }
