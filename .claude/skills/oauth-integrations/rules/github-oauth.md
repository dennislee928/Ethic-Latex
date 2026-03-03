---
globs: ["**/*github*", "**/oauth/**/*.ts", "**/auth/**/*.ts", "**/callback*.ts"]
---

# GitHub API & OAuth

GitHub API has strict requirements that differ from Google/Microsoft.

## Required Headers

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Fetch without User-Agent | `'User-Agent': 'AppName/1.0'` (REQUIRED - 403 without) |
| No Accept header | `'Accept': 'application/vnd.github+json'` |

```typescript
const resp = await fetch('https://api.github.com/user', {
  headers: {
    Authorization: `Bearer ${accessToken}`,
    'User-Agent': 'MyApp/1.0',
    'Accept': 'application/vnd.github+json',
  },
});
```

## Private Email Handling

GitHub users can set email to private (`/user` returns `email: null`).

```typescript
if (!userData.email) {
  const emails = await fetch('https://api.github.com/user/emails', { headers }).then(r => r.json());
  userData.email = emails.find(e => e.primary && e.verified)?.email;
}
```

Requires `user:email` scope.

## OAuth Specifics

| Issue | Solution |
|-------|----------|
| Callback URL | Must be EXACT - no wildcards, no subdirectory matching |
| Token exchange returns form-encoded | Add `'Accept': 'application/json'` header |
| Tokens don't expire | No refresh flow needed, but revoked = full re-auth |

## Token Exchange

```typescript
const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
  },
  body: new URLSearchParams({ code, client_id, client_secret, redirect_uri }),
});
```
