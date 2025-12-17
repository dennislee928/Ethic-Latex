from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from simulation.api.schemas import HealthResponse, SimulationRequest, SimulationResponse
from simulation.core.action_space import generate_world
from simulation.core.judgement_system import BiasedJudge, evaluate_judgement
from simulation.core.ethical_primes import select_ethical_primes, compute_Pi_and_error, analyze_error_growth

app = FastAPI(
    title="Ethical Riemann Hypothesis API",
    description="API for the ERH simulation framework",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/simulate", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    try:
        # 1. Generate world
        actions = generate_world(
            num_actions=request.num_actions,
            complexity_dist=request.complexity_dist,
            random_seed=request.random_seed
        )
        
        # 2. Use a default judge (can be parameterized later)
        judge = BiasedJudge(bias_strength=0.2, noise_scale=0.1)
        evaluate_judgement(actions, judge, tau=0.3)
        
        # 3. Analyze
        primes = select_ethical_primes(actions, importance_quantile=0.9)
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
        analysis = analyze_error_growth(E_x, x_vals)
        
        mistakes = sum(1 for a in actions if a.mistake_flag)
        
        return {
            "message": "Simulation calculation complete",
            "num_actions": len(actions),
            "mistakes": mistakes,
            "primes": len(primes),
            "erh_satisfied": analysis.get("erh_satisfied", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
