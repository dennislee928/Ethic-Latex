"""
Tests for features added in update.plan.md (Phase 1–3).

Covers:
- AdvancedEthicalCircuit (VQE-style quantum circuit)
- calculate_evs (Ethical Viability Score)
- run_simulation_batch parallel execution
- generate_comprehensive_report EVS integration
"""

import json
import os
import tempfile

import pytest


class TestAdvancedEthicalCircuit:
    """Tests for AdvancedEthicalCircuit in simulation/quantum/simulator.py."""

    def test_advanced_ethical_circuit_import(self):
        """AdvancedEthicalCircuit can be imported from simulation.quantum."""
        from simulation.quantum import AdvancedEthicalCircuit

        assert AdvancedEthicalCircuit is not None

    def test_advanced_ethical_circuit_run_social_simulation(self):
        """run_social_simulation returns stability_index and raw_distribution."""
        from simulation.quantum import AdvancedEthicalCircuit

        circuit = AdvancedEthicalCircuit(n_qubits=3, entanglement="linear", seed=42)
        result = circuit.run_social_simulation()
        assert "stability_index" in result
        assert "raw_distribution" in result
        assert 0 <= result["stability_index"] <= 1
        assert isinstance(result["raw_distribution"], dict)

    def test_advanced_ethical_circuit_entanglement_options(self):
        """Supports linear, full, circular entanglement."""
        from simulation.quantum import AdvancedEthicalCircuit

        for ent in ("linear", "full", "circular"):
            circuit = AdvancedEthicalCircuit(n_qubits=2, entanglement=ent, seed=0)
            r = circuit.run_social_simulation()
            assert r["stability_index"] >= 0


class TestCalculateEvs:
    """Tests for calculate_evs in erh_core.analysis.statistics."""

    def test_calculate_evs_import(self):
        """calculate_evs can be imported."""
        from erh_core.analysis.statistics import calculate_evs

        assert callable(calculate_evs)

    def test_calculate_evs_range(self):
        """EVS is in [0, 1]."""
        from erh_core.analysis.statistics import calculate_evs

        assert 0 <= calculate_evs(0.5, 0.5, 0) <= 1
        assert 0 <= calculate_evs(1.0, 1.0, 0) <= 1
        assert 0 <= calculate_evs(0.8, 0.6, 0.2) <= 1

    def test_calculate_evs_zero_stability_fairness(self):
        """Returns 0 when stability + fairness == 0."""
        from erh_core.analysis.statistics import calculate_evs

        assert calculate_evs(0, 0, 0) == 0.0

    def test_calculate_evs_harmonic_mean_formula(self):
        """EVS = F1 * (1 - polarization) where F1 is harmonic mean."""
        from erh_core.analysis.statistics import calculate_evs

        # stability=1, fairness=1, polarization=0 -> F1=1, EVS=1
        assert abs(calculate_evs(1.0, 1.0, 0) - 1.0) < 1e-6
        # polarization=1 -> EVS=0
        assert calculate_evs(1.0, 1.0, 1.0) == 0.0


class TestRunSimulationBatch:
    """Tests for run_simulation_batch parallel execution."""

    def test_batch_creates_distinct_files(self):
        """Parallel runs produce distinct JSON files (no overwrite)."""
        from scripts.run_simulation_batch import _run_single_config

        with tempfile.TemporaryDirectory() as tmp:
            configs = [
                {"id": 0, "num_actions": 50, "complexity_dist": "zipf", "seed": 1},
                {"id": 1, "num_actions": 50, "complexity_dist": "zipf", "seed": 2},
            ]
            for cfg in configs:
                _run_single_config(cfg, tmp)
            files = [f for f in os.listdir(tmp) if f.endswith(".json")]
            assert len(files) >= 2, f"Expected ≥2 files, got {files}"

    def test_single_run_backward_compatible(self):
        """Single run without --instances works."""
        import subprocess
        import sys

        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                [os.getcwd(), os.path.join(os.getcwd(), "erh_core")]
            )
            r = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_simulation_batch.py",
                    "--num-actions",
                    "50",
                    "--output-dir",
                    tmp,
                ],
                cwd=os.path.dirname(os.path.dirname(__file__)),
                env=env,
                capture_output=True,
                text=True,
            )
            assert r.returncode == 0, r.stderr
            assert any(f.endswith(".json") for f in os.listdir(tmp))


class TestGenerateComprehensiveReportEvs:
    """Tests for generate_comprehensive_report EVS integration."""

    def test_report_computes_evs(self):
        """Report adds EVS column when loading results."""
        from scripts.generate_comprehensive_report import load_results, _add_evs_columns

        with tempfile.TemporaryDirectory() as tmp:
            # Create minimal sim_result JSON
            data = {
                "timestamp": "2025-02-08T10:00:00",
                "config": {"complexity_dist": "zipf", "num_actions": 100},
                "metrics": {
                    "mistake_rate": 0.2,
                    "ethical_primes_count": 80,
                    "erh_satisfied": True,
                    "estimated_exponent": 0.48,
                },
            }
            with open(os.path.join(tmp, "sim_result_zipf_N100_test.json"), "w") as f:
                json.dump(data, f)
            df = load_results(tmp)
            assert not df.empty
            assert "evs" in df.columns
            assert (df["evs"] >= 0).all() and (df["evs"] <= 1).all()

    def test_generate_report_produces_evs_plot(self):
        """Report generates evs_over_time.png when EVS data exists."""
        from scripts.generate_comprehensive_report import (
            load_results,
            generate_visualizations,
        )

        with tempfile.TemporaryDirectory() as tmp:
            for i in range(2):
                data = {
                    "timestamp": f"2025-02-08T10:00:0{i}",
                    "config": {"complexity_dist": "zipf", "num_actions": 100},
                    "metrics": {
                        "mistake_rate": 0.2,
                        "ethical_primes_count": 80,
                        "erh_satisfied": True,
                        "estimated_exponent": 0.48,
                    },
                }
                with open(
                    os.path.join(tmp, f"sim_result_zipf_N100_{i}.json"), "w"
                ) as f:
                    json.dump(data, f)
            df = load_results(tmp)
            out = os.path.join(tmp, "report_out")
            generate_visualizations(df, out)
            assert os.path.isfile(os.path.join(out, "evs_over_time.png"))
