---
globs: ["**/*.ts", "**/*.tsx", "wrangler.jsonc", "wrangler.toml"]
---

# Cloudflare Workers AI Function-Calling Models

Reference for Workers AI models that support tool/function calling.

## Function-Calling Models (Verified Jan 2026)

| Model ID | Name | Context |
|----------|------|---------|
| `@cf/meta/llama-4-scout-17b-16e-instruct` | Llama 4 Scout 17B | 131k |
| `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | Llama 3.3 70B (Fast) | 24k |
| `@cf/ibm-granite/granite-4.0-h-micro` | IBM Granite 4.0 Micro | 131k |
| `@cf/qwen/qwen3-30b-a3b-fp8` | Qwen 3 30B | 32k |
| `@cf/mistralai/mistral-small-3.1-24b-instruct` | Mistral Small 3.1 24B | 128k |
| `@hf/nousresearch/hermes-2-pro-mistral-7b` | Hermes 2 Pro 7B | 24k |
| `@cf/openai/gpt-oss-120b` | OpenAI GPT-OSS 120B | 128k |
| `@cf/openai/gpt-oss-20b` | OpenAI GPT-OSS 20B | 128k |

📚 **Source**: https://developers.cloudflare.com/workers-ai/features/function-calling/

## New 2025 Partner Models

| Model ID | Type | Provider | Added |
|----------|------|----------|-------|
| `@cf/openai/gpt-oss-120b` | Text Gen | OpenAI | Aug 2025 |
| `@cf/openai/gpt-oss-20b` | Text Gen | OpenAI | Aug 2025 |
| `@cf/deepgram/aura-1` | TTS | Deepgram | Aug 2025 |
| `@cf/deepgram/nova-3` | STT | Deepgram | Aug 2025 |
| `@cf/leonardo/lucid-origin` | Image Gen | Leonardo | Aug 2025 |
| `@cf/leonardo/phoenix-1.0` | Image Gen | Leonardo | Aug 2025 |
| `@cf/pipecat-ai/smart-turn-v2` | Turn Detect | Pipecat | Aug 2025 |
| `@cf/myshell-ai/melotts` | TTS | MyShell | Mar 2025 |
| `@cf/baai/bge-m3` | Embeddings | BAAI | Mar 2025 |
| `@cf/baai/bge-reranker-base` | Reranker | BAAI | Mar 2025 |
| `@cf/openai/whisper-large-v3-turbo` | STT | OpenAI | Mar 2025 |

📚 **Source**: https://developers.cloudflare.com/changelog/

## Model ID Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `@cf/ibm/granite-4.0-h-micro` | `@cf/ibm-granite/granite-4.0-h-micro` |
| `@cf/qwen/qwen2.5-coder-32b-instruct` | Remove (no function calling support) |

## Dynamic Discovery via API

Cloudflare has an API to list models with metadata including function-calling support:

```bash
# Via Wrangler CLI
npx wrangler ai models --json

# Via REST API
GET https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/models/search
Authorization: Bearer {CF_API_TOKEN}
```

### Filtering for Function-Calling Models

```typescript
const functionCallingModels = data.result
  .filter(m => {
    const isTextGen = m.task?.name === 'Text Generation';
    const hasFunctionCalling = m.properties?.some(
      p => p.property_id === 'function_calling' && p.value === 'true'
    );
    return isTextGen && hasFunctionCalling;
  });
```

## Important Notes

- **Qwen 2.5** does NOT support function calling (only Qwen 3 does)
- **Qwen 3** outputs tool calls as JSON in text response (parse with regex fallback)
- All Workers AI models are FREE - no API key required
- Use native `env.AI.run()` binding, not AI Gateway
