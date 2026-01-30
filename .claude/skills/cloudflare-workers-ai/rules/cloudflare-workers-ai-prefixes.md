---
globs: ["**/wrangler.jsonc", "**/wrangler.toml", "**/*.ts", "**/*.tsx", "**/*.js"]
---

# Cloudflare Workers AI Model Prefixes

Workers AI models use two prefixes that BOTH require routing through the native `env.AI.run()` binding, not AI Gateway.

## Prefixes

| Prefix | Source | Example |
|--------|--------|---------|
| `@cf/` | Cloudflare-hosted models | `@cf/meta/llama-4-scout-17b-16e-instruct` |
| `@hf/` | Hugging Face on Workers AI | `@hf/nousresearch/hermes-2-pro-mistral-7b` |

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Route only `@cf/` through `env.AI.run()` | Route BOTH `@cf/` AND `@hf/` through `env.AI.run()` |
| Send `@hf/` models to AI Gateway | Use native Workers AI binding |
| `model.startsWith('@cf/')` only | `model.startsWith('@cf/') \|\| model.startsWith('@hf/')` |

## Correct Routing Pattern

```typescript
// In parseModelId()
if (modelId.startsWith('@cf/') || modelId.startsWith('@hf/')) {
  return { provider: 'cloudflare', model: modelId };
}

// In chat() - route through native binding
if ((model.startsWith('@cf/') || model.startsWith('@hf/')) && env.AI) {
  const response = await env.AI.run(model, { messages, tools });
  // ...
}

// When detecting OpenRouter models (exclude Workers AI)
const isOpenRouterModel = options.model.includes('/') &&
  !options.model.startsWith('@cf/') &&
  !options.model.startsWith('@hf/');
```

## Error Symptom

If `@hf/` models return "not a valid model ID" error, they're being sent to AI Gateway instead of Workers AI binding.

## Why This Matters

- AI Gateway doesn't recognize Workers AI model IDs
- Workers AI models are FREE on the edge - no API key needed
- Native binding has better performance than gateway routing
