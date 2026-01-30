# docs-workflow

Documentation lifecycle management for Claude Code projects.

## Auto-Trigger Keywords

- "create CLAUDE.md"
- "initialize documentation"
- "docs init"
- "update documentation"
- "audit docs"
- "CLAUDE.md maintenance"
- "check documentation"
- "create README"
- "docs workflow"

## Commands

| Command | Description |
|---------|-------------|
| `/docs` | Main entry - shows available options |
| `/docs/init` | Create CLAUDE.md + README.md + docs/ structure |
| `/docs/update` | Audit and maintain all documentation |
| `/docs/claude` | Smart CLAUDE.md maintenance |

## What It Does

- Creates CLAUDE.md from project-type templates (Cloudflare, Next.js, generic)
- Creates README.md with standard structure
- Scaffolds docs/ directory (optional)
- Audits docs for staleness, broken links, outdated versions
- Maintains CLAUDE.md to match actual project state

## When to Use

- Starting a new project
- Onboarding to an existing project without CLAUDE.md
- Before releases (audit documentation)
- Monthly maintenance
- After major code changes
