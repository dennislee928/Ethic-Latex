# CLI Scripts

These scripts provide command-line access to {server-name} functionality.
For use with Claude Code in terminal environments.

## Prerequisites

- Node.js 18+
- Run `npm install` in this directory

## Available Scripts

### {tool-name}.ts

{Description of what this tool does}

**Usage:**
```bash
npx tsx scripts/{tool-name}.ts <required-arg>
npx tsx scripts/{tool-name}.ts --option value
```

**Arguments:**
- `<required-arg>` - Description
- `--option <value>` - Description (default: x)

**Examples:**
```bash
# Basic usage
npx tsx scripts/{tool-name}.ts 12345

# With options
npx tsx scripts/{tool-name}.ts --input batch.csv --output results.json

# Verbose mode
npx tsx scripts/{tool-name}.ts 12345 --verbose
```

**Output:**
```json
{
  "success": true,
  "data": { ... }
}
```

### {another-tool}.ts

...

## Common Options

All scripts support these common options:

| Option | Description |
|--------|-------------|
| `--output <file>` | Write results to file instead of stdout |
| `--format <type>` | Output format: json, csv, table |
| `--verbose` | Show debug information |
| `--help` | Show usage information |

## Error Handling

Scripts exit with code 0 on success, non-zero on failure.
Errors are output as JSON:

```json
{
  "success": false,
  "error": "Error message here"
}
```
