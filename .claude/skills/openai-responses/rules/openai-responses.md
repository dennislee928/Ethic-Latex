---
paths: "**/*.ts", "**/*.tsx", "**/*openai*.ts"
---

# OpenAI Responses API Corrections

Claude's training may reference Chat Completions. This project uses **Responses API**.

## Key Differences from Chat Completions

```typescript
/* ❌ Chat Completions pattern */
const response = await openai.chat.completions.create({
  model: 'gpt-5',
  messages: [{ role: 'system', content: '...' }, { role: 'user', content: '...' }],
})
const text = response.choices[0].message.content

/* ✅ Responses API pattern */
const response = await openai.responses.create({
  model: 'gpt-5',
  input: 'Hello',
  instructions: '...', // replaces system message
})
const text = response.output_text // helper property
```

## System Role → Developer Role

```typescript
/* ❌ Chat Completions system role */
messages: [{ role: 'system', content: 'You are helpful' }]

/* ✅ Responses API uses 'developer' or instructions */
instructions: 'You are helpful'
// OR in input array:
input: [{ role: 'developer', content: 'You are helpful' }]
```

## Stateful Conversations

```typescript
/* ❌ Managing history manually */
const messages = [...history, newMessage]

/* ✅ Use conversation_id for automatic state */
// First message
const response = await openai.responses.create({
  model: 'gpt-5',
  input: 'Hello',
})
const conversationId = response.conversation_id

// Subsequent messages - history managed automatically
const response2 = await openai.responses.create({
  model: 'gpt-5',
  input: 'Follow up question',
  conversation_id: conversationId, // Preserves context
})
```

## Conversation Expiration

```typescript
/* ⚠️ Conversations expire after 90 days */
// Verify conversation exists before using
try {
  const response = await openai.responses.create({
    model: 'gpt-5',
    input: 'Hello',
    conversation_id: oldConversationId,
  })
} catch (error) {
  // Conversation expired - start new one
  const response = await openai.responses.create({
    model: 'gpt-5',
    input: 'Hello',
  })
}
```

## Cost Tracking

```typescript
/* ⚠️ Responses API has additional costs */
// Cost = input + output + tools + stored conversations

/* Disable storage if not needed */
const response = await openai.responses.create({
  model: 'gpt-5',
  input: 'Hello',
  store: false, // Don't persist conversation
})
```

## Quick Fixes

| Chat Completions | Responses API |
|-----------------|---------------|
| `/v1/chat/completions` | `/v1/responses` |
| `messages` | `input` |
| `role: 'system'` | `role: 'developer'` or `instructions` |
| `choices[0].message.content` | `output_text` |
| Manual history | `conversation_id` |
