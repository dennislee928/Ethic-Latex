# Initialize Documentation

Create documentation structure for a new project. Detects project type and uses appropriate templates.

## Command Usage

`/docs/init [options]`

**Options:**
- `--type=cloudflare|nextjs|generic` - Force project type (auto-detects if not specified)
- `--full` - Include docs/ directory scaffolding
- `--minimal` - Only create CLAUDE.md

## Process

### 1. Detect Project Type

Look for indicator files in this order:

```
Priority 1: wrangler.jsonc or wrangler.toml → Cloudflare Workers
Priority 2: next.config.js or next.config.ts → Next.js
Priority 3: package.json exists → Generic Node.js
Priority 4: None of the above → Generic
```

Also scan package.json dependencies for additional context:
- React, Vue, Svelte → Frontend framework
- Hono, Express, Fastify → API framework
- Drizzle, Prisma → Database ORM
- Clerk, better-auth → Authentication

### 2. Gather Project Info

Extract from existing files:

```javascript
// From package.json
const projectName = pkg.name || folderName
const description = pkg.description || ''
const techStack = Object.keys(pkg.dependencies || {})

// From git
const repoUrl = getGitRemoteUrl() // if available
```

### 3. Check Existing Files

Before creating, check what exists:

```markdown
## Existing Documentation

| File | Status | Action |
|------|--------|--------|
| CLAUDE.md | Missing | Will create |
| README.md | Exists (124 lines) | Skip (use --force to overwrite) |
| docs/ | Missing | Will create (with --full) |

Proceed? [Y/n]
```

### 4. Create CLAUDE.md

Use the appropriate template based on detected project type:

**For Cloudflare Workers:**
```bash
# Copy from skill templates
# Fill in: {{PROJECT_NAME}}, {{DATE}}, {{TECH_STACK}}
```

Template includes:
- Wrangler commands
- D1/KV/R2 bindings (if detected in wrangler.jsonc)
- Cloudflare-specific patterns
- Deployment workflow

**For Next.js:**
- App Router vs Pages Router patterns
- Server Components guidance
- Deployment (Vercel) workflow
- API route patterns

**For Generic:**
- Basic project structure
- Development commands
- Key file locations

### 5. Create README.md (if missing)

Use README template with:
- Project name and description from package.json
- Standard sections (Installation, Usage, Development, License)
- Placeholder content for user to fill in

### 6. Scaffold docs/ (if --full)

Create documentation directory:

```bash
mkdir -p docs
```

Create starter files:
- `docs/ARCHITECTURE.md` - System overview placeholder
- `docs/API.md` - API documentation placeholder
- `docs/DATABASE.md` - Database schema placeholder (if ORM detected)

Each file has basic structure and TODOs for user to complete.

### 7. Output Summary

```markdown
## Documentation Initialized

**Project Type**: Cloudflare Workers
**Files Created**:
- [x] CLAUDE.md (from cloudflare template)
- [x] README.md (from standard template)
- [x] docs/ARCHITECTURE.md
- [x] docs/API.md
- [x] docs/DATABASE.md

**Next Steps**:
1. Review CLAUDE.md and customize for your project
2. Update README.md with accurate installation instructions
3. Fill in docs/ files as you build features

**Commit suggestion**:
```bash
git add CLAUDE.md README.md docs/
git commit -m "docs: Initialize project documentation"
```
```

## Template Placeholders

Templates use these placeholders (auto-filled):

| Placeholder | Source |
|-------------|--------|
| `{{PROJECT_NAME}}` | package.json name or folder name |
| `{{DATE}}` | Current date (YYYY-MM-DD) |
| `{{TECH_STACK}}` | Detected technologies |
| `{{DESCRIPTION}}` | package.json description |
| `{{REPO_URL}}` | Git remote URL (if available) |

## Edge Cases

**CLAUDE.md already exists:**
- Skip creation unless `--force` specified
- Suggest running `/docs/claude` instead for maintenance

**No package.json:**
- Use folder name for project name
- Use generic template
- Warn user to update tech stack section manually

**Monorepo detected:**
- Ask which package to document
- Create docs at appropriate level (root vs package)
