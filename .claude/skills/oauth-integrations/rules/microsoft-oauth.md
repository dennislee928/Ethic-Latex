---
globs: ["**/oauth*.ts", "**/auth*.ts", "**/microsoft*.ts", "**/azure*.ts", "**/entra*.ts", "**/callback*.ts"]
---

# Microsoft OAuth in Cloudflare Workers

Patterns for implementing Microsoft Entra (Azure AD) OAuth in Cloudflare Workers without MSAL.

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Using MSAL.js in Workers | Manual OAuth + jose for JWT validation |
| Scope `openid email profile` for user info | Add `User.Read` scope |
| Fetching email from token claims only | Use Microsoft Graph `/me` endpoint |

## Why MSAL Doesn't Work in Workers

MSAL.js depends on:
- Browser APIs (localStorage, sessionStorage, DOM)
- Node.js crypto module

Cloudflare's V8 isolate runtime has neither. The workaround is simpler and more secure:
1. Manual OAuth URL construction
2. Direct token exchange via fetch
3. JWT validation with `jose` library

## Required Scopes

```typescript
// For user identity (email, name, profile picture)
const scope = 'openid email profile User.Read';

// For refresh tokens (long-lived sessions)
const scope = 'openid email profile User.Read offline_access';
```

**Critical**: `User.Read` is required for Microsoft Graph `/me` endpoint. Without it, token exchange succeeds but user info fetch returns 403.

## User Info Endpoint

```typescript
// Microsoft Graph /me endpoint
const resp = await fetch('https://graph.microsoft.com/v1.0/me', {
  headers: { Authorization: `Bearer ${accessToken}` },
});

// Email may be in different fields
const email = data.mail || data.userPrincipalName;
```

## Tenant Configuration

| Tenant Value | Who Can Sign In |
|--------------|-----------------|
| `common` | Any Microsoft account (personal + work) |
| `organizations` | Work/school accounts only |
| `consumers` | Personal Microsoft accounts only |
| `{tenant-id}` | Specific organization only |

## Azure Portal Setup

1. App Registration → New registration
2. Platform: **Web** (not SPA) for server-side OAuth
3. Redirect URIs: Add both `/callback` and `/admin/callback`
4. Certificates & secrets → New client secret

## Token Lifetimes

| Token Type | Default Lifetime | Notes |
|------------|------------------|-------|
| Access token | 60-90 minutes | Configurable via token lifetime policies |
| Refresh token | 90 days | Revoked on password change, can be extended |
| ID token | 60 minutes | Same as access token |

**Best Practice**: Always request `offline_access` scope and implement refresh token flow for sessions longer than 1 hour.

📚 **Source**: https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens#token-lifetime

## Reference

- Graph API permissions: https://learn.microsoft.com/en-us/graph/permissions-reference
- AADSTS error codes: https://learn.microsoft.com/en-us/entra/identity-platform/reference-error-codes
