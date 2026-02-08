---
paths: "**/*.ts", "**/*.tsx", "**/*gemini*.ts", package.json
---

# Google Gemini API Corrections

Claude's training may reference the deprecated SDK. This project uses **@google/genai v1.30+**.

## CRITICAL: SDK Migration

```typescript
/* ❌ DEPRECATED - Sunset November 30, 2025 */
import { GoogleGenerativeAI } from '@google/generative-ai'
const genAI = new GoogleGenerativeAI(apiKey)
const model = genAI.getGenerativeModel({ model: 'gemini-pro' })

/* ✅ CURRENT SDK */
import { GoogleGenAI } from '@google/genai'
const ai = new GoogleGenAI({ apiKey })
const response = await ai.models.generateContent({
  model: 'gemini-2.5-flash',
  contents: 'Hello',
})
```

## Context Window Correction

```typescript
/* ❌ Common misconception */
// "Gemini 2.5 has 2M token context"

/* ✅ Actual limits */
// Gemini 2.5 Pro/Flash: 1,048,576 input tokens (NOT 2M!)
// Gemini 1.5 Pro had 2M - this was reduced in 2.5
// Output limit: 65,536 tokens (all 2.5 models)
```

## Thinking Is Always Enabled (2.5)

```typescript
/* ❌ Trying to disable thinking */
const response = await ai.models.generateContent({
  model: 'gemini-2.5-flash',
  contents: 'Hello',
  thinkingConfig: { enabled: false }, // Not possible!
})

/* ✅ Thinking is always on for 2.5 models */
// Can only adjust budget/level, not disable
const response = await ai.models.generateContent({
  model: 'gemini-2.5-flash',
  contents: 'Hello',
  thinkingConfig: { thinkingBudget: 1024 }, // Adjust, not disable
})
```

## Context Caching Requires Explicit Version

```typescript
/* ❌ Will fail for caching */
const cache = await ai.caches.create({
  model: 'gemini-2.5-flash', // Generic name
  contents: [...],
})

/* ✅ Use explicit version for caching */
const cache = await ai.caches.create({
  model: 'gemini-2.5-flash-001', // Explicit version required
  contents: [...],
})
```

## Current Model Names (2025)

```typescript
/* ❌ Old/incorrect names */
'gemini-pro'           // Old
'gemini-1.5-pro'       // Use 2.5 instead

/* ✅ Current models */
'gemini-3-pro-preview' // Latest (Nov 2025 preview)
'gemini-2.5-pro'       // Stable
'gemini-2.5-flash'     // Fast
'gemini-2.5-flash-lite' // Lightweight
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `@google/generative-ai` | `@google/genai` |
| `GoogleGenerativeAI` class | `GoogleGenAI` class |
| 2M context window | 1,048,576 tokens (Gemini 2.5) |
| Disabling thinking | Adjust `thinkingBudget` instead |
| `gemini-pro` | `gemini-2.5-pro` or `gemini-2.5-flash` |
| Generic model for caching | Explicit version (e.g., `gemini-2.5-flash-001`) |
| `genai.getGenerativeModel()` | `ai.models.generateContent()` |

## Image Generation Models

| Model ID | Codename | Use For |
|----------|----------|---------|
| `gemini-2.0-flash-exp-image-generation` | Nano Banana | Fast, 1024px |
| `gemini-2.5-flash-preview-image-generation` | Nano Banana | Fast iteration |
| `gemini-2.5-pro-preview-image-generation` | Nano Banana Pro | 4K, complex, text |

## NEVER

- Never use `@google/generative-ai` package
- Never use `GoogleGenerativeAI` class
- Never use `.getGenerativeModel()` pattern
- These are all deprecated patterns from the old SDK
