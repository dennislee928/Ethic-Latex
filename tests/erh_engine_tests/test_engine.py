"""Phase 0 tests: contract correctness + REST/gRPC parity for the ERH engine."""

from __future__ import annotations

import random

import pytest

from erh_engine import EvaluateParams, EvaluateRequest, Sample, evaluate


def _make_samples(n: int = 300, biased: bool = True, seed: int = 0):
    rng = random.Random(seed)
    samples = []
    for i in range(n):
        c = rng.randint(1, 100)
        v = 1.0
        if biased:
            # Systematic over-approval that worsens with complexity (unhealthy).
            j = -1.0 if (c > 50 and rng.random() < 0.6) else 1.0
        else:
            # Rare, complexity-independent noise (healthy).
            j = -1.0 if rng.random() < 0.02 else 1.0
        samples.append(Sample(id=f"s{i}", complexity=c, value=v, judgment=j, weight=rng.uniform(1, 30)))
    return samples


def test_empty_request_is_healthy():
    resp = evaluate(EvaluateRequest(samples=[]))
    assert resp.erh_satisfied is True
    assert resp.num_samples == 0
    assert resp.risk_score == 0.0


def test_biased_system_flags_primes_and_risk():
    resp = evaluate(EvaluateRequest(samples=_make_samples(biased=True)))
    assert resp.num_primes > 0
    assert resp.risk_score >= 0.0
    assert resp.num_samples == 300


def test_response_floats_are_json_safe():
    # Flat error profiles previously produced NaN; ensure all floats are finite.
    import math

    resp = evaluate(EvaluateRequest(samples=_make_samples(biased=False)))
    for field in ("risk_score", "violation_rate", "max_ratio", "bound_value",
                  "estimated_exponent", "r_squared"):
        assert math.isfinite(getattr(resp, field)), field


def test_curves_returned_when_requested():
    resp = evaluate(
        EvaluateRequest(samples=_make_samples(), params=EvaluateParams(include_curves=True))
    )
    assert resp.error_curve is not None
    assert len(resp.error_curve.x) == len(resp.error_curve.y) > 0


def test_rest_matches_direct_engine():
    from fastapi.testclient import TestClient
    from erh_engine.rest.main import app

    client = TestClient(app)
    req = EvaluateRequest(samples=_make_samples())
    direct = evaluate(req)
    rest = client.post("/v1/evaluate", json=req.model_dump()).json()
    assert rest["erh_satisfied"] == direct.erh_satisfied
    assert rest["num_primes"] == direct.num_primes
    assert rest["risk_score"] == pytest.approx(direct.risk_score)


def test_grpc_matches_rest():
    import grpc
    from erh_engine.grpc import erh_engine_pb2 as pb
    from erh_engine.grpc import erh_engine_pb2_grpc as pb_grpc
    from erh_engine.grpc.server import ERHEngineServicer
    from concurrent import futures

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    pb_grpc.add_ERHEngineServicer_to_server(ERHEngineServicer(), server)
    port = server.add_insecure_port("[::]:0")
    server.start()
    try:
        samples = _make_samples()
        pb_samples = [
            pb.Sample(id=s.id, complexity=s.complexity, value=s.value,
                      judgment=s.judgment, weight=s.weight)
            for s in samples
        ]
        req = pb.EvaluateRequest(samples=pb_samples, params=pb.EvaluateParams(), judge_name="t")
        with grpc.insecure_channel(f"localhost:{port}") as channel:
            stub = pb_grpc.ERHEngineStub(channel)
            grpc_resp = stub.Evaluate(req)

        direct = evaluate(EvaluateRequest(samples=samples, judge_name="t"))
        assert grpc_resp.erh_satisfied == direct.erh_satisfied
        assert grpc_resp.num_primes == direct.num_primes
        assert grpc_resp.risk_score == pytest.approx(direct.risk_score, rel=1e-6)
    finally:
        server.stop(0)


def test_adapter_smoke():
    from erh_engine.adapters.llm import LLMExchange, exchanges_to_samples
    from erh_engine.adapters.iam_cspm import IAMGrant, grants_to_samples
    from erh_engine.adapters.ueba import UEBARequest, UEBAEvent, events_to_samples

    llm = exchanges_to_samples(
        [LLMExchange(prompt="hi", response="hello", harmful_intent=False)], use_oracle=False
    )
    assert len(llm) == 1

    iam = grants_to_samples([IAMGrant(principal="p", actions=["*"], resources=["*"])])
    assert iam[0].context["mitre_iob"]

    ueba = events_to_samples(
        UEBARequest(events=[
            UEBAEvent(user="a", hour=10, bytes_downloaded=10, is_baseline=True),
            UEBAEvent(user="a", hour=2, bytes_downloaded=5000, sensitive=True),
        ])
    )
    assert len(ueba) == 1
