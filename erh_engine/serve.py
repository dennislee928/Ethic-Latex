"""
Unified entrypoint: run the REST server, the gRPC server, or both.

    ERH_MODE=rest   python -m erh_engine.serve   # REST only
    ERH_MODE=grpc   python -m erh_engine.serve   # gRPC only
    ERH_MODE=both   python -m erh_engine.serve   # both (default)
"""

from __future__ import annotations

import os
import threading


def _run_rest() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("erh_engine.rest.main:app", host="0.0.0.0", port=port)


def _run_grpc() -> None:
    from .grpc.server import serve

    serve()


def main() -> None:
    mode = os.environ.get("ERH_MODE", "both").lower()
    if mode == "rest":
        _run_rest()
    elif mode == "grpc":
        _run_grpc()
    else:
        # Run gRPC in a daemon thread, REST in the foreground.
        threading.Thread(target=_run_grpc, daemon=True).start()
        _run_rest()


if __name__ == "__main__":
    main()
