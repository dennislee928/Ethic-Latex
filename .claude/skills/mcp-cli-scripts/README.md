# MCP CLI Scripts

Build CLI scripts alongside MCP servers for Claude Code terminal environments.

## Auto-Trigger Keywords

This skill should be invoked when discussing:

- MCP server scripts, CLI scripts for MCP, MCP companion scripts
- SCRIPTS.md, batch processing MCP, MCP file output
- npx tsx scripts, TypeScript CLI scripts
- MCP batch operations, MCP caching, MCP file I/O
- Saving MCP results to files
- Processing batch inputs for MCP tools
- CLI wrappers for APIs

## What This Skill Provides

1. **Pattern**: Why and when to create CLI scripts alongside MCP servers
2. **Templates**: TypeScript script template, SCRIPTS.md documentation template
3. **Rules**: Correction rules for consistent script patterns
4. **Best Practices**: JSON output, argument patterns, error handling

## Quick Start

```bash
# Copy templates to your MCP server project
cp ~/.claude/skills/mcp-cli-scripts/templates/script-template.ts scripts/new-tool.ts
cp ~/.claude/skills/mcp-cli-scripts/templates/SCRIPTS-TEMPLATE.md SCRIPTS.md

# Install tsx
npm install -D tsx

# Run your script
npx tsx scripts/new-tool.ts --help
```

## Related Skills

- `fastmcp` - Python MCP server framework
- `typescript-mcp` - TypeScript MCP patterns
- `cloudflare-mcp-server` - Cloudflare-hosted MCP servers
