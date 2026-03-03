---
paths: "**/*.ts", wrangler.jsonc, wrangler.toml
---

# Cloudflare R2 Corrections

## Always Set Content-Type

```typescript
/* ❌ Files download as binary */
await env.BUCKET.put('image.jpg', imageData)

/* ✅ Set httpMetadata.contentType */
await env.BUCKET.put('image.jpg', imageData, {
  httpMetadata: { contentType: 'image/jpeg' },
})
```

## Multipart Upload Limits

```typescript
/* ❌ Part too small or too large */
// Parts < 5MB or > 100MB will fail

/* ✅ Keep parts between 5MB and 100MB */
const PART_SIZE = 10 * 1024 * 1024 // 10MB recommended
```

## Presigned URLs: Never Expose Keys

```typescript
/* ❌ Keys in frontend */
const s3 = new S3Client({
  credentials: { accessKeyId, secretAccessKey }, // In browser!
})

/* ✅ Generate presigned URLs server-side only */
// Worker generates URL, sends to client
const presignedUrl = await generatePresignedUrl(key, { expiresIn: 3600 })
return new Response(JSON.stringify({ uploadUrl: presignedUrl }))
```

## Batch Delete Limit

```typescript
/* ❌ More than 1000 keys */
await env.BUCKET.delete(arrayOf2000Keys)

/* ✅ Chunk into batches of 1000 */
for (const batch of chunks(keys, 1000)) {
  await env.BUCKET.delete(batch)
}
```

## Use head() for Metadata

```typescript
/* ❌ Downloads entire object */
const obj = await env.BUCKET.get(key)
const size = obj?.size

/* ✅ Use head() to get metadata without body */
const head = await env.BUCKET.head(key)
const size = head?.size
```

## Conditional Operations

```typescript
/* ✅ Prevent accidental overwrites */
await env.BUCKET.put(key, data, {
  onlyIf: { etagDoesNotMatch: '*' }, // Only if doesn't exist
})
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Missing `contentType` | Set `httpMetadata.contentType` |
| Part size outside 5-100MB | Use 10MB chunks |
| Credentials in browser | Generate presigned URLs server-side |
| Deleting >1000 keys | Batch into chunks of 1000 |
| `get()` for metadata only | Use `head()` |
