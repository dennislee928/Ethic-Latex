# Ethical Riemann Hypothesis (ERH) SDK

A Python SDK for simulating and analyzing ethical decision-making systems using the mathematical framework of the Riemann Hypothesis.

## Installation

```bash
pip install erh
```

## Code Structure

The `erh/` package is a Python SDK that re-exports core functionality from the shared 
`erh_core/` module. This ensures consistency with the `simulation/` research framework 
while providing a clean SDK interface for distribution.

**Note**: The actual implementation lives in `erh_core/` to follow DRY principles and 
avoid code duplication between `simulation/` and `erh/` packages. Both `simulation/` and 
`erh/` maintain backward compatibility by re-exporting from `erh_core/`.

## Usage

### Local Simulation
Run simulations directly in your Python environment:

```python
from erh.client import ERHLocalClient

# Initialize client
client = ERHLocalClient(seed=42)

# Run simulation
result = client.run_simulation(num_actions=1000, complexity_dist='zipf')

print(f"Mistake Rate: {result['mistake_rate']:.2%}")
print(f"ERH Satisfied: {result['analysis']['erh_satisfied']}")
```

### Remote API
Interact with a running ERH API server:

```python
from erh.client import ERHRemoteClient

client = ERHRemoteClient(base_url="http://localhost:8000")

if client.health():
    result = client.run_simulation(num_actions=1000)
    print(result)
```

## Modules

- `erh.core`: Core simulation primitives (Action Space, Judges).
- `erh.analysis`: Statistical analysis tools (Zeta function, Error metrics).
- `erh.client`: User-friendly wrappers.
