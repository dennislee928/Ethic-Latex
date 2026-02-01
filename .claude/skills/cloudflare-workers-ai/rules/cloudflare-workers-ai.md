---
paths: "**/*.ts", wrangler.jsonc
---

# Cloudflare Workers AI Corrections

## max_tokens Breaking Change (April 2025)

```typescript
/* ⚠️ max_tokens now correctly defaults to 256 */
// Before April 2025: max_tokens was ignored
// After: Actually enforced, default 256

/* ✅ Always set max_tokens explicitly */
const response = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
  prompt: 'Write a story',
  max_tokens: 1024, // Set explicitly!
})
```

## BGE Embeddings Pooling Change (April 2025)

```typescript
/* ❌ mean pooling not backwards compatible */
const result = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
  text: 'Hello',
  pooling: 'mean', // Changed behavior!
})

/* ✅ Use cls pooling */
const result = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
  text: 'Hello',
  pooling: 'cls', // Recommended
})
```

## Always Use Streaming for Text

```typescript
/* ❌ Buffering issues with large responses */
const response = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
  prompt: 'Write a long story',
})

/* ✅ Use streaming to prevent buffering */
const stream = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
  prompt: 'Write a long story',
  stream: true,
})
return new Response(stream, {
  headers: { 'Content-Type': 'text/event-stream' },
})
```

## Manual SSE Parsing Required

```typescript
/* ✅ Parse SSE format manually */
const stream = await env.AI.run(model, { prompt, stream: true })
const reader = stream.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  const chunk = decoder.decode(value)
  // Format: data: {"response":"text"}\n\n
  for (const line of chunk.split('\n')) {
    if (line.startsWith('data: ') && line !== 'data: [DONE]') {
      const { response } = JSON.parse(line.slice(6))
      // Use response text
    }
  }
}
```

## Model Deprecations (October 2025)

```typescript
/* ❌ Older models deprecated */
'@cf/meta/llama-2-7b-chat'  // Deprecated

/* ✅ Use current models */
'@cf/meta/llama-3.1-8b-instruct'   // Text
'@cf/meta/llama-3.2-11b-vision'    // Vision
'@cf/baai/bge-base-en-v1.5'        // Embeddings
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| No `max_tokens` set | Always set explicitly |
| `pooling: 'mean'` for BGE | `pooling: 'cls'` |
| Non-streaming for text | Always use `stream: true` |
| Auto SSE parsing | Manual TextDecoder + line parsing |
| Llama 2 models | Llama 3.1/3.2 models |
