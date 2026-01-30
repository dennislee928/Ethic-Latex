---
paths: "**/streamlit/*.py", "environment.yml", "**/streamlit_app.py"
---

# Snowflake Streamlit Corrections

## Map Rendering

`st.map()` may not render properly in Snowflake's Streamlit environment. Use PyDeck instead.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `st.map(df)` | `st.pydeck_chart(pdk.Deck(...))` |

Required setup:
1. Add `pydeck` to `environment.yml` dependencies
2. Import: `import pydeck as pdk`
3. Use `map_style=None` to inherit Streamlit theme

```python
import pydeck as pdk

st.pydeck_chart(
    pdk.Deck(
        map_style=None,  # Uses Streamlit theme
        initial_view_state=pdk.ViewState(
            latitude=-25.0,
            longitude=134.0,
            zoom=3,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position="[lon, lat]",
                get_color="[30, 136, 229, 180]",
                get_radius=15000,
                pickable=True,
            ),
        ],
        tooltip={"text": "{name}"}
    )
)
```

## Startup Performance

Snowflake Streamlit uses Warehouse Runtime by default:
- Creates new instance per viewer = cold start each time
- Slow startup is expected (warehouse resume + env init + package install)
- Container Runtime (Preview) is faster but requires compute pool setup

## Git Integration (Jan 2025)

Streamlit in Snowflake now supports **Git repository integration** for version-controlled apps:

```sql
-- Create Git repository reference
CREATE OR REPLACE GIT REPOSITORY my_repo
  API_INTEGRATION = github_api_int
  ORIGIN = 'https://github.com/org/repo.git';

-- Create Streamlit from Git
CREATE OR REPLACE STREAMLIT my_app
  ROOT_LOCATION = '@my_repo/branches/main/streamlit'
  MAIN_FILE = 'app.py'
  QUERY_WAREHOUSE = 'MY_WH';

-- Sync latest changes
ALTER GIT REPOSITORY my_repo FETCH;
```

**Benefits**:
- Deploy updates by pushing to Git (no manual upload)
- Branch-based environments (main, staging, dev)
- Full version history and rollback capability

📚 **Source**: https://docs.snowflake.com/en/developer-guide/streamlit/create-streamlit-git

## Column Names for Maps

PyDeck expects lowercase column names for coordinates:
- Rename `LATITUDE` → `lat`, `LONGITUDE` → `lon`
- Or use `get_position="[LONGITUDE, LATITUDE]"` explicitly

## Query Building Pattern

When building filtered queries with counts, build filter clause separately to avoid SQL errors.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `count_query = data_query.replace("SELECT cols", "SELECT COUNT(*)")` | Build filter clause separately, use in both queries |

**Wrong approach** (creates invalid SQL with leftover columns):
```python
data_query = "SELECT col1, col2 FROM table WHERE 1=1"
data_query += filter_clause
count_query = data_query.replace("SELECT col1", "SELECT COUNT(*) as CNT")  # Leaves col2!
```

**Correct approach:**
```python
filter_clause = ""
if search_term:
    filter_clause += f" AND UPPER(NAME) LIKE '%{search_term.upper()}%'"
if selected_state != "All":
    filter_clause += f" AND STATE = '{selected_state}'"

# Separate queries using same filter
count_query = f"SELECT COUNT(*) as CNT FROM table WHERE 1=1 {filter_clause}"
data_query = f"SELECT col1, col2 FROM table WHERE 1=1 {filter_clause} ORDER BY col1 LIMIT 500"
```
