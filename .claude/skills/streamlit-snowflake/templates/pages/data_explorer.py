"""
Data Explorer Page

Multi-page Streamlit app example.
This page demonstrates:
- Table/schema browsing
- Interactive data filtering
- Visualization with Plotly
- Safe identifier handling
"""

import re
import streamlit as st
import pandas as pd

# Import shared utilities
from common.utils import get_snowpark_session

# Try to import plotly (optional dependency)
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.set_page_config(layout="wide")
st.title("Data Explorer")


# -----------------------------------------------------------------------------
# Identifier Validation (Security)
# -----------------------------------------------------------------------------

def validate_identifier(name: str) -> bool:
    """
    Validate Snowflake identifier to prevent SQL injection.

    Valid identifiers:
    - Start with letter or underscore
    - Contain only letters, numbers, underscores
    - Max 255 characters
    """
    if not name or len(name) > 255:
        return False
    # Snowflake unquoted identifier pattern
    pattern = r'^[A-Za-z_][A-Za-z0-9_$]*$'
    return bool(re.match(pattern, name))


def quote_identifier(name: str) -> str:
    """
    Quote identifier for safe use in SQL.
    Escapes any double quotes within the identifier.
    """
    if not validate_identifier(name):
        # For complex identifiers, quote them
        escaped = name.replace('"', '""')
        return f'"{escaped}"'
    return name


# -----------------------------------------------------------------------------
# Data Functions
# -----------------------------------------------------------------------------

@st.cache_data(ttl=600)
def get_tables(database: str, schema: str) -> pd.DataFrame:
    """Get list of tables in a schema with safe identifier handling."""
    if not validate_identifier(database) or not validate_identifier(schema):
        st.error("Invalid database or schema name. Use alphanumeric characters and underscores only.")
        return pd.DataFrame()

    session = get_snowpark_session()
    # Use quoted identifiers for safety
    query = f"""
    SELECT table_name, row_count, bytes
    FROM {quote_identifier(database)}.information_schema.tables
    WHERE table_schema = '{schema.upper()}'
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
    """
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Failed to list tables: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def preview_table(database: str, schema: str, table: str, limit: int = 100) -> pd.DataFrame:
    """Preview rows from a table with safe identifier handling."""
    # Validate all identifiers
    for name, label in [(database, "Database"), (schema, "Schema"), (table, "Table")]:
        if not validate_identifier(name):
            st.error(f"Invalid {label} name: {name}")
            return pd.DataFrame()

    # Validate limit is reasonable
    limit = max(1, min(limit, 10000))

    session = get_snowpark_session()
    # Use quoted identifiers
    query = f'SELECT * FROM {quote_identifier(database)}.{quote_identifier(schema)}.{quote_identifier(table)} LIMIT {limit}'
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Failed to preview table: {e}")
        return pd.DataFrame()


# -----------------------------------------------------------------------------
# Sidebar Controls
# -----------------------------------------------------------------------------

with st.sidebar:
    st.header("Explorer Settings")

    # Database/Schema selection
    database = st.text_input("Database", value="MY_DATABASE")
    schema = st.text_input("Schema", value="PUBLIC")

    # Validate inputs
    if database and not validate_identifier(database):
        st.warning("Database name contains invalid characters")
    if schema and not validate_identifier(schema):
        st.warning("Schema name contains invalid characters")

    # Row limit
    row_limit = st.slider("Preview Rows", 10, 500, 100)

    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()


# -----------------------------------------------------------------------------
# Main Content
# -----------------------------------------------------------------------------

# Get tables
st.subheader(f"Tables in {database}.{schema}")
tables_df = get_tables(database, schema)

if tables_df.empty:
    st.warning("No tables found or unable to access schema.")
    st.stop()

# Table selector - these come from query results, so they're safe
table_names = tables_df["TABLE_NAME"].tolist()
selected_table = st.selectbox("Select Table", table_names)

if selected_table:
    st.divider()

    # Show table info
    table_info = tables_df[tables_df["TABLE_NAME"] == selected_table].iloc[0]
    col1, col2 = st.columns(2)
    with col1:
        row_count = table_info.get('ROW_COUNT')
        if row_count is not None:
            st.metric("Row Count", f"{int(row_count):,}")
        else:
            st.metric("Row Count", "N/A")
    with col2:
        bytes_val = table_info.get("BYTES", 0) or 0
        st.metric("Size", f"{bytes_val / 1024 / 1024:.2f} MB")

    # Preview data
    st.subheader(f"Preview: {selected_table}")
    preview_df = preview_table(database, schema, selected_table, row_limit)

    if not preview_df.empty:
        # Data tabs
        tab1, tab2 = st.tabs(["Table View", "Chart View"])

        with tab1:
            st.dataframe(preview_df, use_container_width=True)

            # Column stats
            with st.expander("Column Statistics"):
                st.write(preview_df.describe())

        with tab2:
            if HAS_PLOTLY:
                # Simple chart builder
                numeric_cols = preview_df.select_dtypes(include=["number"]).columns.tolist()
                all_cols = preview_df.columns.tolist()

                if numeric_cols:
                    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter"])
                    x_col = st.selectbox("X Axis", all_cols)
                    y_col = st.selectbox("Y Axis", numeric_cols)

                    if chart_type == "Bar":
                        fig = px.bar(preview_df, x=x_col, y=y_col)
                    elif chart_type == "Line":
                        fig = px.line(preview_df, x=x_col, y=y_col)
                    else:
                        fig = px.scatter(preview_df, x=x_col, y=y_col)

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No numeric columns for charting.")
            else:
                st.info("Add 'plotly' to environment.yml for charts.")
