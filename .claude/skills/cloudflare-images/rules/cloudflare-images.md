---
paths: "**/*.ts", "**/*image*.ts"
---

# Cloudflare Images Corrections

## Direct Creator Upload: Backend Only

```typescript
/* ❌ Calling from browser */
fetch('https://api.cloudflare.com/client/v4/accounts/.../images/v2/direct_upload', {
  headers: { 'Authorization': `Bearer ${apiToken}` } // Exposed!
})

/* ✅ Call from backend, send URL to frontend */
// Backend:
const response = await fetch(
  `https://api.cloudflare.com/client/v4/accounts/${accountId}/images/v2/direct_upload`,
  { method: 'POST', headers: { 'Authorization': `Bearer ${apiToken}` } }
)
const { result } = await response.json()
return Response.json({ uploadURL: result.uploadURL })

// Frontend uses the uploadURL
```

## Use multipart/form-data, Field Named "file"

```typescript
/* ❌ Wrong content type or field name */
const formData = new FormData()
formData.append('image', file) // Wrong field name!

/* ✅ Field MUST be named "file" */
const formData = new FormData()
formData.append('file', file) // Correct!

// Let browser set Content-Type (includes boundary)
await fetch(uploadURL, { method: 'POST', body: formData })
```

## Flexible Variants + Signed URLs Incompatible

```typescript
/* ❌ Cannot use together */
// Flexible variants with requireSignedURLs=true

/* ✅ Use named variants for private images */
// Create named variant in dashboard
// Use: /cdn-cgi/imagedelivery/{hash}/{imageId}/myVariant
```

## AI Face Cropping (August 2025)

```typescript
/* ✅ New gravity=face parameter */
const url = `https://imagedelivery.net/${hash}/${imageId}/w=300,h=300,gravity=face,zoom=1.2`
// GPU-based RetinaFace detection
// zoom: 0.5 (zoomed out) to 2.0 (zoomed in)
```

## Avoid Request Loops

```typescript
/* ❌ Error 9403: request loop */
// Worker fetching its own URL

/* ✅ Use binding directly or external URL */
const image = await env.IMAGES.get(imageId)
// OR fetch from external source
```

## Always Validate Server-Side

```typescript
/* ❌ Trusting client validation */
if (file.type.startsWith('image/')) { /* upload */ }

/* ✅ Validate on server */
const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
const contentType = request.headers.get('content-type')
// Also check file magic bytes if needed
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Direct upload from browser | Backend generates URL, frontend uploads |
| Field name 'image' | Field name 'file' |
| Flexible + signed URLs | Named variants for private images |
| Fetching own Worker URL | Use binding or external URL |
| Client-only validation | Always validate server-side |
