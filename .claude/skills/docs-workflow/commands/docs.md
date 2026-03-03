# Documentation Workflow

Main entry point for documentation management. Shows available subcommands and quick actions.

## Command Usage

`/docs`

**Related Commands:**
- `/docs-init` - Create documentation for new project
- `/docs-update` - Audit and maintain all documentation
- `/docs-claude` - Smart CLAUDE.md maintenance

## Process

### 1. Check Current Project

Quickly assess documentation status:

```
Look for:
- CLAUDE.md exists? Y/N
- README.md exists? Y/N
- docs/ directory? Y/N
- SESSION.md? Y/N
```

### 2. Present Options

Based on what exists, show relevant options:

```markdown
## Documentation Status

| File | Status |
|------|--------|
| CLAUDE.md | Exists (Last updated: 2025-12-01) |
| README.md | Exists |
| docs/ | Missing |
| SESSION.md | Exists |

## Available Commands

1. `/docs-init` - Create missing documentation (will scaffold docs/)
2. `/docs-update` - Audit all docs for staleness and issues
3. `/docs-claude` - Check and update CLAUDE.md

What would you like to do?
```

## Quick Actions

If user just wants a quick status without running full commands:

```markdown
## Quick Status

**CLAUDE.md**: 847 lines, last git change 3 days ago
**README.md**: 124 lines, matches package.json name
**docs/**: 4 files (ARCHITECTURE.md, API.md, DATABASE.md, TESTING.md)

No obvious issues detected. Run `/docs-update` for full audit.
```

## Integration

This command is the entry point. For detailed work, use the specific commands:

- `/docs-init` - Full initialization workflow
- `/docs-update` - Full audit workflow
- `/docs-claude` - CLAUDE.md-specific maintenance
