---
paths: "**/*.ts", wrangler.jsonc, wrangler.toml
---

# Cloudflare Queues Corrections

## CRITICAL: Configure Dead Letter Queue

```typescript
/* ❌ Messages PERMANENTLY DELETED after max_retries */
// No DLQ configured...

/* ✅ Always configure DLQ in production */
// wrangler.jsonc:
{
  "queues": {
    "consumers": [{
      "queue": "my-queue",
      "dead_letter_queue": "my-queue-dlq", // Required!
      "max_retries": 3
    }]
  }
}
```

## Message Size Limit: 128KB

```typescript
/* ❌ Message too large */
await env.QUEUE.send({ largeData: megabytesOfData })

/* ✅ Store large data in R2, send reference */
const key = `data/${crypto.randomUUID()}`
await env.BUCKET.put(key, largeData)
await env.QUEUE.send({ dataRef: key })
```

## Explicit Ack for Non-Idempotent Operations

```typescript
/* ❌ Entire batch retried if one fails */
async queue(batch, env) {
  for (const msg of batch.messages) {
    await processMessage(msg) // If one fails, all retry
  }
}

/* ✅ Explicit ack for DB writes, payments, API calls */
async queue(batch, env) {
  for (const msg of batch.messages) {
    try {
      await processMessage(msg)
      msg.ack() // Explicit acknowledgment
    } catch (error) {
      msg.retry({ delaySeconds: 60 * Math.pow(2, msg.attempts - 1) })
    }
  }
}
```

## Don't Assume FIFO Ordering

```typescript
/* ❌ Relying on message order */
// Messages may arrive out of order

/* ✅ Include timestamp/sequence if order matters */
await env.QUEUE.send({
  data: payload,
  timestamp: Date.now(),
  sequence: getNextSequence(),
})
```

## Throughput Limit: 5,000 msg/s

```typescript
/* ✅ Use sendBatch with delays for high throughput */
const batches = chunks(messages, 100)
for (const batch of batches) {
  await env.QUEUE.sendBatch(batch)
  await new Promise(r => setTimeout(r, 100)) // Throttle
}
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| No DLQ configured | Add `dead_letter_queue` in wrangler.jsonc |
| Large message body | Store in R2, send reference |
| No explicit ack | Use `msg.ack()` for non-idempotent ops |
| Assuming FIFO order | Include timestamp/sequence |
| High-volume sends | Use `sendBatch()` with throttling |
