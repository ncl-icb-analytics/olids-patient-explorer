"""
Database connection management for Snowflake
"""

import streamlit as st


@st.cache_resource
def get_connection():
    """
    Get Snowflake connection using Streamlit's native connection.
    Connection is cached for performance.

    Returns:
        Snowflake session object
    """
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {str(e)}")
        st.stop()
