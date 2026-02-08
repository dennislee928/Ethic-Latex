# Container Runtime Templates

Templates for deploying Streamlit apps using **Container Runtime** (Preview) instead of Warehouse Runtime.

## Key Differences from Warehouse Runtime

| Aspect | Warehouse Runtime | Container Runtime |
|--------|-------------------|-------------------|
| Instance | Per-viewer | Shared across viewers |
| Packages | Snowflake Anaconda only | PyPI packages allowed |
| Config file | `environment.yml` | `requirements.txt` or `pyproject.toml` |
| Python | 3.9, 3.10, 3.11 | 3.11 only |
| Streamlit | 1.22 - 1.35 | 1.49+ |
| Cost | ~$48/day (XS warehouse) | ~$2.88/day (XS compute pool) |
| Caching | Session-scoped only | Full cross-viewer caching |

## When to Use Container Runtime

**Use Container Runtime when:**
- App has frequent usage across multiple viewers
- You need PyPI packages not in Snowflake Anaconda Channel
- Cost optimization is important
- You want cross-viewer caching

**Stick with Warehouse Runtime when:**
- You need Python 3.9 or 3.10
- You need isolated sessions per viewer
- Your app is rarely used (warehouse auto-suspend saves costs)
- You need the stability of the Snowflake Anaconda Channel

## Setup

### 1. Create Compute Pool

```sql
-- Create compute pool for Streamlit apps
CREATE COMPUTE POOL streamlit_pool
  MIN_NODES = 1
  MAX_NODES = 3
  INSTANCE_FAMILY = CPU_X64_XS;

-- Check pool status
DESCRIBE COMPUTE POOL streamlit_pool;
```

### 2. Create External Access Integration (Optional)

Required if you need to install packages from PyPI:

```sql
-- Create network rule for PyPI
CREATE OR REPLACE NETWORK RULE pypi_network_rule
  TYPE = HOST_PORT
  VALUE_LIST = ('pypi.org', 'files.pythonhosted.org')
  MODE = EGRESS;

-- Create external access integration
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION pypi_access
  ALLOWED_NETWORK_RULES = (pypi_network_rule)
  ENABLED = TRUE;
```

### 3. Deploy with Container Runtime

```sql
CREATE OR REPLACE STREAMLIT my_app
  FROM '@my_stage/app_folder'
  MAIN_FILE = 'streamlit_app.py'
  RUNTIME_NAME = 'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'
  COMPUTE_POOL = streamlit_pool
  QUERY_WAREHOUSE = my_warehouse
  EXTERNAL_ACCESS_INTEGRATIONS = (pypi_access);
```

## Session Handling Difference

Container Runtime does NOT have the `_snowflake` module. Update your session code:

**Warehouse Runtime:**
```python
from _snowflake import get_active_session
session = get_active_session()
```

**Container Runtime:**
```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()

# OR use Streamlit's connection (works in both):
import streamlit as st
conn = st.connection("snowflake")
session = conn.session()
```

## Cost Comparison

| Compute Type | Credits/Hour | USD/Day (at $2/credit) |
|--------------|--------------|------------------------|
| XS Warehouse | 1.0 | ~$48 (24 hours) |
| CPU_X64_XS Pool | 0.06 | ~$2.88 (24 hours) |

Container Runtime is **~94% cheaper** for always-on apps.

## Files in This Directory

- `requirements.txt` - Package dependencies for PyPI
- `pyproject.toml` - Alternative to requirements.txt (optional)
- `streamlit_app.py` - Entry point compatible with Container Runtime

## References

- [Runtime Environments](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments)
- [Container Runtime Preview](https://dev.to/tsubasa_tech/sis-container-runtime-run-streamlit-apps-at-a-fraction-of-the-cost-2mn8)
