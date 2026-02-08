# {{PROJECT_NAME}}

**Last Updated**: {{DATE}}

---

## Project Overview

{{DESCRIPTION}}

**Tech Stack**: Cloudflare Workers, {{TECH_STACK}}

---

## Quick Start

```bash
# Install dependencies
pnpm install

# Start dev server
pnpm dev

# Deploy to Cloudflare
pnpm deploy
```

---

## Development

### Local Development

```bash
pnpm dev              # Start Vite + Workers dev server
```

The dev server runs at `http://localhost:5173` (or next available port).

### Build & Deploy

```bash
pnpm build            # Build for production
pnpm deploy           # Deploy to Cloudflare Workers
```

### Database (D1)

```bash
# Generate migration from schema changes
pnpm drizzle-kit generate

# Apply migrations locally
pnpm wrangler d1 execute {{DB_NAME}} --local --file=drizzle/XXXX_migration.sql

# Apply migrations to production
pnpm wrangler d1 execute {{DB_NAME}} --remote --file=drizzle/XXXX_migration.sql
```

**Important**: Always run migrations on BOTH local AND remote before testing.

---

## Project Structure

```
src/
├── client/           # React frontend
│   ├── components/   # UI components
│   ├── pages/        # Page components
│   └── main.tsx      # Client entry
├── server/           # Cloudflare Worker backend
│   ├── routes/       # API routes
│   ├── middleware/   # Hono middleware
│   └── index.ts      # Worker entry
└── shared/           # Shared types and utilities
```

---

## Environment Variables

### Local Development (.dev.vars)

```bash
# Database is auto-created by wrangler
# Add any API keys here
```

### Production (Cloudflare Secrets)

```bash
# Set secrets with wrangler
echo "value" | pnpm wrangler secret put SECRET_NAME
pnpm deploy  # Redeploy to activate secrets
```

---

## Key Files

| File | Purpose |
|------|---------|
| `wrangler.jsonc` | Cloudflare Workers configuration |
| `src/server/index.ts` | Worker entry point |
| `src/client/main.tsx` | React app entry |
| `drizzle/schema.ts` | Database schema |
| `drizzle.config.ts` | Drizzle Kit configuration |

---

## Common Tasks

### Add a New API Route

1. Create route file in `src/server/routes/`
2. Register route in `src/server/index.ts`
3. Add types to `src/shared/types.ts` if needed

### Add a New Page

1. Create component in `src/client/pages/`
2. Add route in `src/client/App.tsx`

### Modify Database Schema

1. Edit `drizzle/schema.ts`
2. Generate migration: `pnpm drizzle-kit generate`
3. Apply locally: `pnpm wrangler d1 execute ...`
4. Test, then apply to production

---

## Cloudflare Bindings

Configured in `wrangler.jsonc`:

```jsonc
{
  "d1_databases": [...],
  "kv_namespaces": [...],
  "r2_buckets": [...],
  // Add other bindings as needed
}
```

Access in Worker:

```typescript
export default {
  async fetch(request: Request, env: Env) {
    const db = env.DB;        // D1 database
    const kv = env.KV;        // KV namespace
    const bucket = env.R2;    // R2 bucket
  }
}
```

---

## Troubleshooting

### "Table not found" errors
Run migrations on remote: `pnpm wrangler d1 execute {{DB_NAME}} --remote --file=...`

### Changes not appearing after deploy
1. Rebuild: `pnpm build`
2. Redeploy: `pnpm deploy`
3. Hard refresh browser: Ctrl+Shift+R

### Secrets not working
Secrets require redeploy to take effect: `pnpm deploy`
