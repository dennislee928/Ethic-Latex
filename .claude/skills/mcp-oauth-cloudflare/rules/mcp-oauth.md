# MCP OAuth Correction Rules

## Globs
- src/oauth/**/*.ts
- src/index.ts (when contains OAuthProvider)

## Common Mistakes

### 1. Missing KV Binding for OAuth State

**Wrong:**
```jsonc
// wrangler.jsonc without KV
{
  "name": "my-mcp",
  "durable_objects": { ... }
  // No kv_namespaces!
}
```

**Correct:**
```jsonc
{
  "name": "my-mcp",
  "kv_namespaces": [
    {
      "binding": "OAUTH_KV",
      "id": "your-kv-namespace-id"
    }
  ]
}
```

### 2. Forgetting to Deploy After Setting Secrets

**Wrong:**
```bash
# Set secret only
echo "secret" | npx wrangler secret put GOOGLE_CLIENT_ID
# Forget to deploy!
```

**Correct:**
```bash
echo "secret" | npx wrangler secret put GOOGLE_CLIENT_ID
npx wrangler deploy  # Required to activate secrets!
```

### 3. Missing Session Binding Cookie

**Wrong:**
```typescript
// Creating state without binding to session
const { stateToken } = await createOAuthState(oauthReqInfo, kv);
return Response.redirect(googleUrl);  // No session cookie!
```

**Correct:**
```typescript
const { stateToken } = await createOAuthState(oauthReqInfo, c.env.OAUTH_KV);
const { setCookie } = await bindStateToSession(stateToken);  // Bind to session!
return new Response(null, {
  status: 302,
  headers: {
    'Set-Cookie': setCookie,
    'Location': googleUrl,
  },
});
```

### 4. Not Deleting State After Use

**Wrong:**
```typescript
// Validate but don't delete - allows replay attacks!
const storedData = await kv.get(`oauth:state:${state}`);
// Continue without deleting...
```

**Correct:**
```typescript
const storedData = await kv.get(`oauth:state:${state}`);
// ... validate ...
await kv.delete(`oauth:state:${state}`);  // One-time use!
```

### 5. Missing CSRF Token in Approval Form

**Wrong:**
```html
<form method="post" action="/authorize">
  <input type="hidden" name="state" value="${state}">
  <!-- No CSRF token! -->
  <button type="submit">Approve</button>
</form>
```

**Correct:**
```html
<form method="post" action="/authorize">
  <input type="hidden" name="state" value="${state}">
  <input type="hidden" name="csrf_token" value="${csrfToken}">
  <button type="submit">Approve</button>
</form>
```

### 6. Using Regular Cookies Instead of __Host- Prefix

**Wrong:**
```typescript
const setCookie = `CSRF_TOKEN=${token}; HttpOnly; Secure`;  // No prefix!
```

**Correct:**
```typescript
const setCookie = `__Host-CSRF_TOKEN=${token}; HttpOnly; Secure; Path=/; SameSite=Lax`;
// __Host- prefix ensures: Secure, no Domain, Path=/
```

### 7. Accessing this.props Before OAuth Completes

**Wrong:**
```typescript
async init() {
  const email = this.props.email;  // May be undefined!
}
```

**Correct:**
```typescript
async init() {
  if (this.props) {
    const email = this.props.email;  // Safe!
  }
}
```

### 8. Wrong Durable Object Class Name

**Wrong:**
```jsonc
// wrangler.jsonc
"durable_objects": {
  "bindings": [{
    "class_name": "MyMcpServer",  // Name in config
    "name": "MCP_OBJECT"
  }]
}
```

```typescript
// index.ts
export class MyMCPServer extends McpAgent { }  // Different casing!
```

**Correct:**
```typescript
// Names must match exactly
export class MyMcpServer extends McpAgent { }  // Same as wrangler.jsonc
```

### 9. Missing DCR Endpoint

**Wrong:**
```typescript
export default new OAuthProvider({
  apiHandlers: { '/mcp': MyMcpServer.serve('/mcp') },
  authorizeEndpoint: '/authorize',
  tokenEndpoint: '/token',
  // Missing clientRegistrationEndpoint!
});
```

**Correct:**
```typescript
export default new OAuthProvider({
  apiHandlers: { '/mcp': MyMcpServer.serve('/mcp') },
  authorizeEndpoint: '/authorize',
  clientRegistrationEndpoint: '/register',  // Required for Claude.ai!
  tokenEndpoint: '/token',
});
```

### 10. Hardcoding Callback URL

**Wrong:**
```typescript
redirect_uri: 'https://my-worker.workers.dev/callback',  // Breaks in dev!
```

**Correct:**
```typescript
redirect_uri: new URL('/callback', request.url).href,  // Works everywhere!
```

## Required Secrets Checklist

- [ ] `GOOGLE_CLIENT_ID` - From Google Cloud Console
- [ ] `GOOGLE_CLIENT_SECRET` - From Google Cloud Console
- [ ] `COOKIE_ENCRYPTION_KEY` - Generate: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

## Google Cloud Console Setup

1. APIs & Services → Credentials → Create OAuth client ID
2. Application type: Web application
3. Authorized redirect URI: `https://your-worker.workers.dev/callback`
4. Copy Client ID and Client Secret
