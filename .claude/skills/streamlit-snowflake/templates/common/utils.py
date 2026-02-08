"""
Shared Utilities for Streamlit in Snowflake Apps

Common patterns for:
- Session management
- Query execution
- Data transformation
- Error handling
"""

import streamlit as st
import pandas as pd
from typing import Optional, Any
from functools import wraps


# -----------------------------------------------------------------------------
# Session Management
# -----------------------------------------------------------------------------

@st.cache_resource
def get_snowpark_session():
    """
    Get cached Snowpark session.

    Usage:
        from common.utils import get_snowpark_session
        session = get_snowpark_session()
        df = session.sql("SELECT 1").to_pandas()
    """
    conn = st.connection("snowflake")
    return conn.session()


def get_current_context() -> dict:
    """
    Get current Snowflake context (user, role, warehouse, etc.)

    Returns:
        dict with keys: user, role, warehouse, database, schema
    """
    session = get_snowpark_session()
    result = session.sql("""
        SELECT
            CURRENT_USER() as user,
            CURRENT_ROLE() as role,
            CURRENT_WAREHOUSE() as warehouse,
            CURRENT_DATABASE() as database,
            CURRENT_SCHEMA() as schema
    """).to_pandas()

    if result.empty:
        return {}

    row = result.iloc[0]
    return {
        "user": row["USER"],
        "role": row["ROLE"],
        "warehouse": row["WAREHOUSE"],
        "database": row["DATABASE"],
        "schema": row["SCHEMA"],
    }


# -----------------------------------------------------------------------------
# Query Execution
# -----------------------------------------------------------------------------

def run_query(
    query: str,
    ttl: int = 300,
    show_spinner: bool = True,
) -> pd.DataFrame:
    """
    Execute a SQL query with optional caching.

    Args:
        query: SQL query string
        ttl: Cache time-to-live in seconds (default 5 min)
        show_spinner: Show loading spinner

    Returns:
        pandas DataFrame with results

    Usage:
        df = run_query("SELECT * FROM my_table LIMIT 100")
    """
    @st.cache_data(ttl=ttl)
    def _execute(q: str) -> pd.DataFrame:
        session = get_snowpark_session()
        return session.sql(q).to_pandas()

    if show_spinner:
        with st.spinner("Executing query..."):
            return _execute(query)
    else:
        return _execute(query)


def run_query_safe(
    query: str,
    ttl: int = 300,
    default: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Execute query with error handling.

    Returns empty DataFrame (or default) on error instead of raising.

    Usage:
        df = run_query_safe("SELECT * FROM maybe_missing_table")
        if df.empty:
            st.warning("No data found")
    """
    try:
        return run_query(query, ttl=ttl, show_spinner=False)
    except Exception as e:
        st.error(f"Query failed: {e}")
        return default if default is not None else pd.DataFrame()


# -----------------------------------------------------------------------------
# Data Helpers
# -----------------------------------------------------------------------------

def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable string."""
    if bytes_val is None:
        return "N/A"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} PB"


def format_number(num: Any) -> str:
    """Format number with thousand separators."""
    if num is None:
        return "N/A"
    try:
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return str(num)


# -----------------------------------------------------------------------------
# UI Helpers
# -----------------------------------------------------------------------------

def show_dataframe_with_download(
    df: pd.DataFrame,
    filename: str = "data.csv",
    key: Optional[str] = None,
) -> None:
    """
    Display DataFrame with download button.

    Usage:
        show_dataframe_with_download(df, "my_export.csv")
    """
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=filename,
            mime="text/csv",
            key=key,
        )


def show_connection_info() -> None:
    """Display current Snowflake connection info in an expander."""
    with st.expander("Connection Info"):
        ctx = get_current_context()
        if ctx:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**User:** {ctx.get('user', 'N/A')}")
                st.write(f"**Role:** {ctx.get('role', 'N/A')}")
            with col2:
                st.write(f"**Warehouse:** {ctx.get('warehouse', 'N/A')}")
                st.write(f"**Database:** {ctx.get('database', 'N/A')}.{ctx.get('schema', 'N/A')}")
        else:
            st.warning("Could not retrieve connection info")
