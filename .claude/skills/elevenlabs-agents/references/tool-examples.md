# Tool Examples

## Client Tools (Browser-Side)

### Update Shopping Cart
```typescript
import { useConversation } from '@elevenlabs/react';
import { z } from 'zod';

clientTools: {
  updateCart: {
    description: "Add or remove items from the shopping cart",
    parameters: z.object({
      action: z.enum(['add', 'remove']),
      item: z.string(),
      quantity: z.number().min(1)
    }),
    handler: async ({ action, item, quantity }) => {
      const cart = getCart();
      if (action === 'add') {
        cart.add(item, quantity);
      } else {
        cart.remove(item, quantity);
      }
      return { success: true, total: cart.total, items: cart.items.length };
    }
  }
}
```

### Navigate to Page
```typescript
navigate: {
  description: "Navigate user to a different page",
  parameters: z.object({
    url: z.string().url()
  }),
  handler: async ({ url }) => {
    window.location.href = url;
    return { success: true };
  }
}
```

## Server Tools (Webhooks)

### Get Weather
```json
{
  "name": "get_weather",
  "description": "Fetch current weather for a city",
  "url": "https://api.weather.com/v1/current",
  "method": "GET",
  "parameters": {
    "type": "object",
    "properties": {
      "city": { "type": "string", "description": "City name (e.g., 'London')" }
    },
    "required": ["city"]
  },
  "headers": {
    "Authorization": "Bearer {{secret__weather_api_key}}"
  }
}
```

### Stripe Payment
```json
{
  "name": "create_payment_intent",
  "description": "Create a Stripe payment intent for order",
  "url": "https://api.stripe.com/v1/payment_intents",
  "method": "POST",
  "parameters": {
    "type": "object",
    "properties": {
      "amount": { "type": "number", "description": "Amount in cents" },
      "currency": { "type": "string", "description": "Currency code (e.g., 'usd')" }
    },
    "required": ["amount", "currency"]
  },
  "headers": {
    "Authorization": "Bearer {{secret__stripe_api_key}}"
  }
}
```

### CRM Integration
```json
{
  "name": "update_crm",
  "description": "Update customer record in CRM",
  "url": "https://api.salesforce.com/services/data/v57.0/sobjects/Contact/{{contact_id}}",
  "method": "PATCH",
  "parameters": {
    "type": "object",
    "properties": {
      "notes": { "type": "string" },
      "status": { "type": "string", "enum": ["active", "resolved", "pending"] }
    }
  },
  "headers": {
    "Authorization": "Bearer {{secret__salesforce_token}}",
    "Content-Type": "application/json"
  }
}
```

## MCP Tools

### Critical: ElevenLabs MCP Server Compatibility

ElevenLabs labels their MCP integration as "Streamable HTTP" but **does NOT support** the actual MCP 2025-03-26 Streamable HTTP spec (SSE responses). Instead, ElevenLabs expects:

- **Plain JSON responses** (`application/json`), NOT SSE (`text/event-stream`)
- **Protocol version `2024-11-05`**, NOT the newer `2025-03-26`
- **Simple JSON-RPC over HTTP** with direct JSON responses

**What DOES NOT work:**
- Official MCP SDK's `createMcpHandler` (returns SSE format)
- Cloudflare Agents SDK `McpServer.serve()` (returns SSE format)
- Any server returning `Content-Type: text/event-stream`

**What WORKS:**
- Raw Hono + JSON-RPC pattern with `c.json()` responses
- Protocol version `2024-11-05` in initialize response
- Plain `application/json` Content-Type

### Working MCP Server Pattern for ElevenLabs

```typescript
import { Hono } from 'hono';
import { cors } from 'hono/cors';

const tools = [{
  name: "my_tool",
  description: "Tool description",
  inputSchema: {
    type: "object",
    properties: {
      param1: { type: "string", description: "Description" }
    },
    required: ["param1"]
  }
}];

async function handleMCPRequest(request, env) {
  const { id, method, params } = request;

  switch (method) {
    case 'initialize':
      return {
        jsonrpc: '2.0', id,
        result: {
          protocolVersion: '2024-11-05',  // MUST be 2024-11-05, NOT 2025-03-26
          serverInfo: { name: 'my-mcp-server', version: '1.0.0' },
          capabilities: { tools: {} }
        }
      };

    case 'tools/list':
      return { jsonrpc: '2.0', id, result: { tools } };

    case 'tools/call':
      const result = await handleTool(params.name, params.arguments, env);
      return { jsonrpc: '2.0', id, result };

    default:
      return { jsonrpc: '2.0', id, error: { code: -32601, message: `Method not found: ${method}` } };
  }
}

const app = new Hono();

app.use('/*', cors({ origin: '*', allowMethods: ['GET', 'POST', 'OPTIONS'], allowHeaders: ['Content-Type', 'Authorization'] }));

app.post('/mcp', async (c) => {
  const body = await c.req.json();
  const response = await handleMCPRequest(body, c.env);
  return c.json(response);  // Plain JSON, NOT SSE
});

export default app;
```

### Connect MCP Server in ElevenLabs

In ElevenLabs agent settings → Tools → Custom MCP Server:

```json
{
  "name": "My MCP Server",
  "server_url": "https://my-mcp.workers.dev/mcp",
  "transport": "streamable_http"
}
```

Note: Despite selecting "Streamable HTTP", ElevenLabs actually sends plain JSON-RPC requests and expects plain JSON responses.

### Connect PostgreSQL MCP Server
```json
{
  "name": "PostgreSQL Database",
  "server_url": "https://mcp.example.com/postgres",
  "transport": "sse",
  "secret_token": "{{secret__mcp_auth_token}}",
  "approval_mode": "fine_grained"
}
```

### Connect File System MCP Server
```json
{
  "name": "File System Access",
  "server_url": "https://mcp.example.com/filesystem",
  "transport": "http",
  "approval_mode": "always_ask"
}
```

## System Tools

### Update Conversation State
```json
{
  "name": "update_state",
  "description": "Update conversation context",
  "parameters": {
    "key": { "type": "string" },
    "value": { "type": "string" }
  }
}
```

### Transfer to Human
```json
{
  "name": "transfer_to_human",
  "description": "Transfer call to human agent",
  "parameters": {
    "reason": { "type": "string", "description": "Reason for transfer" }
  }
}
```

## Best Practices

**Client Tools**:
- Keep handler logic simple
- Always return meaningful values
- Handle errors gracefully

**Server Tools**:
- Use secret variables for API keys
- Provide clear parameter descriptions
- Include format examples in descriptions

**MCP Tools**:
- Test connectivity before production
- Use appropriate approval modes
- Monitor tool usage and errors

**System Tools**:
- Use for workflow state management
- Document state schema
- Clean up state when conversation ends
