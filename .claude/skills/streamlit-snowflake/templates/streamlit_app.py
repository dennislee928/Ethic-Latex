"""
Streamlit in Snowflake - Main Application

This template demonstrates:
- Snowpark session connection via st.connection()
- Cached data loading for performance
- Basic layout patterns
- Error handling

Deploy: snow streamlit deploy --replace
"""

import streamlit as st
import pandas as pd

# Import shared utilities (session management, query helpers)
from common.utils import get_snowpark_session, run_query_safe, show_connection_info

# Page configuration
# Note: page_title, page_icon, and menu_items are NOT supported in Streamlit in Snowflake
# Only use layout and initial_sidebar_state
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

# Application title
st.title("My Streamlit App")
st.markdown("Built with Streamlit in Snowflake")


# -----------------------------------------------------------------------------
# Data Loading (Cached)
# -----------------------------------------------------------------------------

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_sample_data() -> pd.DataFrame:
    """
    Load sample data from Snowflake.
    Uses caching to avoid repeated queries on interaction.
    """
    session = get_snowpark_session()

    # Example query - replace with your table/query
    query = """
    SELECT
        CURRENT_TIMESTAMP() as query_time,
        CURRENT_USER() as current_user,
        CURRENT_ROLE() as current_role,
        CURRENT_WAREHOUSE() as warehouse,
        CURRENT_DATABASE() as database,
        CURRENT_SCHEMA() as schema
    """

    try:
        df = session.sql(query).to_pandas()
        return df
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def run_custom_query(query: str) -> pd.DataFrame:
    """
    Run a custom SQL query with caching.
    TTL of 5 minutes to balance freshness and performance.
    """
    session = get_snowpark_session()
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

with st.sidebar:
    st.header("Settings")

    # Example: Refresh button that clears cache
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # Example: Show connection info
    with st.expander("Connection Info"):
        df = load_sample_data()
        if not df.empty:
            st.write(f"**User:** {df['CURRENT_USER'].iloc[0]}")
            st.write(f"**Role:** {df['CURRENT_ROLE'].iloc[0]}")
            st.write(f"**Warehouse:** {df['WAREHOUSE'].iloc[0]}")


# -----------------------------------------------------------------------------
# Main Content
# -----------------------------------------------------------------------------

# Tabs for different views
tab1, tab2 = st.tabs(["Dashboard", "Query"])

with tab1:
    st.header("Dashboard")

    # Example metrics row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Metric 1", "123", "+5%")

    with col2:
        st.metric("Metric 2", "456", "-2%")

    with col3:
        st.metric("Metric 3", "789", "+10%")

    # Example data display
    st.subheader("Sample Data")
    df = load_sample_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data available. Check your connection settings.")

with tab2:
    st.header("Run Custom Query")

    # SQL query input
    query = st.text_area(
        "Enter SQL Query",
        value="SELECT CURRENT_TIMESTAMP() as now",
        height=100,
    )

    if st.button("Run Query"):
        with st.spinner("Executing query..."):
            result = run_custom_query(query)

            if not result.empty:
                st.success(f"Returned {len(result)} rows")
                st.dataframe(result, use_container_width=True)

                # Download option
                csv = result.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "query_results.csv",
                    "text/csv",
                )


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------

st.divider()
st.caption("Powered by Streamlit in Snowflake")
