---
paths: "**/*.ts", "**/mcp*.ts", "**/server*.ts", "**/tools*.ts"
---

# TypeScript MCP Server Corrections

MCP (Model Context Protocol) is new (2024+). Claude's training may have limited or no MCP knowledge.

## SDK Import

```typescript
/* ❌ Wrong/outdated import */
import { Server } from 'mcp'
import { MCPServer } from '@modelcontextprotocol/server'

/* ✅ Correct import */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
```

## Server Setup

```typescript
/* ❌ Incomplete setup */
const server = new McpServer()

/* ✅ Full setup with info */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'

const server = new McpServer({
  name: 'my-server',
  version: '1.0.0',
})

// Connect transport
const transport = new StdioServerTransport()
await server.connect(transport)
```

## Tool Definition

```typescript
/* ❌ Wrong tool schema */
server.addTool({
  name: 'my_tool',
  description: 'Does something',
  parameters: { type: 'object', properties: {...} },
})

/* ✅ Correct tool definition */
server.tool(
  'my_tool',
  'Does something useful',
  {
    input: z.object({
      query: z.string().describe('The search query'),
    }),
  },
  async ({ input }) => {
    return {
      content: [{ type: 'text', text: `Result for: ${input.query}` }],
    }
  }
)
```

## Resource Definition

```typescript
/* ❌ Wrong resource pattern */
server.addResource({ uri: 'file://...', content: '...' })

/* ✅ Correct resource handler */
server.resource(
  'config',
  'config://settings',
  async (uri) => ({
    contents: [{
      uri: uri.href,
      mimeType: 'application/json',
      text: JSON.stringify(config),
    }],
  })
)
```

## Error Handling

```typescript
/* ❌ Throwing generic errors */
throw new Error('Something went wrong')

/* ✅ MCP error format */
return {
  content: [{
    type: 'text',
    text: 'Error: Something went wrong',
  }],
  isError: true,
}
```

## Cloudflare Workers Transport

```typescript
/* ❌ Using stdio in Workers */
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'

/* ✅ Use SSE or custom transport for Workers */
// For Cloudflare Workers, use workers-mcp-server package
// or implement custom SSE transport
import { McpAgent } from 'workers-mcp-server'
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `import { Server }` | `import { McpServer }` |
| `server.addTool()` | `server.tool()` |
| `parameters: {...}` | Zod schema: `{ input: z.object({...}) }` |
| `throw new Error()` | Return `{ content: [...], isError: true }` |
| stdio transport in Workers | SSE or workers-mcp-server |
| `@modelcontextprotocol/server` | `@modelcontextprotocol/sdk/server/mcp.js` |
