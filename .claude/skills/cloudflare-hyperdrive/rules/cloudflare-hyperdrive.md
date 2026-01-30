---
paths: "**/*.ts", wrangler.jsonc
---

# Cloudflare Hyperdrive Corrections

## nodejs_compat REQUIRED

```typescript
/* ❌ "No such module 'node:*'" error */
// Missing compatibility flag

/* ✅ Add to wrangler.jsonc */
{
  "compatibility_flags": ["nodejs_compat"]
}
```

## Connection Cleanup: Use waitUntil

```typescript
/* ❌ Blocks response */
export default {
  async fetch(request, env, ctx) {
    const client = new Client(env.HYPERDRIVE.connectionString)
    await client.connect()
    const result = await client.query('SELECT * FROM users')
    await client.end() // Blocks!
    return Response.json(result.rows)
  }
}

/* ✅ Non-blocking cleanup with waitUntil */
export default {
  async fetch(request, env, ctx) {
    const client = new Client(env.HYPERDRIVE.connectionString)
    await client.connect()
    const result = await client.query('SELECT * FROM users')
    ctx.waitUntil(client.end()) // Non-blocking!
    return Response.json(result.rows)
  }
}
```

## Pool Max: 5 Connections

```typescript
/* ❌ Too many connections */
const pool = new Pool({
  connectionString: env.HYPERDRIVE.connectionString,
  max: 10, // Workers limit is 6 total!
})

/* ✅ Max 5 connections */
const pool = new Pool({
  connectionString: env.HYPERDRIVE.connectionString,
  max: 5, // Leave room for other connections
})
```

## mysql2: Disable eval

```typescript
/* ❌ "eval() disallowed" error */
import mysql from 'mysql2/promise'
const conn = await mysql.createConnection(env.HYPERDRIVE.connectionString)

/* ✅ Disable eval for Workers */
import mysql from 'mysql2/promise'
const conn = await mysql.createConnection({
  uri: env.HYPERDRIVE.connectionString,
  disableEval: true, // Required!
})
```

## Use Prepared Statements

```typescript
/* ✅ Better caching with prepared statements */
const result = await client.query(
  'SELECT * FROM users WHERE id = $1',
  [userId]
)
// Hyperdrive caches prepared statement plans
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Missing `nodejs_compat` | Add to `compatibility_flags` |
| `await client.end()` | `ctx.waitUntil(client.end())` |
| `max: 10` in pool | `max: 5` (Workers limit) |
| mysql2 without config | Add `disableEval: true` |
| String interpolation | Use prepared statements with `$1` params |
