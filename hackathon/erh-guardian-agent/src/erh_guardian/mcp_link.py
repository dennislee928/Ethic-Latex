"""Connect the guardian to the erh-guardian-mcp Cloudflare Worker.

The worker persists value-alignment profiles and the gate-decision audit log
in D1; its tools are exposed over streamable HTTP MCP. Set
``ERH_GUARDIAN_MCP_URL`` (e.g. ``https://erh-guardian-mcp.<acct>.workers.dev/mcp``)
to enable it — without it the guardian runs fully offline.
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

    return MCPClient(lambda: streamablehttp_client(url))
