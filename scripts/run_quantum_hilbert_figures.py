#!/usr/bin/env python3
"""
Run Quantum Hilbert Space simulation and generate figures for thesis PDF.

Produces:
  - simulation/output/figures/latest_quantum_circuit.png
  - simulation/output/figures/latest_quantum_distribution.png
  - simulation/output/quantum_hilbert_results.json (consensus_state, system_coherence, von_neumann_entropy)

Used by build_thesis.yml to ensure quantum figures and stats are available for the PDF.
"""

import json
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault("PYTHONPATH", str(project_root) + os.pathsep + os.environ.get("PYTHONPATH", ""))


def main():
    fig_dir = project_root / "simulation" / "output" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    output_json = project_root / "simulation" / "output" / "quantum_hilbert_results.json"

    try:
        from erh_core.core.hybrid_model import HybridPsychohistoryModel

        model = HybridPsychohistoryModel(
            num_agents=20,
            enable_temporal=False,
            enable_network_dynamics=False,
            enable_fluid_model=False,
            enable_meta_monitor=False,
            enable_quantum=True,
            quantum_agents_subsample=8,
        )
        results = model.run_simulation(
            num_time_steps=1,
            actions_per_step=200,
            network_dynamics_model="degroot",
        )
        qs = results.get("quantum_stability")
        if qs and isinstance(qs, dict) and "error" not in qs:
            payload = {
                "consensus_state": qs.get("consensus_state", "N/A"),
                "system_coherence": qs.get("system_coherence", 0.0),
                "von_neumann_entropy": qs.get("von_neumann_entropy"),
                "circuit_image": str(qs.get("circuit_image", "")),
                "dist_image": str(qs.get("dist_image", "")),
            }
            with open(output_json, "w") as f:
                json.dump(payload, f, indent=2)
            print(f"Quantum Hilbert results saved to {output_json}")
            print(f"  consensus_state: {payload['consensus_state']}")
            print(f"  system_coherence: {payload['system_coherence']:.4f}")
            if payload.get("von_neumann_entropy") is not None:
                print(f"  von_neumann_entropy: {payload['von_neumann_entropy']:.4f}")
        else:
            err = qs.get("error", "unknown") if qs else "no quantum_stability"
            print(f"Quantum step failed: {err}")
            with open(output_json, "w") as f:
                json.dump({"error": str(err)}, f)
    except ImportError as e:
        print(f"Import error (qiskit may be missing): {e}")
        with open(output_json, "w") as f:
            json.dump({"error": f"ImportError: {e}"}, f)
    except Exception as e:
        print(f"Error: {e}")
        with open(output_json, "w") as f:
            json.dump({"error": str(e)}, f)
        raise


if __name__ == "__main__":
    main()
