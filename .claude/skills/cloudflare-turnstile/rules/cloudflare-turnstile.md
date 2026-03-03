---
paths: "**/*.ts", "**/*.tsx", "**/*turnstile*.ts"
---

# Cloudflare Turnstile Corrections

## Server-Side Validation MANDATORY

```typescript
/* ❌ SECURITY VULNERABILITY - client-only validation */
// Frontend gets token, sends to your API
// API trusts token without verification

/* ✅ ALWAYS call Siteverify API */
async function verifyTurnstile(token: string, env: Env): Promise<boolean> {
  const response = await fetch(
    'https://challenges.cloudflare.com/turnstile/v0/siteverify',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        secret: env.TURNSTILE_SECRET_KEY,
        response: token,
      }),
    }
  )
  const result = await response.json()
  return result.success === true
}
```

## Siteverify: POST Only, Not GET

```typescript
/* ❌ GET not supported (unlike reCAPTCHA) */
fetch(`https://challenges.cloudflare.com/turnstile/v0/siteverify?secret=...&response=...`)

/* ✅ Must use POST */
fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
  method: 'POST',
  body: new URLSearchParams({ secret, response: token }),
})
```

## Token Expires in 5 Minutes

```typescript
/* ⚠️ Tokens have 300 second TTL */
// User completes challenge
// Token valid for 5 minutes only
// After that, siteverify returns success: false

/* ✅ Verify immediately after form submission */
```

## Never Expose Secret Key

```typescript
/* ❌ Secret in frontend */
const TURNSTILE_SECRET = 'xxx' // In client code!

/* ✅ Secret only in backend environment */
// .dev.vars or wrangler secret
// Access via env.TURNSTILE_SECRET_KEY
```

## Test Keys for Development

```typescript
/* ✅ Dummy keys for testing */
// Site key (always passes): 1x00000000000000000000AA
// Site key (always fails): 2x00000000000000000000AB
// Site key (forces challenge): 3x00000000000000000000FF

// Secret key (always passes): 1x0000000000000000000000000000000AA
// Secret key (always fails): 2x0000000000000000000000000000000AB
```

## CSP Configuration Required

```typescript
/* ✅ Allow Turnstile iframe in CSP */
// frame-src: https://challenges.cloudflare.com
// script-src: https://challenges.cloudflare.com
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Client-only validation | ALWAYS call Siteverify API server-side |
| GET request to Siteverify | POST with URLSearchParams body |
| Secret key in frontend | Keep in backend env only |
| Production keys in dev | Use dummy test keys |
| Missing CSP | Allow challenges.cloudflare.com |
