# CLAUDE.md Documentation Patterns

Common mistakes and best practices for CLAUDE.md files.

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Copying full framework docs into CLAUDE.md | Link to official docs, only include project-specific patterns |
| Generic tech tutorials | Project-specific workflows and commands |
| Outdated "Last Updated" date | Current date when making changes |
| Hardcoded paths that may change | Use relative paths or explain file discovery patterns |

## Structure Best Practices

### Required Sections

Every CLAUDE.md should have:

1. **Project Overview** - What it is, tech stack
2. **Quick Start** - Essential commands to get running
3. **Project Structure** - Key directories and their purposes
4. **Common Tasks** - Frequent operations with commands

### Optional but Recommended

- **Environment Variables** - Required vars and where to set them
- **Key Files** - Important files and their purposes
- **Troubleshooting** - Common issues and solutions

## Anti-Patterns

### Don't Include

- Full API references (link to docs instead)
- Generic programming tutorials
- Information that changes frequently without automated updates
- Secrets or credentials
- User-specific configuration

### Keep Focused

CLAUDE.md is for project-specific context:
- ✅ "Run `pnpm db:push` to sync schema"
- ❌ "Drizzle ORM is a TypeScript ORM that..."

## Maintenance

### Update Triggers

Update CLAUDE.md when:
- Adding new major dependencies
- Changing project structure
- Adding new workflows/commands
- Fixing common developer issues

### Don't Update For

- Minor dependency patches
- Small code changes
- Bug fixes (unless pattern-breaking)

## Size Guidelines

| Project Size | CLAUDE.md Lines | Notes |
|--------------|-----------------|-------|
| Small/Simple | 100-200 | Just essentials |
| Medium | 200-500 | Include troubleshooting |
| Large/Complex | 500-1000 | Multiple workflows, detailed structure |
| Enterprise | 1000+ | Consider splitting into docs/ |

**Note**: Size isn't the metric - clarity and usefulness are. A well-organized 800-line CLAUDE.md is better than a cramped 200-line one.
