# MCP OAuth Cloudflare Skill

OAuth authentication for MCP servers on Cloudflare Workers.

## Auto-Trigger Keywords

This skill activates when discussing:

- "mcp oauth"
- "mcp authentication"
- "mcp server auth"
- "oauth mcp server"
- "cloudflare mcp oauth"
- "workers-oauth-provider"
- "dynamic client registration"
- "DCR mcp"
- "claude.ai mcp authentication"
- "google oauth mcp"
- "mcp user authentication"
- "replace auth tokens mcp"
- "oauth instead of tokens"

## What This Skill Provides

1. **Complete OAuth flow** for MCP servers
2. **Security utilities** (CSRF, state validation, session binding)
3. **Beautiful approval dialog** (dark mode, branded)
4. **Google OAuth integration** (token exchange, user info)
5. **Claude.ai compatibility** (DCR support)

## Quick Usage

```bash
# Tell Claude:
"Add OAuth authentication to my MCP server on Cloudflare"

# Or:
"Set up Google Sign-In for my MCP server"

# Or:
"Replace auth tokens with OAuth for my MCP"
```

## Files Included

```
mcp-oauth-cloudflare/
├── SKILL.md                    # Full documentation
├── README.md                   # This file
├── templates/
│   └── oauth/
│       ├── google-handler.ts   # OAuth routes
│       ├── utils.ts            # Google OAuth utilities
│       └── workers-oauth-utils.ts # Security utilities
├── rules/
│   └── mcp-oauth.md            # Common mistakes
└── references/
    └── oauth-flow.md           # Flow diagrams
```

## Key Dependencies

```json
{
  "@cloudflare/workers-oauth-provider": "^0.2.2",
  "agents": "^0.3.3",
  "@modelcontextprotocol/sdk": "^1.25.1",
  "hono": "^4.11.3",
  "zod": "^3.24.2"
}
```

**v0.2.0+ Features:**
- Refresh token support for long-lived sessions
- Bearer token + OAuth coexistence for CLI tools
- Improved state validation

## Why OAuth Over Auth Tokens?

| Auth Tokens | OAuth |
|-------------|-------|
| Manual sharing | Automatic flow |
| No user consent | Explicit approval |
| No expiration | Auto-refresh |
| All-or-nothing | Scoped access |
| No Claude.ai DCR | Full compatibility |

## License

MIT
