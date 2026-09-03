"""Connect the guardian to the erh-guardian-mcp Cloudflare Worker.

The worker persists value-alignment profiles and the gate-decision audit log
in D1; its tools are exposed over streamable HTTP MCP. Set
``ERH_GUARDIAN_MCP_URL`` (e.g. ``https://erh-guardian-mcp.<acct>.workers.dev/mcp``)
to enable it — without it the guardian runs fully offline. If the worker was
deployed with an ``MCP_AUTH_TOKEN`` secret, set ``ERH_GUARDIAN_MCP_TOKEN`` to
the same value so requests carry the bearer token.
"""

from __future__ import annotations

import os
from typing import Optional

from strands.tools.mcp import MCPClient


def mcp_client_from_env(url: Optional[str] = None) -> Optional[MCPClient]:
    """Build an MCPClient for the guardian worker, or None when unconfigured."""
    url = url or os.environ.get("ERH_GUARDIAN_MCP_URL")
    if not url:
        return None
    from mcp.client.streamable_http import streamablehttp_client

    token = os.environ.get("ERH_GUARDIAN_MCP_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else None
    return MCPClient(lambda: streamablehttp_client(url, headers=headers))
