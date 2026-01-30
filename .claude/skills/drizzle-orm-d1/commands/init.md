# Init Drizzle + D1

Set up Drizzle ORM with Cloudflare D1 database. Creates schema, migrations directory, and Drizzle config.

---

## Your Task

Follow these steps to add Drizzle ORM to an existing Cloudflare Workers project.

### 1. Check Prerequisites

Verify the project has:
- `wrangler.jsonc` with a D1 binding configured
- TypeScript configured (`tsconfig.json`)

If no D1 binding exists, inform user:
```
Run: npx wrangler d1 create <database-name>
Then add the binding to wrangler.jsonc
```

### 2. Install Dependencies

```bash
npm install drizzle-orm
npm install -D drizzle-kit better-sqlite3 @types/better-sqlite3
```

### 3. Create Directory Structure

```
src/
└── db/
    └── schema.ts
drizzle.config.ts
migrations/
```

### 4. Create Schema File

Create `src/db/schema.ts`:

```typescript
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

// Example users table - customize for your needs
export const users = sqliteTable('users', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  email: text('email').notNull().unique(),
  name: text('name'),
  createdAt: integer('created_at', { mode: 'timestamp' }).$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).$defaultFn(() => new Date()),
});

// Add more tables as needed
```

### 5. Create Drizzle Config

Create `drizzle.config.ts`:

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/db/schema.ts',
  out: './migrations',
  dialect: 'sqlite',
  driver: 'd1-http',
  dbCredentials: {
    accountId: process.env.CLOUDFLARE_ACCOUNT_ID!,
    databaseId: process.env.CLOUDFLARE_DATABASE_ID!,
    token: process.env.CLOUDFLARE_D1_TOKEN!,
  },
});
```

### 6. Update wrangler.jsonc

Ensure D1 binding and migrations directory are configured:

```jsonc
{
  "d1_databases": [{
    "binding": "DB",
    "database_name": "<database-name>",
    "database_id": "<your-database-id>",
    "migrations_dir": "./migrations"
  }]
}
```

### 7. Create Database Helper

Create `src/db/index.ts`:

```typescript
import { drizzle } from 'drizzle-orm/d1';
import * as schema from './schema';

export function createDb(d1: D1Database) {
  return drizzle(d1, { schema });
}

export type Database = ReturnType<typeof createDb>;
export * from './schema';
```

### 8. Add Scripts to package.json

```json
{
  "scripts": {
    "db:generate": "drizzle-kit generate",
    "db:migrate:local": "wrangler d1 migrations apply <database-name> --local",
    "db:migrate:remote": "wrangler d1 migrations apply <database-name> --remote",
    "db:studio": "drizzle-kit studio"
  }
}
```

### 9. Generate Initial Migration

```bash
npm run db:generate
```

### 10. Provide Next Steps

```
✅ Drizzle ORM configured for D1!

📁 Structure:
   - src/db/schema.ts    (Define your tables)
   - src/db/index.ts     (Database helper)
   - drizzle.config.ts   (Drizzle Kit config)
   - migrations/         (SQL migrations)

🚀 Next steps:
   1. Edit src/db/schema.ts to define your tables
   2. npm run db:generate     (Generate migrations)
   3. npm run db:migrate:local (Apply to local)
   4. npm run db:migrate:remote (Apply to production)

💡 Usage in Worker:
   import { createDb } from './db';
   const db = createDb(env.DB);
   const users = await db.select().from(schema.users);

📚 Skill loaded: drizzle-orm-d1
   - 12 common issues auto-prevented
   - Use db.batch([]) for transactions (D1 doesn't support BEGIN)
```

---

## Critical Patterns Applied

1. **Timestamp mode**: Uses `mode: 'timestamp'` with `$defaultFn()` for dates
2. **Batch API**: D1 doesn't support SQL transactions - use `db.batch([])`
3. **Migrations directory**: Points to `./migrations` in wrangler.jsonc
4. **Local-first**: Always test migrations locally before remote
