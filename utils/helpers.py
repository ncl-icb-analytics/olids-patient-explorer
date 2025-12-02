"""
Helper functions for formatting and display
"""

from datetime import datetime
import streamlit as st


def format_date(date_value):
    """
    Format date value for display.

    Args:
        date_value: Date value (datetime, date, or string)

    Returns:
        Formatted date string or 'N/A'
    """
    if date_value is None:
        return "N/A"

    try:
        if isinstance(date_value, str):
            # Try to parse string date
            date_value = datetime.strptime(date_value, "%Y-%m-%d")

        return date_value.strftime("%d %b %Y")
    except:
        return str(date_value)


def format_boolean(value):
    """
    Format boolean value with emoji.

    Args:
        value: Boolean value

    Returns:
        Formatted string with emoji
    """
    if value is None:
        return "N/A"
    return "Yes" if value else "No"


def render_status_badge(is_active, is_deceased, inactive_reason=None):
    """
    Render status badge for patient.

    Args:
        is_active: Active registration status
        is_deceased: Deceased status
        inactive_reason: Reason for inactive status
    """
    if is_deceased:
        st.markdown('<span class="status-deceased">DECEASED</span>', unsafe_allow_html=True)
    elif is_active:
        st.markdown('<span class="status-active">ACTIVE</span>', unsafe_allow_html=True)
    else:
        reason = f" - {inactive_reason}" if inactive_reason else ""
        st.markdown(f'<span class="status-inactive">INACTIVE{reason}</span>', unsafe_allow_html=True)


def format_value_with_unit(value, unit):
    """
    Format observation value with unit.

    Args:
        value: Observation value
        unit: Unit of measurement

    Returns:
        Formatted string
    """
    if value is None or value == "":
        return "N/A"

    if unit and unit != "":
        return f"{value} {unit}"

    return str(value)


def safe_str(value):
    """
    Safely convert value to string.

    Args:
        value: Any value

    Returns:
        String representation or 'N/A'
    """
    if value is None or value == "":
        return "N/A"
    return str(value)
