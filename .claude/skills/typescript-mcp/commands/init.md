# Init TypeScript MCP Server

Scaffold a TypeScript MCP server for Cloudflare Workers with tools, resources, and prompts.

---

## Your Task

Follow these steps to create a new TypeScript MCP server.

### 1. Gather Project Details

Ask the user for:
- **Project name**
- **MCP capabilities**: Tools, Resources, Prompts, or all
- **Transport**: Streamable HTTP (remote) or stdio (local)
- **Platform**: Cloudflare Workers or Node.js

Defaults:
- Name: "my-mcp"
- Capabilities: Tools only
- Transport: Streamable HTTP
- Platform: Cloudflare Workers

### 2. Scaffold Project

**For Cloudflare Workers:**
```bash
npm create cloudflare@latest <project-name> -- --type hello-world --ts --git --deploy false
cd <project-name>
npm install @modelcontextprotocol/sdk hono zod
npm install -D @cloudflare/workers-types
```

**For Node.js:**
```bash
mkdir <project-name> && cd <project-name>
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node tsx
```

### 3. Create Server Structure

```
src/
├── index.ts           # Entry point
├── server.ts          # MCP server configuration
├── tools/
│   └── index.ts       # Tool definitions
├── resources/         # If resources enabled
│   └── index.ts
└── prompts/           # If prompts enabled
    └── index.ts
```

### 4. Create MCP Server

Create `src/server.ts`:

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';

export function createServer() {
  const server = new McpServer({
    name: '<project-name>',
    version: '1.0.0',
  });

  // Register a sample tool
  server.registerTool(
    'echo',
    {
      description: 'Echo back the input text',
      inputSchema: z.object({
        text: z.string().describe('Text to echo'),
      }),
    },
    async ({ text }) => ({
      content: [{ type: 'text', text: `Echo: ${text}` }],
    })
  );

  return server;
}
```

### 5. Create Entry Point

**For Cloudflare Workers** (`src/index.ts`):

```typescript
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { createServer } from './server';

const app = new Hono();

app.use('/mcp/*', cors());

app.post('/mcp', async (c) => {
  const server = createServer();
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });
  await server.connect(transport);
  return transport.handleRequest(c.req.raw);
});

app.get('/', (c) => c.json({ name: '<project-name>', mcp: '/mcp' }));

export default app;
```

**For Node.js stdio** (`src/index.ts`):

```typescript
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { createServer } from './server';

async function main() {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP server running on stdio');
}

main().catch(console.error);
```

### 6. Configure TypeScript

Create/update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist"
  },
  "include": ["src"]
}
```

### 7. Configure Platform

**For Cloudflare Workers** (`wrangler.jsonc`):
```jsonc
{
  "name": "<project-name>",
  "main": "src/index.ts",
  "compatibility_date": "2025-11-11",
  "compatibility_flags": ["nodejs_compat"]
}
```

**For Node.js** (update `package.json`):
```json
{
  "type": "module",
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  }
}
```

### 8. Add to Claude Desktop (if stdio)

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "<project-name>": {
      "command": "node",
      "args": ["path/to/<project-name>/dist/index.js"]
    }
  }
}
```

### 9. Provide Next Steps

```
✅ TypeScript MCP Server "<project-name>" created!

📁 Structure:
   - src/server.ts     (MCP server + tools)
   - src/index.ts      (Entry point)

🚀 Next steps:
   1. Add tools in src/server.ts
   2. npm run dev      (Start development)
   3. Deploy or connect to Claude

📚 Skill loaded: typescript-mcp
   - Streamable HTTP for remote servers
   - stdio transport for local servers
   - Zod schema validation included
```

---

## Transport Selection Guide

| Transport | Use Case |
|-----------|----------|
| **Streamable HTTP** | Remote servers, Claude.ai, web clients |
| **stdio** | Local servers, Claude Desktop |
| **SSE** | Legacy, prefer Streamable HTTP |
