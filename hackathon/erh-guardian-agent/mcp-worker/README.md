# erh-guardian-mcp (Cloudflare Worker)

MCP server exposing ERH Guardian's persistence layer — value-alignment profiles and the
gate-decision audit log — on Cloudflare D1, callable by the Strands agent over
streamable HTTP (`/mcp`) or SSE (`/sse`).

## Setup & deploy

```bash
cd hackathon/erh-guardian-agent/mcp-worker
npm install

# create the D1 database, then paste its id into wrangler.jsonc
npx wrangler d1 create erh-guardian

# generate + apply migrations
npm run db:generate
npm run db:migrate:local     # local dev
npm run db:migrate           # remote

npm run dev                  # http://localhost:8787
npx wrangler deploy
curl https://erh-guardian-mcp.<account>.workers.dev/health
```

## Connecting from the Strands agent

```python
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient

mcp = MCPClient(lambda: streamablehttp_client("https://erh-guardian-mcp.<account>.workers.dev/mcp"))
with mcp:
    tools = mcp.list_tools_sync()
    agent = Agent(model=bedrock_model, tools=[*ALL_TOOLS, *tools])
```

## Tools

- `get_profile` / `update_profile` — value-alignment profile CRUD
- `log_decision` — append a GuardianGate decision to the audit log
- `list_decisions` — recent decisions, newest first (transparency panel feed)
