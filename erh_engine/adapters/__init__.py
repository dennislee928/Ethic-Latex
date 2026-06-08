"""
Domain adapters: convert raw domain data (LLM exchanges, IAM policies, UEBA
events) into the generic :class:`~erh_engine.contracts.schemas.Sample` contract,
then call :func:`erh_engine.engine.evaluate`.

Each adapter ships a live-integration path *and* a deterministic fallback so the
service runs in CI without external credentials.
"""
