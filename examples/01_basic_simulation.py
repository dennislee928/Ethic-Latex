"""
Example 01: Basic Simulation
============================

Demonstrates how to run a simple simulation using the ERH Python SDK.
"""

from erh.client import ERHLocalClient

def main():
    # Initialize the local client
    client = ERHLocalClient(seed=42)
    
    print("Running simulation (N=500)...")
    result = client.run_simulation(
        num_actions=500, 
        complexity_dist='zipf'
    )
    
    # Analyze results
    analysis = result['analysis']
    print(f"\nSimulation Complete:")
    print(f"  Mistake Rate: {result['mistake_rate']:.2%}")
    print(f"  Alpha (Exponent): {analysis.get('estimated_exponent', 'N/A')}")
    print(f"  ERH Satisfied: {analysis.get('erh_satisfied', False)}")
    
if __name__ == "__main__":
    main()
