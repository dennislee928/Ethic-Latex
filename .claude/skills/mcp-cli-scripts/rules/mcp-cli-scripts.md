# MCP CLI Scripts Corrections

Apply when editing TypeScript files in `scripts/` directories.

## Shebang

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `#!/usr/bin/env node` | `#!/usr/bin/env npx tsx` |
| `#!/usr/bin/env ts-node` | `#!/usr/bin/env npx tsx` |
| No shebang | Add `#!/usr/bin/env npx tsx` at top |

**Why**: tsx handles ESM + TypeScript without compilation. Node requires transpilation. ts-node has compatibility issues.

## Output Format

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `console.log("Found 5 results")` | `console.log(JSON.stringify({ success: true, count: 5 }))` |
| `console.log(data)` | `console.log(JSON.stringify(data, null, 2))` |
| Unstructured text output | Structured JSON output |

**Why**: JSON output is machine-readable. Claude Code can parse and use structured data.

## Error Handling

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `console.error("Error: " + err.message)` | `console.error(JSON.stringify({ success: false, error: err.message }))` |
| `throw new Error(...)` without catching | Catch and output JSON error |
| `process.exit(1)` without error output | Output JSON error, then exit |

**Why**: Consistent error format allows Claude Code to detect and handle failures.

## Argument Patterns

Use these standard argument names consistently:

| Pattern | Description |
|---------|-------------|
| `--input <file>` | Read input from file |
| `--output <file>` | Write output to file |
| `--format <type>` | Output format (json/csv/table) |
| `--verbose` | Debug output |
| `--help` or `-h` | Show usage |

**Why**: Consistent patterns reduce cognitive load. Claude can predict script interfaces.

## Verbose Output

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `console.log("Processing...")` | `if (args.verbose) console.error("Processing...")` |
| Status messages to stdout | Status messages to stderr (preserves stdout for data) |

**Why**: Verbose output should go to stderr so stdout contains only the result data.
