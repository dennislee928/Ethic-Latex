"""
Cloud Quantum Judge using IBM Quantum Runtime.

Uses the Qiskit Runtime REST API (see https://quantum.cloud.ibm.com/docs/en/api/qiskit-runtime-rest).
Implements batching for 100+ agents.

Environment variables:
- IBM_QUANTUM_TOKEN (required): IBM Cloud API key from the Dashboard. The REST API uses it to
  obtain an IAM bearer token for each request. Create at https://quantum.cloud.ibm.com/
  (Dashboard → Create API key). Must be the 44-character API key; legacy quantum.ibm.com
  tokens are no longer supported.
- IBM_QUANTUM_INSTANCE (recommended): Instance Cloud Resource Name (CRN). Many REST API calls
  require the Service-CRN header; see Instances page on the platform for your CRN.
- IBM_QUANTUM_REGION (optional): "us-east" (default) or "eu-de" for EU region endpoints.
"""

import os
from typing import List, Tuple

try:
    from qiskit_ibm_runtime import QiskitRuntimeService, Session, SamplerV2 as Sampler
    from qiskit import QuantumCircuit
    import numpy as np

    _IBM_RUNTIME_AVAILABLE = True
except ImportError:
    _IBM_RUNTIME_AVAILABLE = False
    np = None

from .interface import QuantumOracle


def _get_ibm_token() -> str | None:
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        # Load .env from repo root (simulation/quantum/cloud.py -> parent.parent.parent)
        try:
            from pathlib import Path

            _this_file = Path(__file__).resolve()
            _repo_root = _this_file.parent.parent.parent
            _env_file = _repo_root / ".env"
            if _env_file.exists():
                try:
                    from dotenv import load_dotenv

                    load_dotenv(_env_file)
                    token = os.environ.get("IBM_QUANTUM_TOKEN")
                except ImportError:
                    for line in _env_file.read_text().splitlines():
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, _, v = line.partition("=")
                            if k.strip() == "IBM_QUANTUM_TOKEN":
                                token = v.strip().strip('"').strip("'")
                                break
        except Exception:
            pass
    return token


class CloudQuantumJudge(QuantumOracle):
    """
    Cloud-based quantum judge using IBM Quantum hardware/simulators.

    Batches multiple circuits into a single job to reduce queue latency.
    Requires IBM_QUANTUM_TOKEN in environment.
    """

    def __init__(
        self,
        backend_name: str = "ibmq_qasm_simulator",
        batch_size: int = 100,
    ):
        if not _IBM_RUNTIME_AVAILABLE:
            raise ImportError(
                "qiskit-ibm-runtime required for CloudQuantumJudge. "
                "Install with: pip install qiskit-ibm-runtime"
            )
        token = _get_ibm_token()
        if not token:
            raise ValueError(
                "IBM_QUANTUM_TOKEN not set. Create an API key at https://quantum.cloud.ibm.com/ (Dashboard → Create API key)."
            )
        instance = os.environ.get("IBM_QUANTUM_INSTANCE")
        region = os.environ.get("IBM_QUANTUM_REGION")
        service_kw: dict = {"channel": "ibm_quantum_platform", "token": token}
        if instance:
            service_kw["instance"] = instance
        if region:
            service_kw["region"] = region
        self._service = QiskitRuntimeService(**service_kw)
        self._backend_name = backend_name
        self.batch_size = batch_size

    def _get_backend(self):
        """Resolve backend by name, or pick first available simulator if name not found."""
        try:
            return self._service.backend(name=self._backend_name)
        except Exception:
            backends = self._service.backends(simulator=True, operational=True)
            if not backends:
                raise RuntimeError(
                    "No simulator backend available. Check instance/plan at https://quantum.cloud.ibm.com/"
                )
            return backends[0]

    def collapse_wavefunction(
        self,
        complexity_amplitudes: Tuple[float, ...],
    ) -> Tuple[float, float]:
        difficulty = float(np.mean(complexity_amplitudes)) if complexity_amplitudes else 0.5
        difficulty = max(0.0, min(1.0, difficulty))
        theta = difficulty * np.pi
        alpha_sq = float(np.cos(theta / 2) ** 2)
        return (alpha_sq, 1.0 - alpha_sq)

    def entangled_judgment(
        self,
        agent_a_bias: float,
        agent_b_bias: float,
    ) -> Tuple[float, float]:
        theta_a = np.clip(agent_a_bias, -1, 1) * np.pi / 2
        theta_b = np.clip(agent_b_bias, -1, 1) * np.pi / 2
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.rx(theta_a, 0)
        qc.rx(theta_b, 1)
        qc.measure([0, 1], [0, 1])

        backend = self._get_backend()
        with Session(backend=backend) as session:
            sampler = Sampler(mode=session)
            pub = (qc,)
            result = sampler.run([pub]).result()
            quasi = result[0].data.meas.get_counts()

        total = sum(quasi.values())
        J_a = J_b = 0.0
        for outcome, count in quasi.items():
            a_val = 1 if outcome[0] == "0" else -1
            b_val = 1 if outcome[1] == "0" else -1
            p = count / total
            J_a += a_val * p
            J_b += b_val * p
        return (float(J_a), float(J_b))

    def batch_judge(self, difficulties: List[float]) -> List[float]:
        """
        Batch evaluate judgments for many agents in a single job.

        Parameters
        ----------
        difficulties : list of float
            Normalized difficulties ∈ [0, 1]

        Returns
        -------
        list of float
            Judgment values J ∈ [-1, 1]
        """
        circuits = []
        for d in difficulties:
            theta = max(0.0, min(1.0, d)) * np.pi
            qc = QuantumCircuit(1, 1)
            qc.rx(theta, 0)
            qc.measure(0, 0)
            circuits.append(qc)

        backend = self._get_backend()
        with Session(backend=backend) as session:
            sampler = Sampler(mode=session)
            pubs = [(qc,) for qc in circuits[: self.batch_size]]
            result = sampler.run(pubs).result()

        judgments = []
        for i, pub_result in enumerate(result):
            quasi = pub_result.data.meas.get_counts()
            total = sum(quasi.values())
            J = 0.0
            for outcome, count in quasi.items():
                val = 1 if outcome[0] == "0" else -1
                J += val * (count / total)
            judgments.append(float(J))

        if len(difficulties) > self.batch_size:
            remaining = self.batch_judge(difficulties[self.batch_size :])
            judgments.extend(remaining)
        return judgments
