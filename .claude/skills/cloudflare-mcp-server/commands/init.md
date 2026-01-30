# Init MCP Server

Scaffold a new MCP server on Cloudflare Workers with TypeScript, OAuth support, and Durable Objects.

---

## Your Task

Follow these steps to create a new MCP server project.

### 1. Gather Project Details

Ask the user for:
- **Project name** (used for directory and worker name)
- **Authentication type**: OAuth (Claude.ai compatible) or API Key (simpler)
- **Features needed**: Tools only, or Tools + Resources + Prompts

Defaults if not specified:
- Name: "my-mcp-server"
- Auth: OAuth (recommended for Claude.ai)
- Features: Tools only

### 2. Scaffold Project

```bash
npm create cloudflare@latest <project-name> -- --type hello-world --ts --git --deploy false
cd <project-name>
```

### 3. Install Dependencies

```bash
npm install @modelcontextprotocol/sdk hono zod
npm install -D @cloudflare/workers-types wrangler typescript
```

**If OAuth selected:**
```bash
npm install @cloudflare/workers-oauth-provider
```

### 4. Create Directory Structure

```
src/
├── index.ts           # Main worker entry
├── mcp/
│   ├── server.ts      # MCP server setup
│   └── tools/
│       └── index.ts   # Tool definitions
├── auth/              # If OAuth
│   └── oauth.ts
└── types.ts           # TypeScript types
```

### 5. Create MCP Server

Create `src/mcp/server.ts`:

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { registerTools } from './tools';

export function createMcpServer() {
  const server = new McpServer({
    name: '<project-name>',
    version: '1.0.0',
  });

  registerTools(server);

  return server;
}
```

### 6. Create Example Tool

Create `src/mcp/tools/index.ts`:

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';

export function registerTools(server: McpServer) {
  server.registerTool(
    'hello',
    {
      description: 'Say hello to someone',
      inputSchema: z.object({
        name: z.string().describe('Name to greet'),
      }),
    },
    async ({ name }) => ({
      content: [{ type: 'text', text: `Hello, ${name}!` }],
    })
  );

  // Add more tools here
}
```

### 7. Create Main Entry

Create `src/index.ts`:

```typescript
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { createMcpServer } from './mcp/server';

type Bindings = {
  // Add your bindings here
};

const app = new Hono<{ Bindings: Bindings }>();

app.use('/mcp/*', cors());

app.post('/mcp', async (c) => {
  const server = createMcpServer();
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });

  await server.connect(transport);
  return transport.handleRequest(c.req.raw);
});

app.get('/', (c) => c.json({
  name: '<project-name>',
  endpoints: { mcp: '/mcp' }
}));

export default app;
```

### 8. Configure wrangler.jsonc

```jsonc
{
  "name": "<project-name>",
  "main": "src/index.ts",
  "compatibility_date": "2025-11-11",
  "compatibility_flags": ["nodejs_compat"]
}
```

**If OAuth selected, add Durable Objects:**
```jsonc
{
  "durable_objects": {
    "bindings": [
      { "name": "OAUTH_PROVIDER", "class_name": "OAuthProvider" }
    ]
  },
  "migrations": [
    { "tag": "v1", "new_sqlite_classes": ["OAuthProvider"] }
  ]
}
```

### 9. Create TypeScript Config

Ensure `tsconfig.json` has:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "bundler",
    "strict": true,
    "types": ["@cloudflare/workers-types"]
  }
}
```

### 10. Provide Next Steps

```
✅ MCP Server "<project-name>" created!

📁 Structure:
   - src/index.ts           (Worker entry)
   - src/mcp/server.ts      (MCP server setup)
   - src/mcp/tools/index.ts (Tool definitions)

🚀 Next steps:
   1. cd <project-name>
   2. Add your tools in src/mcp/tools/index.ts
   3. npm run dev           (Start local dev)
   4. npx wrangler deploy   (Deploy to Cloudflare)

🔗 Connect to Claude.ai:
   Settings → MCP Servers → Add → https://<worker>.workers.dev/mcp

📚 Skill loaded: cloudflare-mcp-server
   - 22 common issues auto-prevented
   - OAuth ready for Claude.ai integration
```

---

## Critical Patterns Applied

1. **StreamableHTTPServerTransport**: Required for remote MCP servers
2. **CORS middleware**: Required for browser-based clients
3. **nodejs_compat**: Required for MCP SDK
4. **Durable Objects**: Required for OAuth state management
