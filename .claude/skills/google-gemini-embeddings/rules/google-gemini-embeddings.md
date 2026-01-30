---
paths: "**/*embed*.ts", "**/*vector*.ts", "**/*.ts"
---

# Google Gemini Embeddings Corrections

Claude's training may miss task type requirements.

## Task Type REQUIRED for Quality

```typescript
/* ❌ Missing task type (10-30% quality loss) */
const result = await ai.models.embedContent({
  model: 'gemini-embedding-001',
  content: 'Hello world',
})

/* ✅ Always specify task type */
const result = await ai.models.embedContent({
  model: 'gemini-embedding-001',
  content: 'Hello world',
  taskType: 'RETRIEVAL_DOCUMENT', // Required!
})
```

## RAG: Different Task Types for Query vs Document

```typescript
/* ❌ Same task type for both (breaks retrieval) */
// Indexing documents
embed(doc, { taskType: 'RETRIEVAL_QUERY' }) // Wrong!

// Querying
embed(query, { taskType: 'RETRIEVAL_QUERY' })

/* ✅ Use RETRIEVAL_DOCUMENT for docs, RETRIEVAL_QUERY for queries */
// Indexing documents
embed(doc, { taskType: 'RETRIEVAL_DOCUMENT' })

// Querying
embed(query, { taskType: 'RETRIEVAL_QUERY' })
```

## Available Task Types

```typescript
// Choose based on use case:
'RETRIEVAL_QUERY'      // User search queries
'RETRIEVAL_DOCUMENT'   // Documents being indexed
'SEMANTIC_SIMILARITY'  // Comparing text similarity
'CLUSTERING'           // Grouping similar items
'CLASSIFICATION'       // Categorizing text
'CODE_RETRIEVAL_QUERY' // Code search queries
'QUESTION_ANSWERING'   // Q&A systems
'FACT_VERIFICATION'    // Fact checking
```

## Dimension Matching

```typescript
/* ❌ Dimension mismatch with vector store */
// Vectorize index: 768 dimensions
// Embedding: default 3072 dimensions

/* ✅ Match dimensions to your vector store */
const result = await ai.models.embedContent({
  model: 'gemini-embedding-001',
  content: 'Hello',
  taskType: 'RETRIEVAL_DOCUMENT',
  outputDimensionality: 768, // Match your index!
})

// Recommended dimensions:
// 768  - Fast, good for most use cases
// 1536 - Balance of speed and quality
// 3072 - Maximum quality (default)
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Missing `taskType` | Always specify task type |
| Same task type for query & doc | `RETRIEVAL_QUERY` for queries, `RETRIEVAL_DOCUMENT` for docs |
| Default dimensions | Match `outputDimensionality` to your vector index |
| `text-embedding-*` model | `gemini-embedding-001` |
