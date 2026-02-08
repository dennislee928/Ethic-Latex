---
globs:
  - "**/*.sql"
  - "**/snowflake*.py"
---

# Snowflake Cortex AI Corrections

## Function Schema

All Cortex AI functions are in `SNOWFLAKE.CORTEX` schema.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `CORTEX.COMPLETE(...)` | `SNOWFLAKE.CORTEX.COMPLETE(...)` |
| `COMPLETE(...)` without schema | `SNOWFLAKE.CORTEX.COMPLETE(...)` |

## Function Naming (Legacy vs New)

Snowflake renamed functions. Both work, but new names are preferred:

| Legacy (still works) | New (preferred) |
|---------------------|-----------------|
| `SNOWFLAKE.CORTEX.COMPLETE` | `AI_COMPLETE` |
| `SNOWFLAKE.CORTEX.SUMMARIZE` | `AI_SUMMARIZE` |
| `SNOWFLAKE.CORTEX.TRANSLATE` | `AI_TRANSLATE` |
| `SNOWFLAKE.CORTEX.SENTIMENT` | `AI_SENTIMENT` |

## Model Names

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `gpt-4` or `claude-3` | Snowflake-hosted models only |
| Generic model names | `llama3.1-70b`, `mistral-large2`, `snowflake-arctic` |

Available models:
- `llama3.1-70b`, `llama3.1-8b`, `llama3.2-3b`
- `mistral-large2`, `mistral-7b`
- `snowflake-arctic`
- `gemma-7b`

## COMPLETE Function Syntax

```sql
-- Simple prompt (string)
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-70b', 'Your prompt here');

-- With conversation history (array of objects)
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3.1-70b',
    [
        {'role': 'system', 'content': 'You are helpful'},
        {'role': 'user', 'content': 'Hello'}
    ]
);

-- With options (temperature, max_tokens)
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3.1-70b',
    'Prompt',
    {'temperature': 0.3, 'max_tokens': 500}
);
```

## TRANSLATE Function

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Missing source language parameter | Use empty string `''` for auto-detect |

```sql
-- Auto-detect source language
SELECT SNOWFLAKE.CORTEX.TRANSLATE(text, '', 'en');

-- Explicit source language
SELECT AI_TRANSLATE(text, 'es', 'en');
```

## AI_FILTER Usage

AI_FILTER returns boolean, use in WHERE clause:

```sql
-- CORRECT
SELECT * FROM table WHERE AI_FILTER(text_col, 'mentions shipping problems');

-- Can combine with SQL predicates
SELECT * FROM table
WHERE created_date > '2025-01-01'
  AND AI_FILTER(description, 'customer is frustrated');
```

## Billing Awareness

Both input AND output tokens are billed for:
- AI_COMPLETE, AI_CLASSIFY, AI_FILTER, AI_AGG
- AI_SUMMARIZE, AI_TRANSLATE
- Legacy SNOWFLAKE.CORTEX versions

~4 characters = 1 token (varies by model)
