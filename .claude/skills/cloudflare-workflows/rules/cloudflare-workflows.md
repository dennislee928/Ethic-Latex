---
paths: "**/*.ts", "**/*workflow*.ts", wrangler.jsonc
---

# Cloudflare Workflows Corrections

## I/O MUST Be Inside step.do()

```typescript
/* ❌ I/O outside step context */
async run(event, step) {
  const data = await fetch('https://api.example.com') // Error!
  await step.do('process', async () => {
    return processData(data)
  })
}

/* ✅ All I/O inside step.do() */
async run(event, step) {
  const data = await step.do('fetch', async () => {
    const res = await fetch('https://api.example.com')
    return res.json()
  })
  await step.do('process', async () => {
    return processData(data)
  })
}
```

## Only JSON-Serializable Values

```typescript
/* ❌ Functions, symbols, undefined not allowed */
await step.do('bad', async () => {
  return {
    callback: () => {}, // Error!
    data: undefined,    // Error!
  }
})

/* ✅ Return only JSON-serializable values */
await step.do('good', async () => {
  return {
    status: 'complete',
    data: null, // Use null instead of undefined
  }
})
```

## NonRetryableError MUST Have Message

```typescript
/* ❌ Empty message behaves differently in dev vs prod */
throw new NonRetryableError('') // Buggy!

/* ✅ Always provide message */
throw new NonRetryableError('Invalid credentials')
throw new NonRetryableError('Validation failed: missing email')
```

## step.sleep() Doesn't Count Toward Limit

```typescript
/* ✅ Sleep doesn't count against 1,024 step limit */
await step.sleep('wait', '1 hour')
// This is free - use liberally for delays
```

## Use catch for Optional Steps

```typescript
/* ✅ Graceful degradation */
let enrichedData = null
try {
  enrichedData = await step.do('enrich', async () => {
    return await callOptionalAPI()
  })
} catch {
  // Continue without enrichment
}
await step.do('process', async () => {
  return process(data, enrichedData)
})
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| fetch() outside step | Move inside `step.do()` |
| Returning functions/undefined | Return JSON-serializable only |
| `NonRetryableError('')` | Include descriptive message |
| Worrying about sleep limits | `step.sleep()` is unlimited |
| All-or-nothing steps | Use try/catch for optional steps |
