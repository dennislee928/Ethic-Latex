from pydantic import BaseModel
from typing import Optional, Any

class HealthResponse(BaseModel):
    status: str
    version: str

class SimulationRequest(BaseModel):
    num_actions: int = 1000
    complexity_dist: str = "zipf"
    random_seed: Optional[int] = None

class SimulationResponse(BaseModel):
    message: str
    num_actions: int
    mistakes: int
    primes: int
    erh_satisfied: bool
