"""
Redis-based quantum judgment batch processor.

Consumes difficulty values from a Redis queue, runs LocalQuantumJudge (or
CloudQuantumJudge when IBM_QUANTUM_TOKEN is set), and pushes results back.
When REDIS_URL is not set, runs in standalone mode: process a fixed number
of batches and exit (for local/dev testing).
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

# Project root on path for simulation imports
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.quantum import LocalQuantumJudge

try:
    from simulation.quantum.cloud import CloudQuantumJudge
    _CLOUD_AVAILABLE = True
except (ImportError, ValueError):
    _CLOUD_AVAILABLE = False
    CloudQuantumJudge = None

_redis_client = None


def get_redis():
    """Lazy Redis connection (optional)."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    redis_url = os.environ.get("REDIS_URL", "").strip()
    if not redis_url:
        return None
    try:
        import redis
    except ImportError:
        return None
    try:
        _redis_client = redis.from_url(redis_url, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except Exception:
        return None


def get_judge(use_cloud: bool = False):
    """Return LocalQuantumJudge or CloudQuantumJudge when token is set."""
    if use_cloud and _CLOUD_AVAILABLE and CloudQuantumJudge is not None and os.environ.get("IBM_QUANTUM_TOKEN"):
        return CloudQuantumJudge()
    return LocalQuantumJudge(shots=256, seed=42)


def process_batch(judge, difficulties: list[float]) -> list[float]:
    """Run quantum judgment for each difficulty; return list of judgments."""
    if hasattr(judge, "batch_judge"):
        return judge.batch_judge(difficulties)
    return [judge.judge_action(difficulty=d) for d in difficulties]


def run_standalone(batch_size: int, num_batches: int) -> None:
    """Run without Redis: generate synthetic difficulties and process."""
    judge = get_judge(use_cloud=False)
    import random
    for b in range(num_batches):
        difficulties = [random.random() for _ in range(batch_size)]
        results = process_batch(judge, difficulties)
        print(f"[worker] batch {b + 1}/{num_batches} processed, sample J={results[0]:.4f}")
        time.sleep(0.1)


def run_with_redis(redis_url: str, queue_in: str, queue_out: str, batch_size: int) -> None:
    """Consume from queue_in, push results to queue_out."""
    r = get_redis()
    if r is None:
        print("[worker] Redis not available; running standalone batch and exiting.")
        run_standalone(batch_size, 1)
        return
    judge = get_judge(use_cloud=bool(os.environ.get("IBM_QUANTUM_TOKEN")))
    running = True

    def shutdown(_, __):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while running:
        difficulties = []
        for _ in range(batch_size):
            raw = r.lpop(queue_in)
            if raw is None:
                break
            try:
                obj = json.loads(raw)
                d = float(obj.get("difficulty", obj) if isinstance(obj, dict) else obj)
                difficulties.append(d)
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
        if not difficulties:
            time.sleep(1)
            continue
        results = process_batch(judge, difficulties)
        for d, j in zip(difficulties, results):
            r.rpush(queue_out, json.dumps({"difficulty": d, "judgment": j}))
        print(f"[worker] processed {len(difficulties)} jobs")


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum judgment batch worker")
    parser.add_argument("--redis-url", default=os.environ.get("REDIS_URL", ""), help="Redis URL")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size")
    parser.add_argument("--queue-in", default="erh:quantum:in", help="Input queue name")
    parser.add_argument("--queue-out", default="erh:quantum:out", help="Output queue name")
    parser.add_argument("--standalone-batches", type=int, default=5, help="Batches when no Redis")
    args = parser.parse_args()

    if args.redis_url:
        run_with_redis(args.redis_url, args.queue_in, args.queue_out, args.batch_size)
    else:
        run_standalone(args.batch_size, args.standalone_batches)


if __name__ == "__main__":
    main()
