---
globs: ["**/snowflake.yml", "**/snowflake.yaml", "**/setup_script.sql", "**/streamlit_app.py", "**/environment.yml"]
---

# Snowflake Native App Development

Rules for building and deploying Snowflake Native Apps with Streamlit.

## snow CLI Commands (Recommended)

| Task | Command |
|------|---------|
| Deploy/run app | `snow app run` |
| Create version | `snow app version create V1_0` |
| List versions | `snow app version list` |
| Drop version | `snow app version drop V1_0` |
| Publish | `snow app publish --version V1_0` |
| Teardown | `snow app teardown` |

📚 **Source**: https://docs.snowflake.com/en/developer-guide/snowflake-cli/native-apps/overview

## Deployment Sequence

After every `snow app run`, you MUST re-attach external access integrations:

```sql
ALTER STREAMLIT [APP_NAME].config_schema.[streamlit_name]
  SET EXTERNAL_ACCESS_INTEGRATIONS = (integration_name)
```

The setup_script.sql CREATE STREAMLIT does NOT persist this setting across deploys.

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `src: app/streamlit/` with `dest: streamlit/` | List individual files explicitly to avoid nested `streamlit/streamlit/` |
| `dict(result[0])` for Snowpark Row | Access columns explicitly: `row['COLUMN_NAME']` |
| Privileges in manifest.yml | Remove privileges section entirely (Native Apps can't declare privileges) |
| GRANT ALL/FUTURE in setup_script.sql | Use specific table grants only |

## External Access Integration Setup

Must be created in a real database (not the app package). Run in order:

```sql
-- 1. Create database for rules (if needed)
CREATE DATABASE IF NOT EXISTS [APP]_UTILS;

-- 2. Create network rule (fully qualified)
CREATE OR REPLACE NETWORK RULE [DB].PUBLIC.[rule_name]
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('[hostname]:443');

-- 3. Create integration referencing the rule
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION [integration_name]
  ALLOWED_NETWORK_RULES = ([DB].PUBLIC.[rule_name])
  ENABLED = TRUE;

-- 4. Grant to app
GRANT USAGE ON INTEGRATION [integration_name]
  TO APPLICATION [APP_NAME];

-- 5. Attach to Streamlit (must repeat after each deploy!)
ALTER STREAMLIT [APP_NAME].config_schema.[streamlit]
  SET EXTERNAL_ACCESS_INTEGRATIONS = ([integration_name]);
```

## Artifact Mapping in snowflake.yml

Directory mappings nest the folder. Always list files explicitly:

```yaml
# WRONG - creates streamlit/streamlit/
artifacts:
  - src: app/streamlit/
    dest: streamlit/

# CORRECT - flat structure
artifacts:
  - src: app/streamlit/environment.yml
    dest: streamlit/environment.yml
  - src: app/streamlit/streamlit_app.py
    dest: streamlit/streamlit_app.py
  - src: app/streamlit/pages/01_sync.py
    dest: streamlit/pages/01_sync.py
```

## Snowpark Row Access

```python
# WRONG
config = dict(result[0])  # Doesn't work as expected

# CORRECT
row = result[0]
config = {
    'COLUMN_A': row['COLUMN_A'],
    'COLUMN_B': row['COLUMN_B'],
}
```
