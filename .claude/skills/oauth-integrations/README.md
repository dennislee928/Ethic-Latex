# OAuth Integrations Skill

Implement OAuth 2.0 authentication with GitHub and Microsoft Entra (Azure AD) in Cloudflare Workers and other edge environments.

## Auto-Trigger Keywords

This skill should be automatically loaded when discussions involve:

- "GitHub OAuth", "GitHub authentication", "GitHub API"
- "Microsoft OAuth", "Azure AD", "Entra ID", "MSAL"
- "OAuth callback", "token exchange"
- "User-Agent header", "403 forbidden" (GitHub context)
- "User.Read scope", "Microsoft Graph"
- "github.com/login/oauth", "login.microsoftonline.com"
- "AADSTS", "AADSTS50058", "AADSTS700084"
- "private email", "/user/emails"
- "jose", "JWT validation"

## What This Skill Covers

1. **GitHub OAuth** - Required headers, private email handling, token exchange
2. **Microsoft Entra** - Manual OAuth without MSAL, required scopes, tenant config
3. **Edge Runtime** - Patterns for Cloudflare Workers without browser/Node APIs
4. **Error Handling** - Provider-specific error codes and fixes

## Quick Start

### GitHub OAuth

```typescript
// Always include User-Agent!
const resp = await fetch('https://api.github.com/user', {
  headers: {
    Authorization: `Bearer ${accessToken}`,
    'User-Agent': 'MyApp/1.0',
    'Accept': 'application/vnd.github+json',
  },
});
```

### Microsoft OAuth

```typescript
// Always include User.Read scope!
const scope = 'openid email profile User.Read offline_access';

// Use Graph API for user info
const resp = await fetch('https://graph.microsoft.com/v1.0/me', {
  headers: { Authorization: `Bearer ${accessToken}` },
});
```

## Related Skills

- `cloudflare-worker-base` - Edge runtime setup
- `clerk-auth` - Managed auth alternative
- `better-auth` - Self-hosted auth library

## Version History

- **v1.0.0** (2025-01-18): Initial release with GitHub and Microsoft OAuth patterns
