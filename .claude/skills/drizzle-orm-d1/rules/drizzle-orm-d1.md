---
paths: "**/*schema*.ts", "**/*db*.ts", drizzle.config.ts, wrangler.jsonc, wrangler.toml
---

# Drizzle ORM + D1 Corrections

Claude's training may suggest patterns that don't work with Cloudflare D1.

## Critical: No SQL Transactions

```typescript
/* ❌ D1 doesn't support SQL BEGIN/COMMIT */
await db.transaction(async (tx) => {
  await tx.insert(users).values({ ... })
  await tx.insert(posts).values({ ... })
})
// Error: D1_ERROR: Cannot use BEGIN TRANSACTION

/* ✅ Use D1 batch API instead */
await db.batch([
  db.insert(users).values({ email: 'test@example.com' }),
  db.insert(posts).values({ title: 'Post', authorId: 1 }),
])
```

## Migrations: Use Wrangler, Not Drizzle Push

```bash
# ❌ drizzle-kit push doesn't work reliably with D1
npx drizzle-kit push

# ✅ Generate SQL then apply with Wrangler
npx drizzle-kit generate
npx wrangler d1 migrations apply my-database --local   # Test first
npx wrangler d1 migrations apply my-database --remote  # Production
```

## wrangler.jsonc: Set migrations_dir

```jsonc
{
  "d1_databases": [{
    "binding": "DB",
    "database_name": "my-database",
    "database_id": "your-database-id",
    "migrations_dir": "./migrations"  // Points to Drizzle output
  }]
}
```

## Dates: Use Integer with Timestamp Mode

```typescript
/* ❌ D1 has no native DATE type */
createdAt: text('created_at')

/* ✅ Use integer with timestamp mode */
createdAt: integer('created_at', { mode: 'timestamp' }).$defaultFn(() => new Date())
```

## Foreign Keys: Use Cascading

```typescript
/* ❌ May fail during migrations */
authorId: integer('author_id').references(() => users.id)

/* ✅ Add cascading to prevent constraint failures */
authorId: integer('author_id').references(() => users.id, { onDelete: 'cascade' })
```

## Don't Import from Wrangler

```typescript
/* ❌ Fails in production */
import { ... } from 'wrangler'

/* ✅ Use drizzle-orm/d1 */
import { drizzle } from 'drizzle-orm/d1'
const db = drizzle(env.DB)
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `db.transaction()` | `db.batch([...])` |
| `npx drizzle-kit push` | `npx drizzle-kit generate` + `wrangler d1 migrations apply` |
| Missing `migrations_dir` | Add to wrangler.jsonc d1_databases config |
| `text()` for dates | `integer('col', { mode: 'timestamp' })` |
| `.default(new Date())` | `.$defaultFn(() => new Date())` |
| Import from 'wrangler' | Import from 'drizzle-orm/d1' |
| `wrangler.toml` | `wrangler.jsonc` (supports comments) |
