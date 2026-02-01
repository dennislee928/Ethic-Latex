# Init Cloudflare Worker

Initialize a new Cloudflare Workers project with Hono routing, Vite plugin, and Static Assets. Uses production-tested templates that prevent 8 common issues.

---

## Your Task

Follow these steps to scaffold a new Cloudflare Workers project.

### 1. Gather Project Details

Ask the user for:
- **Project name** (will be used for directory and worker name)
- **Account ID** (optional - can use default from wrangler config)
- **Features needed** (D1 database, R2 storage, KV, etc.)

If user doesn't specify, use sensible defaults:
- Project name: "my-worker"
- Features: None (just base Hono + Static Assets)

### 2. Scaffold Project Structure

Create the following directory structure:

```
{project-name}/
├── src/
│   └── index.ts
├── public/
│   └── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── wrangler.jsonc
└── .gitignore
```

**Use templates from**: `~/.claude/skills/cloudflare-worker-base/templates/`

Copy and customize these files:
- `templates/package.json` → Update `name` field
- `templates/tsconfig.json` → Copy as-is
- `templates/vite.config.ts` → Copy as-is
- `templates/wrangler.jsonc` → Update `name`, optionally add bindings
- `templates/src/index.ts` → Copy as-is (or customize for features)
- `templates/public/index.html` → Copy as-is

### 3. Add Bindings (If Requested)

If user requested D1, R2, KV, or other bindings, add them to `wrangler.jsonc`:

**D1 Database**:
```jsonc
"d1_databases": [{
  "binding": "DB",
  "database_name": "{project-name}-db",
  "database_id": "to-be-created"
}]
```
Tell user: "Run `npx wrangler d1 create {project-name}-db` and update the database_id"

**R2 Bucket**:
```jsonc
"r2_buckets": [{
  "binding": "BUCKET",
  "bucket_name": "{project-name}-bucket"
}]
```
Tell user: "Run `npx wrangler r2 bucket create {project-name}-bucket`"

**KV Namespace**:
```jsonc
"kv_namespaces": [{
  "binding": "KV",
  "id": "to-be-created"
}]
```
Tell user: "Run `npx wrangler kv namespace create KV` and update the id"

### 4. Create .gitignore

```
node_modules/
.wrangler/
dist/
.dev.vars
*.log
.DS_Store
```

### 5. Copy Project Rules

If the skill has rules, copy them to the new project:

```bash
mkdir -p {project-name}/.claude/rules
cp ~/.claude/skills/cloudflare-worker-base/rules/*.md {project-name}/.claude/rules/
```

This ensures Claude has the correction rules available in the new project.

### 6. Install Dependencies

Run:
```bash
cd {project-name}
npm install
```

### 7. Provide Next Steps

Output a summary:

```
✅ Cloudflare Worker project "{project-name}" created!

📁 Structure:
   - src/index.ts       (Hono API routes)
   - public/            (Static assets)
   - wrangler.jsonc     (Cloudflare config)

🚀 Next steps:
   1. cd {project-name}
   2. npm run dev         (Start local dev server)
   3. npx wrangler deploy (Deploy to Cloudflare)

{If bindings were added, list the wrangler commands to create them}

📚 Skill loaded: cloudflare-worker-base
   - 8 common issues auto-prevented
   - Correction rules copied to .claude/rules/
```

---

## Critical Patterns Applied

This command applies patterns from the cloudflare-worker-base skill:

1. **Export Syntax**: Uses `export default app` (not `{ fetch: app.fetch }`)
2. **run_worker_first**: Configured in wrangler.jsonc to prevent SPA fallback intercepting API routes
3. **Vite Plugin**: Uses `@cloudflare/vite-plugin` for unified dev experience
4. **TypeScript Config**: Proper module resolution and strict mode

---

## Error Prevention

The templates prevent these documented issues:
- Export syntax error (hono #3955)
- Static assets routing conflicts (workers-sdk #8879)
- Vite HMR proxy conflicts
- Free tier 429 rate limits
- Missing account_id in CI/CD
