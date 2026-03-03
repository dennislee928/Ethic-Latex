# Smart CLAUDE.md Maintenance

Focused maintenance for CLAUDE.md files. Ensures project context stays in sync with actual codebase state.

## Command Usage

`/docs/claude [options]`

**Options:**
- (no options) - Full maintenance check
- `--quick` - Just check date and basic structure
- `--sync` - Auto-fix sync issues without prompting

## Process

### 1. Read Current CLAUDE.md

Parse the existing CLAUDE.md to understand:
- Last Updated date
- Tech stack mentioned
- File paths referenced
- Scripts/commands documented
- Environment variables listed

### 2. Scan Project State

Gather actual project information:

```javascript
// From package.json
const dependencies = { ...pkg.dependencies, ...pkg.devDependencies }
const scripts = pkg.scripts

// From wrangler.jsonc (if exists)
const bindings = parseWranglerConfig()

// From .env.example or .env (if exists)
const envVars = parseEnvFile()

// From file system
const keyFiles = findKeyFiles() // src/index.ts, src/server/*, etc.
```

### 3. Compare & Identify Gaps

**Tech Stack Sync:**
```markdown
## Tech Stack Analysis

| Technology | In CLAUDE.md | In package.json | Status |
|------------|--------------|-----------------|--------|
| React | ✅ Yes | ✅ Yes | ✅ OK |
| Drizzle ORM | ❌ No | ✅ Yes | ⚠️ Missing |
| Tailwind | ✅ Yes | ✅ Yes | ✅ OK |
| Hono | ❌ No | ✅ Yes | ⚠️ Missing |

**Suggestion**: Add Drizzle ORM and Hono sections to CLAUDE.md
```

**File Path Validation:**
```markdown
## File Paths in CLAUDE.md

| Referenced Path | Exists | Status |
|-----------------|--------|--------|
| `src/server/index.ts` | ✅ Yes | ✅ OK |
| `src/lib/auth.ts` | ❌ No | ⚠️ Broken |
| `src/config.ts` | ✅ Yes | ✅ OK |

**Broken path**: `src/lib/auth.ts`
- Did you mean: `src/auth/index.ts`?
```

**Script References:**
```markdown
## Scripts in CLAUDE.md

| Script Mentioned | In package.json | Status |
|------------------|-----------------|--------|
| `pnpm dev` | ✅ Yes | ✅ OK |
| `pnpm migrate` | ❌ No | ⚠️ Doesn't exist |
| `pnpm build` | ✅ Yes | ✅ OK |

**Note**: `pnpm migrate` is mentioned but doesn't exist in package.json
```

**Environment Variables:**
```markdown
## Environment Variables

| Var in CLAUDE.md | In .env.example | Status |
|------------------|-----------------|--------|
| `DATABASE_URL` | ✅ Yes | ✅ OK |
| `AUTH_SECRET` | ❌ No | ⚠️ Missing from .env.example |
| `OLD_API_KEY` | ✅ Yes | ⚠️ Not used in code |
```

### 4. Check Critical Rules

Based on detected tech stack, check if CLAUDE.md includes important patterns:

**For Cloudflare Workers:**
- Wrangler commands mentioned?
- D1 migration workflow?
- Workers-specific limitations noted?

**For React/Vite:**
- Dev server commands?
- Build/preview workflow?
- Environment variable patterns (VITE_ prefix)?

**For Database (Drizzle/Prisma):**
- Migration commands?
- Schema location?
- Common query patterns?

### 5. Suggest Updates

Present findings and offer to fix:

```markdown
## CLAUDE.md Maintenance Report

### Date Check
- Last Updated: 2025-10-15 (87 days ago)
- Last git change: 2025-12-01
- **Action**: Update date to today

### Tech Stack Gaps
Missing sections for detected technologies:
1. **Drizzle ORM** - Database queries, migrations, schema
2. **Hono** - API routing, middleware patterns

### Broken References
1. `src/lib/auth.ts` → Should be `src/auth/index.ts`
2. `pnpm migrate` → Script doesn't exist (maybe `pnpm db:push`?)

### Missing Critical Patterns
For a Cloudflare Workers project, consider adding:
- D1 binding usage
- R2 storage patterns (if using R2)
- Deployment checklist

---

**Proposed Changes:**
1. [ ] Update "Last Updated" date
2. [ ] Fix broken path: lib/auth.ts → auth/index.ts
3. [ ] Add Drizzle ORM section
4. [ ] Add Hono routing section

Apply changes? [Y/n/select]
```

### 6. Apply Updates

For approved changes:

**Date Update:**
- Find "Last Updated" pattern
- Replace with current date

**Path Fixes:**
- Find-and-replace broken paths
- Update to correct paths

**Add Missing Sections:**
- Generate section content based on detected tech
- Insert at appropriate location (after existing tech sections)
- Use templates from skill's templates/ directory

### 7. Output Summary

```markdown
## CLAUDE.md Updated

**Changes Made:**
- Updated "Last Updated" to 2026-01-11
- Fixed path: src/lib/auth.ts → src/auth/index.ts
- Added Drizzle ORM section (15 lines)
- Added Hono routing section (12 lines)

**Manual Review Suggested:**
- Drizzle section: Verify table names and query patterns
- Hono section: Add project-specific middleware

**Commit suggestion:**
```bash
git add CLAUDE.md
git commit -m "docs: Update CLAUDE.md with current project state"
```
```

## Section Templates

When adding missing tech sections, use these templates:

**Drizzle ORM:**
```markdown
## Database (Drizzle ORM)

**Schema**: `src/db/schema.ts`
**Migrations**: `drizzle/`

**Common Commands:**
- Generate migration: `pnpm drizzle-kit generate`
- Push to DB: `pnpm drizzle-kit push`
- Studio: `pnpm drizzle-kit studio`

**Query Patterns:**
[To be filled based on project usage]
```

**Hono:**
```markdown
## API (Hono)

**Entry**: `src/server/index.ts`
**Routes**: `src/server/routes/`

**Route Pattern:**
```typescript
app.get('/api/resource', async (c) => {
  // Handler
})
```
```

## Important Notes

- Only modifies CLAUDE.md, not other documentation
- Always shows diff before applying changes
- Preserves existing content structure
- Sections are added, not replaced (unless explicitly broken)
- User can select which changes to apply
