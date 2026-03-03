# MCP OAuth Flow Reference

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MCP OAuth Flow                                   │
└─────────────────────────────────────────────────────────────────────────────┘

User (Claude.ai)              Worker                 Google              KV
     │                           │                      │                 │
     │  1. Add MCP Server        │                      │                 │
     │──────────────────────────>│                      │                 │
     │                           │                      │                 │
     │  2. POST /register (DCR)  │                      │                 │
     │──────────────────────────>│                      │                 │
     │  ◄─ client_id, secret ────│                      │                 │
     │                           │                      │                 │
     │  3. GET /authorize        │                      │                 │
     │──────────────────────────>│                      │                 │
     │                           │                      │                 │
     │                           │ [Check approved clients cookie]        │
     │                           │                      │                 │
     │  ◄─ Show approval dialog ─│ (if not approved)   │                 │
     │                           │                      │                 │
     │  4. POST /authorize       │                      │                 │
     │  (CSRF token + approval)  │                      │                 │
     │──────────────────────────>│                      │                 │
     │                           │                      │                 │
     │                           │─── Create state ────────────────────>│
     │                           │  oauth:state:{uuid}                   │
     │                           │                      │                 │
     │  ◄─ Redirect to Google ───│                      │                 │
     │     + state + cookies     │                      │                 │
     │                           │                      │                 │
     │  5. Google Sign-In        │                      │                 │
     │──────────────────────────────────────────────────>│                │
     │  ◄─────────────────────────────────────────────────│                │
     │     (consent, code)       │                      │                 │
     │                           │                      │                 │
     │  6. GET /callback?code=   │                      │                 │
     │──────────────────────────>│                      │                 │
     │                           │                      │                 │
     │                           │◄── Validate state ──────────────────│
     │                           │    + delete (one-time)               │
     │                           │                      │                 │
     │                           │── Token exchange ───>│                 │
     │                           │◄─ access_token ──────│                 │
     │                           │                      │                 │
     │                           │── Get user info ────>│                 │
     │                           │◄─ email, name, id ───│                 │
     │                           │                      │                 │
     │                           │ [completeAuthorization]                │
     │                           │ (props encrypted in token)             │
     │                           │                      │                 │
     │  ◄─ Redirect to Claude ───│                      │                 │
     │     (MCP session token)   │                      │                 │
     │                           │                      │                 │
     │  7. Call /mcp endpoint    │                      │                 │
     │──────────────────────────>│                      │                 │
     │                           │                      │                 │
     │                           │ [Token verified, props decrypted]      │
     │                           │ this.props.email available             │
     │                           │                      │                 │
     │  ◄─ Tool results ─────────│                      │                 │
     │                           │                      │                 │
```

## Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/register` | POST | Dynamic Client Registration (DCR) |
| `/authorize` | GET | Show approval dialog |
| `/authorize` | POST | Process approval form |
| `/callback` | GET | Handle Google OAuth callback |
| `/token` | POST | Token exchange/refresh |
| `/mcp` | POST | MCP tool calls (Streamable HTTP) |
| `/sse` | GET | MCP tool calls (SSE, legacy) |
| `/.well-known/oauth-authorization-server` | GET | OAuth discovery |

## Security Cookies

| Cookie Name | Purpose | TTL |
|-------------|---------|-----|
| `__Host-CSRF_TOKEN` | CSRF protection | 10 min |
| `__Host-CONSENTED_STATE` | Session binding | 10 min |
| `__Host-APPROVED_CLIENTS` | Skip consent | 30 days |

## State Storage

**KV Key Pattern:** `oauth:state:{uuid}`

**Value:** Serialized `AuthRequest` from OAuthProvider

**TTL:** 600 seconds (10 minutes)

**Lifecycle:**
1. Created in POST /authorize (after approval)
2. Validated in GET /callback
3. Deleted after validation (one-time use)

## Props Available in Tools

```typescript
this.props = {
  id: string;        // Google user ID (unique identifier)
  email: string;     // User's email address
  name: string;      // User's display name
  picture?: string;  // Profile picture URL (optional)
  accessToken: string; // Google access token (for Google API calls)
}
```

## Google OAuth URLs

| URL | Purpose |
|-----|---------|
| `https://accounts.google.com/o/oauth2/v2/auth` | Authorization |
| `https://oauth2.googleapis.com/token` | Token exchange |
| `https://www.googleapis.com/oauth2/v2/userinfo` | User info |

## OAuth Scopes

Default scopes requested:
- `openid` - OpenID Connect
- `email` - User's email address
- `profile` - User's name and picture

## Error Codes

| Code | Description |
|------|-------------|
| `invalid_request` | Missing/invalid parameters |
| `invalid_client` | Client not registered |
| `invalid_grant` | Code expired or invalid |
| `server_error` | Internal server error |

## Troubleshooting

### "Invalid or expired state"
- State expired (>10 min)
- State already used
- KV binding not configured

### "CSRF token mismatch"
- Cookies blocked by browser
- Form submitted from different origin
- Cookie expired (>10 min)

### "Missing session binding cookie"
- User cleared cookies mid-flow
- SameSite restrictions blocked cookie
- Flow restarted in different browser/tab

### "Failed to fetch user info"
- Google access token invalid
- Network error to Google API
- Google API rate limited
