---
globs: ["**/*.ts", "**/*vector*.ts", "wrangler.jsonc"]
---

# Cloudflare Vectorize Corrections

## V2: Mutations Are Now Async

```typescript
/* ❌ Expecting synchronous insert */
await env.VECTORIZE.insert([{ id: '1', values: [...] }])
// Assuming it's immediately queryable...

/* ✅ Mutations return mutationId, are async */
const { mutationId } = await env.VECTORIZE.insert([
  { id: '1', values: [...], metadata: { title: 'Doc' } }
])
// May take a moment to be queryable
```

## returnMetadata is Now Enum

```typescript
/* ❌ Old boolean syntax */
const results = await env.VECTORIZE.query(vector, {
  returnMetadata: true, // Error!
})

/* ✅ New enum syntax */
const results = await env.VECTORIZE.query(vector, {
  returnMetadata: 'all', // 'all' | 'indexed' | 'none'
})
```

## Create Metadata Indexes BEFORE Inserting

```typescript
/* ❌ Vectors added before index won't be filterable */
await env.VECTORIZE.insert([{ id: '1', values, metadata: { category: 'A' } }])
// Then creating index... too late!

/* ✅ Create index first, then insert */
// 1. Create index in dashboard or wrangler
// 2. Then insert vectors
await env.VECTORIZE.insert([{ id: '1', values, metadata: { category: 'A' } }])
// Now filtering works
```

**Symptoms of missing index**:
- Query returns 0 matches despite vectors existing
- Same query without filter returns results
- No error thrown

**Key insight**: Creating the index doesn't retroactively index existing vectors. You must re-embed/re-insert vectors after creating the index.

## Metadata Index Types

| Type | Use for |
|------|---------|
| `string` | Text fields, IDs, categories |
| `number` | Integers, scores, timestamps |
| `boolean` | True/false flags |

```bash
# Create metadata index
npx wrangler vectorize create-metadata-index my-index --property-name=type --type=string
npx wrangler vectorize create-metadata-index my-index --property-name=score --type=number
```

## Match Embedding Dimensions

```typescript
/* ❌ Dimension mismatch */
// Index: 768 dimensions
// Embedding: 1536 dimensions (OpenAI default)

/* ✅ Match dimensions exactly */
// BGE-base: 768 dimensions
// OpenAI text-embedding-3-small: 1536 dimensions
// OpenAI text-embedding-3-large: 3072 dimensions

// Create index matching your embedding model:
// wrangler vectorize create my-index --dimensions=768 --metric=cosine
```

## Filter Size Limit

```typescript
/* ❌ Filter exceeds 2048 bytes */
const results = await env.VECTORIZE.query(vector, {
  filter: { tags: veryLongArrayOfTags }, // May exceed limit
})

/* ✅ Simplify filters */
const results = await env.VECTORIZE.query(vector, {
  filter: { category: 'tech' }, // Keep filters simple
})
```

## V1 Deprecation

```typescript
/* ⚠️ Cannot create new V1 indexes after December 2024 */
// Migrate existing V1 indexes to V2
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Synchronous mutations | Handle async with `mutationId` |
| `returnMetadata: true` | `returnMetadata: 'all'` |
| Index after insert | Create metadata indexes BEFORE inserting |
| Mismatched dimensions | Match embedding model to index dimensions |
| Complex filters | Keep filters under 2048 bytes |
