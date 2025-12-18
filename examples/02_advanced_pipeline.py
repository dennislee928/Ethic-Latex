"""
Example 02: Advanced Pipeline (Fairness & Robustness)
=====================================================

Demonstrates how to run a comprehensive analysis including AI Fairness 360 
checks and Adversarial Robustness Toolbox checks.
"""

from erh.tools.pipeline import CombinedPipeline
import json

def main():
    # Initialize pipeline
    pipeline = CombinedPipeline(seed=123)
    
    print("Running combined pipeline...")
    results = pipeline.run(num_actions=1000)
    
    print("\nResults Summary:")
    print(json.dumps(results, indent=2))
    
    # Interpretation
    fairness = results['fairness']
    if 'mean_difference' in fairness:
        print(f"\nFairness - Mean Difference: {fairness['mean_difference']:.4f}")
        
    robustness = results['robustness']
    if 'mock_robustness_score' in robustness:
        print(f"Robustness Score: {robustness['mock_robustness_score']}")

if __name__ == "__main__":
    main()
