"""
gRPC server for the ERH engine — the low-latency path for the K8s sidecar and
the Go/Gin edge proxy. Delegates to the same :func:`erh_engine.engine.evaluate`
as REST, so results are identical across transports.

Run:  python -m erh_engine.grpc.server   (listens on :50051 by default)
"""

from __future__ import annotations

import os
from concurrent import futures

import grpc

from .. import __version__
from ..engine import evaluate as run_evaluate
from . import erh_engine_pb2 as pb
from . import erh_engine_pb2_grpc as pb_grpc
from .translate import request_from_pb, response_to_pb


class ERHEngineServicer(pb_grpc.ERHEngineServicer):
    def Evaluate(self, request, context):  # noqa: N802 (gRPC naming)
        req = request_from_pb(request)
        resp = run_evaluate(req)
        return response_to_pb(resp)

    def Health(self, request, context):  # noqa: N802
        return pb.HealthResponse(status="ok", service="erh_engine", version=__version__)


def serve(port: int | None = None, max_workers: int = 8) -> None:
    port = port or int(os.environ.get("ERH_GRPC_PORT", "50051"))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    pb_grpc.add_ERHEngineServicer_to_server(ERHEngineServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"erh_engine gRPC listening on :{port}")
    server.wait_for_termination()


if __name__ == "__main__":  # pragma: no cover
    serve()
