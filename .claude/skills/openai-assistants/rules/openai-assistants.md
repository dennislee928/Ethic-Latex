---
paths: "**/*assistant*.ts", "**/*.ts"
---

# OpenAI Assistants API - DEPRECATED

**⚠️ SUNSET H1 2026** - Use `openai-responses` skill for new projects.

## Migration Required

```typescript
/* ❌ Assistants API (deprecated) */
const assistant = await openai.beta.assistants.create({...})
const thread = await openai.beta.threads.create()
const run = await openai.beta.threads.runs.create(thread.id, {...})

/* ✅ Use Responses API instead */
const response = await openai.responses.create({
  model: 'gpt-5',
  input: 'Hello',
  conversation_id: existingConversationId, // Optional: for stateful
})
```

## If Maintaining Existing Code

### Thread Already Has Active Run

```typescript
/* ❌ Will fail if run already active */
await openai.beta.threads.runs.create(threadId, { assistant_id })

/* ✅ Cancel existing run first */
const runs = await openai.beta.threads.runs.list(threadId)
const activeRun = runs.data.find(r => r.status === 'in_progress')
if (activeRun) {
  await openai.beta.threads.runs.cancel(threadId, activeRun.id)
}
await openai.beta.threads.runs.create(threadId, { assistant_id })
```

### Vector Store Must Be Ready

```typescript
/* ❌ Using vector store before ready */
const vectorStore = await openai.beta.vectorStores.create({...})
// Immediately using...

/* ✅ Poll until completed */
let vs = await openai.beta.vectorStores.create({...})
while (vs.status !== 'completed') {
  await new Promise(r => setTimeout(r, 1000))
  vs = await openai.beta.vectorStores.retrieve(vs.id)
}
```

## v1 → v2 Changes

| v1 | v2 |
|----|-----|
| Max 20 files for file search | Max 10,000 files |
| 32k char instructions | 256k char instructions |
| retrieval tool | file_search tool |

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| New Assistants project | Responses API (`openai-responses` skill) |
| `retrieval` tool | `file_search` tool (v2) |
| No run cancellation | Cancel active runs before creating new |
| Immediate vector store use | Poll until `status: 'completed'` |
