---
paths: "**/*.ts", "**/*mcp*.ts", wrangler.jsonc
---

# Cloudflare MCP Server Corrections

## #1 Failure: Base Path Mismatch

```typescript
/* ❌ Server and client paths don't match */
// Server:
app.get('/sse', (c) => mcp.serveSSE('/sse').fetch(c.req.raw, c.env))

// Client config:
{ "url": "https://worker.dev/mcp" } // Wrong path!

/* ✅ Test with curl, match exactly */
// 1. Test: curl https://worker.dev/sse
// 2. Use same URL in client config
{ "url": "https://worker.dev/sse" }
```

## MUST Export McpAgent Class

```typescript
/* ❌ "Binding not found" error */
class MyMcpAgent extends McpAgent { }

/* ✅ Export the class */
export class MyMcpAgent extends McpAgent { }
```

## Use startsWith for Path Matching

```typescript
/* ❌ Exact match breaks sub-paths */
if (pathname === '/sse') { }

/* ✅ Use startsWith */
if (pathname.startsWith('/sse')) { }
```

## Add OPTIONS Handler for CORS

```typescript
/* ❌ Browser clients blocked by CORS preflight */
app.get('/sse', handler)

/* ✅ Handle OPTIONS for browser clients */
app.options('/sse', (c) => {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
})
app.get('/sse', handler)
```

## OAuth Redirect URIs Must Match

```typescript
/* ❌ Works in dev, fails after deploy */
// OAuth configured for localhost
// Deployed to worker.dev

/* ✅ Update ALL OAuth URLs after deployment */
// 1. Update OAuth provider settings
// 2. Update client config
// 3. Test with curl before integrating
```

## WebSocket State: Use Storage

```typescript
/* ❌ Instance properties lost on hibernation */
class MyAgent extends McpAgent {
  userData = {} // Lost!
}

/* ✅ Use this.state.storage */
class MyAgent extends McpAgent {
  async saveData(data) {
    await this.state.storage.put('userData', data)
  }
  async getData() {
    return await this.state.storage.get('userData')
  }
}
```

## Durable Objects Migration Required

```jsonc
/* ✅ wrangler.jsonc */
{
  "durable_objects": {
    "bindings": [{ "name": "MCP_AGENT", "class_name": "MyMcpAgent" }]
  },
  "migrations": [
    { "tag": "v1", "new_classes": ["MyMcpAgent"] }
  ]
}
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Different server/client paths | Test with curl, use exact URL |
| Class not exported | Add `export class MyMcpAgent` |
| `pathname === '/sse'` | `pathname.startsWith('/sse')` |
| Missing CORS | Add OPTIONS handler |
| Instance properties | Use `this.state.storage` |
| Missing migration | Add to wrangler.jsonc migrations |
