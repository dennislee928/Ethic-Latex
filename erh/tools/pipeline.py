from typing import Dict, Any, List
from erh.core.action_space import generate_world, Action
from erh.core.judgement_system import BiasedJudge, evaluate_judgement
from erh.tools.art_adapter import ARTAdapter
from erh.tools.aif360_adapter import AIF360Adapter

class CombinedPipeline:
    """
    Orchestrates a comprehensive analysis pipeline:
    1. Simulation (generate actions + judge)
    2. Fairness Check (AIF360)
    3. Robustness Check (ART)
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.art = ARTAdapter()
        self.aif = AIF360Adapter()

    def run(self, num_actions: int = 1000) -> Dict[str, Any]:
        print(f"Running pipeline with N={num_actions}")
        
        # 1. Simulation
        print("[1/3] Running Simulation...")
        actions = generate_world(
            num_actions=num_actions,
            complexity_dist='zipf',
            random_seed=self.seed
        )
        judge = BiasedJudge()
        evaluate_judgement(actions, judge)
        
        # 2. Fairness
        print("[2/3] Checking Fairness (AIF360)...")
        fairness_metrics = self.aif.calculate_metrics(actions)
        
        # 3. Robustness
        print("[3/3] Checking Robustness (ART)...")
        robustness_metrics = self.art.check_robustness(actions)
        
        return {
            "simulation": {
                "num_actions": num_actions,
                "mistakes": sum(a.mistake_flag for a in actions)
            },
            "fairness": fairness_metrics,
            "robustness": robustness_metrics
        }

if __name__ == "__main__":
    pipeline = CombinedPipeline()
    results = pipeline.run(500)
    import json
    print(json.dumps(results, indent=2))
