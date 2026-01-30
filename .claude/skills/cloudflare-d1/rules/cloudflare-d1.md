---
paths: "**/*.ts", "**/*.sql", wrangler.jsonc, wrangler.toml
---

# Cloudflare D1 Corrections

## No BEGIN TRANSACTION in Migrations

```sql
/* ❌ Will cause conflicts */
BEGIN TRANSACTION;
CREATE TABLE users (...);
COMMIT;

/* ✅ D1 handles transactions automatically */
CREATE TABLE users (...);
```

## Use null, Not undefined

```typescript
/* ❌ Causes D1_TYPE_ERROR */
await db.prepare('INSERT INTO users (name, bio) VALUES (?, ?)')
  .bind('John', undefined)
  .run()

/* ✅ Use null for optional values */
await db.prepare('INSERT INTO users (name, bio) VALUES (?, ?)')
  .bind('John', null)
  .run()
```

## Always Use .prepare().bind()

```typescript
/* ❌ SQL injection vulnerability */
await db.exec(`SELECT * FROM users WHERE id = ${userId}`)

/* ✅ Use prepared statements */
await db.prepare('SELECT * FROM users WHERE id = ?')
  .bind(userId)
  .first()
```

## Batch Large Inserts

```typescript
/* ❌ Statement too long (>128KB) */
await db.exec(`INSERT INTO items VALUES ${thousands_of_rows}`)

/* ✅ Batch into 100-250 rows */
for (const batch of chunks(rows, 100)) {
  await db.batch(
    batch.map(row =>
      db.prepare('INSERT INTO items VALUES (?, ?)').bind(row.a, row.b)
    )
  )
}
```

## Use .batch() for Multiple Queries

```typescript
/* ❌ Multiple round trips */
await db.prepare('SELECT * FROM users').all()
await db.prepare('SELECT * FROM posts').all()

/* ✅ Single round trip */
const [users, posts] = await db.batch([
  db.prepare('SELECT * FROM users'),
  db.prepare('SELECT * FROM posts'),
])
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `BEGIN TRANSACTION` in migrations | Remove it (D1 auto-handles) |
| `undefined` in bind | `null` |
| String interpolation in SQL | `.prepare().bind()` |
| Multiple separate queries | `.batch([...])` |
| Single large INSERT | Chunk into batches of 100-250 |
