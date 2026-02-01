---
paths: "**/*.ts", "**/*durable*.ts", wrangler.jsonc
---

# Cloudflare Durable Objects Corrections

## MUST Export Class from Worker

```typescript
/* ❌ "Binding not found" error */
class MyDO extends DurableObject {
  // ...
}
// Missing export!

/* ✅ Export the class */
export class MyDO extends DurableObject {
  // ...
}
export default { fetch: handler } // Also export default
```

## SQLite: new_sqlite_classes in FIRST Migration

```typescript
/* ❌ Cannot add SQLite to existing class */
// migrations: [
//   { tag: 'v1' },
//   { tag: 'v2', new_sqlite_classes: ['MyDO'] } // Too late!
// ]

/* ✅ Must be in v1 migration */
// wrangler.jsonc:
{
  "durable_objects": {
    "bindings": [{ "name": "MY_DO", "class_name": "MyDO" }]
  },
  "migrations": [
    { "tag": "v1", "new_sqlite_classes": ["MyDO"] } // First migration!
  ]
}
```

## WebSocket Hibernation: Use ctx.acceptWebSocket

```typescript
/* ❌ Manual accept breaks hibernation */
webSocketPair[1].accept()

/* ✅ Use context method for hibernation support */
this.ctx.acceptWebSocket(webSocket)
```

## In-Memory State Lost on Hibernation

```typescript
/* ❌ State cleared after ~10s idle */
class MyDO extends DurableObject {
  userData = {} // Lost on hibernation!
}

/* ✅ Persist WebSocket metadata */
this.ctx.acceptWebSocket(ws)
ws.serializeAttachment({ userId, roomId })

// Retrieve on wake:
const { userId } = ws.deserializeAttachment()
```

## Use Alarms, Not setTimeout

```typescript
/* ❌ setTimeout prevents hibernation */
setTimeout(() => this.cleanup(), 60000)

/* ✅ Use alarms API */
await this.ctx.storage.setAlarm(Date.now() + 60000)

async alarm() {
  await this.cleanup()
}
```

## Always Call super() First

```typescript
/* ✅ Required in constructor */
constructor(ctx: DurableObjectState, env: Env) {
  super(ctx, env) // Must be first!
  // Then your initialization...
}
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Class not exported | Add `export class MyDO` |
| SQLite in later migration | Move to first migration (`v1`) |
| `ws.accept()` | `this.ctx.acceptWebSocket(ws)` |
| Instance properties for state | `serializeAttachment()` for WebSocket data |
| `setTimeout` | `setAlarm()` |
