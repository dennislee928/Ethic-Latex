---
paths: "**/*.ts", wrangler.jsonc, wrangler.toml
---

# Cloudflare KV Corrections

## Rate Limit: 1 Write Per Second Per Key

```typescript
/* ❌ 429 error - too many writes to same key */
for (const item of items) {
  await env.KV.put('counter', String(count++))
}

/* ✅ Consolidate writes or use different keys */
// Option 1: Single write
await env.KV.put('counter', String(finalCount))

// Option 2: Different keys
await env.KV.put(`counter:${Date.now()}`, value)
```

## returnMetadata Changed to Enum

```typescript
/* ❌ Old boolean syntax */
await env.KV.get(key, { returnMetadata: true })

/* ✅ New enum syntax (V2) */
await env.KV.get(key, { returnMetadata: 'all' })
// Options: 'all' | 'indexed' | 'none'
```

## cacheTtl Minimum 60 Seconds

```typescript
/* ❌ Error: TTL too low */
await env.KV.get(key, { cacheTtl: 30 })

/* ✅ Minimum 60 seconds */
await env.KV.get(key, { cacheTtl: 60 })
```

## Check list_complete for Pagination

```typescript
/* ❌ Wrong pagination check */
const result = await env.KV.list()
if (result.keys.length === 0) { /* done */ }

/* ✅ Use list_complete flag */
let cursor: string | undefined
do {
  const result = await env.KV.list({ cursor })
  // Process result.keys...
  cursor = result.list_complete ? undefined : result.cursor
} while (cursor)
```

## Use Bulk Operations

```typescript
/* ❌ Multiple operations (counts against limits) */
await env.KV.get('key1')
await env.KV.get('key2')
await env.KV.get('key3')

/* ✅ Bulk operations (counts as 1) */
// For writes, use batch in wrangler or Workers KV API
// Max 10,000 keys per bulk operation
```

## Eventual Consistency (~60 seconds)

```typescript
/* ⚠️ Reads may be stale for ~60 seconds globally */
await env.KV.put('key', 'value')
const value = await env.KV.get('key') // May return old value!

/* For strong consistency, use Durable Objects instead */
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Multiple writes to same key | Consolidate or use different keys |
| `returnMetadata: true` | `returnMetadata: 'all'` |
| `cacheTtl < 60` | Minimum 60 seconds |
| `keys.length === 0` for pagination | Check `list_complete` flag |
| Strong consistency needs | Use Durable Objects |
