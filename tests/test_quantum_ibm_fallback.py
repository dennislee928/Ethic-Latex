import types


def test_advanced_quantum_engine_falls_back_when_ibm_service_discovery_fails(monkeypatch):
    from simulation.quantum import simulator

    class FakeAerSimulator:
        pass

    class FakeRuntimeService:
        def __init__(self, **kwargs):
            raise ValueError("No matching instances found for the following filters: .")

    fake_runtime = types.SimpleNamespace(QiskitRuntimeService=FakeRuntimeService)

    monkeypatch.setattr(simulator, "_QISKIT_AVAILABLE", True)
    monkeypatch.setattr(simulator, "AerSimulator", FakeAerSimulator, raising=False)
    monkeypatch.setitem(__import__("sys").modules, "qiskit_ibm_runtime", fake_runtime)
    monkeypatch.setenv("IBM_QUANTUM_TOKEN", "token")

    engine = simulator.AdvancedEthicalQuantumEngine(
        num_agents=2,
        use_real_hardware=True,
        backend_name="ibm_fez",
    )

    assert engine._service is None
    assert engine.use_real_hardware is False
