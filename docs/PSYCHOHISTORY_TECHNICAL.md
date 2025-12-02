# Psychohistory Module Technical Documentation

This document provides technical details about the psychohistory-inspired integration with the ERH framework.

## Model Abstraction Level

The psychohistory module operates at a **hybrid agent-based and network-based** abstraction level:

- **Agent-based component**: Individual agents (representing decision-makers or system components) with local judgment functions and error accumulation
- **Network-based component**: Social networks connecting agents, enabling information flow and error propagation
- **Macro-level aggregation**: Temporal ERH analysis (`E(x,t)`) that tracks error evolution over both complexity $x$ and time $t$

## Core Components

### 1. Agent-Based Model (`simulation/core/abm_simulator.py`)

- **Purpose**: Simulates individual agents making moral judgments over time
- **Key classes**: `Agent`, `ABMSimulator`
- **Output**: Agent-level error trajectories that aggregate to system-level $E(x,t)$

### 2. Social Network (`simulation/core/social_network.py`)

- **Purpose**: Models connections between agents (random, small-world, scale-free topologies)
- **Key classes**: `SocialNetwork`
- **Output**: Network structure affecting error propagation patterns

### 3. Hybrid Model (`simulation/core/hybrid_model.py`)

- **Purpose**: Integrates agent-based simulation with ERH-style analysis
- **Key classes**: `HybridModel`
- **Output**: Coupled $E(x,t)$ trajectories that respect ERH-style bounds

### 4. Temporal ERH Analysis (`simulation/analysis/temporal_analysis.py`)

- **Purpose**: Analyzes error growth over time and complexity
- **Key functions**: 
  - `compute_temporal_erh_satisfaction()`: Checks if $E(x,t)$ satisfies ERH bounds over time
  - `forecast_error_growth()`: Projects future error patterns
- **Output**: Temporal ERH satisfaction metrics, forecast trajectories

### 5. Meta-Monitor (`simulation/core/meta_monitor.py`)

- **Purpose**: Macro-level oversight structure (analogous to "Second Foundation")
- **Key classes**: `MetaMonitor`
- **Output**: System-level interventions when $E(x,t)$ approaches ERH-style bounds

## Integration Test Scripts

The following scripts generate integration test results referenced in Section 7.6:

### Main Test Script
- **`scripts/run_psychohistory_simulations.py`**: Main Python test runner
  - Parameter scanning (agent counts, network topologies, temporal horizons)
  - Long-term simulation tests (50-100 time steps)
  - Stress tests (200-500 agents)
  - Boundary case tests

### Shell Wrapper
- **`scripts/run_psychohistory_tests.sh`**: Shell script wrapper
  - Supports `--quick` mode for CI/CD
  - Full test mode for comprehensive validation

### Test Reports
- **`tests/PSYCHOHISTORY_TESTS_README.md`**: Overview of test structure
- **`simulation/output/psychohistory_tests/test_report.json`**: JSON format detailed report
- **`simulation/output/psychohistory_tests/test_summary.txt`**: Text format summary

## Metrics Written Back to ERH-Style Analysis

The psychohistory integration produces the following metrics that feed back into ERH-style analysis:

1. **Aggregate error growth exponent $\alpha(t)$**: Time-varying growth exponent computed from $E(x,t)$
   - Written to: `simulation/output/psychohistory_tests/alpha_trajectory.csv`
   - Used in: Section 7.6 discussion of temporal ERH satisfaction

2. **ERH satisfaction rate over time**: Fraction of time steps where $E(x,t)$ satisfies ERH-style bounds
   - Written to: `simulation/output/psychohistory_tests/erh_satisfaction_rate.txt`
   - Used in: Validation that psychohistory layer doesn't break sublinear error growth

3. **Crisis point detection**: Times $t^*$ where $E(x,t)$ exhibits sudden acceleration
   - Written to: `simulation/output/psychohistory_tests/crisis_points.json`
   - Used in: Section 7.6 discussion of "Seldon crises"

4. **Network topology effects**: Comparison of ERH metrics across different network structures
   - Written to: `simulation/output/psychohistory_tests/network_comparison.csv`
   - Used in: Sensitivity analysis of psychohistory integration

## Running Integration Tests

### Quick Mode (for CI/CD)
```bash
bash scripts/run_psychohistory_tests.sh --quick
```

### Full Mode (comprehensive testing)
```bash
bash scripts/run_psychohistory_tests.sh
```

### Python Direct
```bash
cd simulation
export PYTHONPATH=$PYTHONPATH:$(pwd)
python ../scripts/run_psychohistory_simulations.py --quick
```

## Key Findings Referenced in Paper

The integration tests (as summarized in Section 7.6) indicate:

- **Sublinear error growth preserved**: The aggregate error growth exponents remain well below the ERH-style worst-case target ($\alpha < 0.5$) even when coupling ERH-based analysis with the psychohistory-inspired macro layer
- **Network topology robustness**: Results are stable across different network structures (random, small-world, scale-free)
- **Temporal stability**: Error growth patterns remain bounded over extended time horizons (50-100 time steps)

## Limitations

As stated in Section 7.7, the current psychohistory-inspired simulations are:
- **Exploratory**: Not validated as a theory of social dynamics
- **Conceptual**: Used as a metaphorical and modelling device
- **Supplementary**: Reside mainly in supplementary code, not core paper results

## File Locations

- Core implementation: `simulation/core/abm_simulator.py`, `hybrid_model.py`, `social_network.py`, `meta_monitor.py`
- Analysis tools: `simulation/analysis/temporal_analysis.py`
- Test scripts: `scripts/run_psychohistory_simulations.py`, `scripts/run_psychohistory_tests.sh`
- Test documentation: `tests/PSYCHOHISTORY_TESTS_README.md`
- Output: `simulation/output/psychohistory_tests/`

