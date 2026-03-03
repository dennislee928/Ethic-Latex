---
paths: "**/*.ts", "**/*.tsx", "**/*claude*.ts", "**/*anthropic*.ts"
---

# Claude API Corrections

Claude's training may reference older patterns. This uses **@anthropic-ai/sdk v0.71+**.

## Model IDs (Jan 2026)

```typescript
/* ❌ DEPRECATED - Claude 3.x models */
'claude-3.5-sonnet'          // All versions deprecated
'claude-3-sonnet-20240229'   // Deprecated
'claude-3.7-sonnet'          // Deprecated Oct 28, 2025
'claude-3-5-haiku-20241022'  // Use claude-haiku-4-5 instead

/* ✅ Active models - Claude 4.x */
'claude-opus-4-5-20251101'   // Flagship - best reasoning, coding, agents ($5/$25 MTok)
'claude-sonnet-4-5-20250929' // Balanced performance ($3/$15 MTok)
'claude-opus-4-20250514'     // High capability ($15/$75 MTok)
'claude-haiku-4-5-20250929'  // Fast, near-frontier ($1/$5 MTok)
```

## Prompt Caching: cache_control on LAST Block

```typescript
/* ❌ cache_control not on last block (silently fails) */
const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  messages: [
    {
      role: 'user',
      content: [
        { type: 'text', text: longDocument, cache_control: { type: 'ephemeral' } }, // Wrong position!
        { type: 'text', text: 'Summarize this' },
      ],
    },
  ],
})

/* ✅ cache_control MUST be on LAST content block */
const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  messages: [
    {
      role: 'user',
      content: [
        { type: 'text', text: longDocument },
        { type: 'text', text: 'Summarize this', cache_control: { type: 'ephemeral' } }, // Correct!
      ],
    },
  ],
})
```

## Streaming Errors Occur Mid-Stream

```typescript
/* ❌ Only checking initial response */
const stream = await anthropic.messages.stream({...})
// No error handling...

/* ✅ Errors happen AFTER initial 200 response */
const stream = await anthropic.messages.stream({...})
stream.on('error', (error) => {
  console.error('Stream error:', error)
})
for await (const event of stream) {
  // Process events...
}
```

## Structured Outputs (v0.69.0+)

```typescript
/* ✅ New structured outputs feature */
const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Extract data' }],
  response_format: {
    type: 'json_schema',
    json_schema: {
      name: 'extraction',
      schema: { /* JSON Schema */ },
    },
  },
}, {
  headers: { 'anthropic-beta': 'structured-outputs-2025-11-13' },
})
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `claude-3.5-sonnet` | `claude-opus-4-5-20251101` or `claude-sonnet-4-5-20250929` |
| `claude-3.7-sonnet` | `claude-opus-4-5-20251101` or `claude-sonnet-4-5-20250929` |
| `claude-3-5-haiku` | `claude-haiku-4-5-20250929` |
| cache_control on first block | cache_control on LAST block |
| No stream error handler | Add `stream.on('error', ...)` |
| Extended thinking on Haiku | Only Opus 4.5, Sonnet 4.5, and Opus 4 support it |
