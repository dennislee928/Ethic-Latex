from typing import List, Optional, Dict, Any
import requests
from erh.core.action_space import generate_world
from erh.core.judgement_system import BiasedJudge, evaluate_judgement
from erh.core.ethical_primes import select_ethical_primes, compute_Pi_and_error, analyze_error_growth

class ERHLocalClient:
    """
    Local client for running simulations directly in Python.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed

    def run_simulation(self, 
                       num_actions: int = 1000, 
                       complexity_dist: str = 'zipf') -> Dict[str, Any]:
        """
        Run a full simulation pipeline and return analysis results.
        """
        # 1. Generate
        actions = generate_world(
            num_actions=num_actions,
            complexity_dist=complexity_dist,
            random_seed=self.seed
        )
        
        # 2. Judge (Default biased judge for now)
        judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)
        evaluate_judgement(actions, judge, tau=0.3)
        
        # 3. Analyze
        primes = select_ethical_primes(actions, importance_quantile=0.9)
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
        analysis = analyze_error_growth(E_x, x_vals)
        
        return {
            "num_actions": num_actions,
            "mistake_rate": sum(a.mistake_flag for a in actions) / len(actions),
            "analysis": analysis,
            "raw_data": {
                "x_vals": x_vals.tolist(),
                "E_x": E_x.tolist()
            }
        }

class ERHRemoteClient:
    """
    Remote client for interacting with a running ERH API instance.
    """
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def health(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/health")
            return resp.status_code == 200
        except:
            return False

    def run_simulation(self, num_actions: int = 1000, complexity_dist: str = 'zipf') -> Dict[str, Any]:
        payload = {
            "num_actions": num_actions,
            "complexity_dist": complexity_dist
        }
        resp = requests.post(f"{self.base_url}/simulate", json=payload)
        resp.raise_for_status()
        return resp.json()
