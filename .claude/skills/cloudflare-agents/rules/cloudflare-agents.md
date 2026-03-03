---
paths: "**/*.ts", "**/*agent*.ts", wrangler.jsonc
---

# Cloudflare Agents Corrections

## Do You Need Agents? (80% Don't)

```typescript
/* Most apps just need AI SDK directly */
// Simple chat = AI SDK
// Stateful multi-turn = Cloudflare Agents

/* Use Agents when you need: */
// - Persistent state across sessions
// - WebSocket real-time chat
// - Scheduled tasks from AI
// - Complex multi-step workflows
```

## SQLite in First Migration (Same as DOs)

```typescript
/* ❌ Cannot add SQLite later */
migrations: [
  { tag: 'v1' },
  { tag: 'v2', new_sqlite_classes: ['MyAgent'] } // Too late!
]

/* ✅ Must be in v1 */
migrations: [
  { tag: 'v1', new_sqlite_classes: ['MyAgent'] }
]
```

## MUST Export Agent Class

```typescript
/* ❌ "Binding not found" */
class MyAgent extends Agent { }

/* ✅ Export the class */
export class MyAgent extends Agent { }
```

## Authenticate in Worker BEFORE Agent

```typescript
/* ❌ Auth inside agent (too late) */
class MyAgent extends Agent {
  async onConnect() {
    if (!authenticated) throw new Error('Unauthorized')
  }
}

/* ✅ Auth in Worker before creating agent */
export default {
  async fetch(request, env) {
    const user = await authenticate(request)
    if (!user) return new Response('Unauthorized', { status: 401 })

    // Now create agent with authenticated user
    return env.AGENT.get(env.AGENT.idFromName(user.id)).fetch(request)
  }
}
```

## Workers AI SSE Parsing

```typescript
/* ❌ Expecting automatic parsing */
const stream = await env.AI.run('@cf/meta/llama-3-8b', { stream: true })

/* ✅ Manual SSE parsing required */
const reader = stream.getReader()
const decoder = new TextDecoder()
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  const text = decoder.decode(value)
  // Parse SSE format: data: {...}\n\n
  for (const line of text.split('\n')) {
    if (line.startsWith('data: ')) {
      const json = JSON.parse(line.slice(6))
      // Process json.response
    }
  }
}
```

## Global Instance Naming

```typescript
/* ⚠️ Same name = same agent globally */
const id = env.AGENT.idFromName('user-123')
// Anyone with 'user-123' accesses same agent!

/* ✅ Use unique, unpredictable names */
const id = env.AGENT.idFromName(`user:${userId}:${sessionId}`)
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Agents for simple chat | AI SDK directly |
| SQLite in later migration | First migration (`v1`) |
| Auth inside agent | Auth in Worker first |
| Auto SSE parsing | Manual TextDecoder + line parsing |
| Simple `idFromName` | Include user-specific prefix |
