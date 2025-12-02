"""
Patient records service for observations and medications
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from config import TABLE_OBSERVATION, TABLE_MEDICATION_ORDER, TABLE_MEDICATION_STATEMENT, MAX_OBSERVATIONS
from database import get_connection


def get_observation_summary(person_id):
    """
    Get summary statistics for patient observations.

    Args:
        person_id: Patient identifier

    Returns:
        Dictionary with summary stats
    """
    conn = get_connection()

    query = f"""
    SELECT
        COUNT(*) as total_observations,
        MIN(clinical_effective_date) as earliest_date,
        MAX(clinical_effective_date) as most_recent_date
    FROM {TABLE_OBSERVATION}
    WHERE person_id = '{person_id}'
    """

    try:
        result = conn.sql(query).to_pandas()
        if result.empty:
            return {
                "total_observations": 0,
                "earliest_date": None,
                "most_recent_date": None
            }

        row = result.iloc[0]
        return {
            "total_observations": int(row["TOTAL_OBSERVATIONS"]),
            "earliest_date": row["EARLIEST_DATE"],
            "most_recent_date": row["MOST_RECENT_DATE"]
        }
    except Exception as e:
        st.error(f"Error loading observation summary: {str(e)}")
        return {
            "total_observations": 0,
            "earliest_date": None,
            "most_recent_date": None
        }


def get_patient_observations(person_id, date_from=None, date_to=None, search_term=""):
    """
    Get observations for a patient with optional filters.

    Args:
        person_id: Patient identifier
        date_from: Start date filter (optional)
        date_to: End date filter (optional)
        search_term: Search term for code or description (optional)

    Returns:
        DataFrame with observations
    """
    conn = get_connection()

    # Build WHERE clause
    where_clauses = [f"o.person_id = '{person_id}'"]

    if date_from:
        where_clauses.append(f"o.clinical_effective_date >= '{date_from}'")

    if date_to:
        where_clauses.append(f"o.clinical_effective_date <= '{date_to}'")

    if search_term and search_term.strip():
        search_pattern = f"%{search_term}%"
        where_clauses.append(
            f"(o.mapped_concept_code ILIKE '{search_pattern}' "
            f"OR o.mapped_concept_display ILIKE '{search_pattern}')"
        )

    where_sql = " AND ".join(where_clauses)

    query = f"""
    SELECT
        o.clinical_effective_date,
        o.mapped_concept_code,
        o.mapped_concept_display,
        o.result_value,
        o.result_text,
        o.result_unit_display,
        o.id
    FROM {TABLE_OBSERVATION} o
    WHERE {where_sql}
    ORDER BY o.clinical_effective_date DESC
    LIMIT {MAX_OBSERVATIONS}
    """

    try:
        result = conn.sql(query).to_pandas()
        return result
    except Exception as e:
        st.error(f"Error loading observations: {str(e)}")
        return pd.DataFrame()


def get_medication_summary(person_id):
    """
    Get summary statistics for patient medications.

    Args:
        person_id: Patient identifier

    Returns:
        Dictionary with summary stats
    """
    conn = get_connection()

    query = f"""
    SELECT
        COUNT(*) as total_medications,
        MIN(clinical_effective_date) as earliest_date,
        MAX(clinical_effective_date) as most_recent_date
    FROM {TABLE_MEDICATION_ORDER}
    WHERE person_id = '{person_id}'
    """

    try:
        result = conn.sql(query).to_pandas()
        if result.empty:
            return {
                "total_medications": 0,
                "earliest_date": None,
                "most_recent_date": None
            }

        row = result.iloc[0]
        return {
            "total_medications": int(row["TOTAL_MEDICATIONS"]),
            "earliest_date": row["EARLIEST_DATE"],
            "most_recent_date": row["MOST_RECENT_DATE"]
        }
    except Exception as e:
        st.error(f"Error loading medication summary: {str(e)}")
        return {
            "total_medications": 0,
            "earliest_date": None,
            "most_recent_date": None
        }


def get_patient_medications(person_id, date_from=None, date_to=None, search_term=""):
    """
    Get medications for a patient with optional filters.

    Args:
        person_id: Patient identifier
        date_from: Start date filter (optional)
        date_to: End date filter (optional)
        search_term: Search term for code or description (optional)

    Returns:
        DataFrame with medications
    """
    conn = get_connection()

    # Build WHERE clause
    where_clauses = [f"m.person_id = '{person_id}'"]

    if date_from:
        where_clauses.append(f"m.clinical_effective_date >= '{date_from}'")

    if date_to:
        where_clauses.append(f"m.clinical_effective_date <= '{date_to}'")

    if search_term and search_term.strip():
        search_pattern = f"%{search_term}%"
        where_clauses.append(
            f"(m.mapped_concept_code ILIKE '{search_pattern}' "
            f"OR m.mapped_concept_display ILIKE '{search_pattern}')"
        )

    where_sql = " AND ".join(where_clauses)

    query = f"""
    SELECT
        m.clinical_effective_date,
        m.mapped_concept_code,
        m.mapped_concept_display,
        m.dose,
        m.quantity_value,
        m.quantity_unit,
        m.duration_days,
        m.estimated_cost,
        m.issue_method_description,
        ms.bnf_reference,
        ms.issue_method as statement_issue_method,
        ms.is_active as statement_is_active,
        m.id
    FROM {TABLE_MEDICATION_ORDER} m
    LEFT JOIN {TABLE_MEDICATION_STATEMENT} ms
        ON m.medication_statement_id = ms.id
    WHERE {where_sql}
    ORDER BY m.clinical_effective_date DESC
    LIMIT {MAX_OBSERVATIONS}
    """

    try:
        result = conn.sql(query).to_pandas()
        return result
    except Exception as e:
        st.error(f"Error loading medications: {str(e)}")
        return pd.DataFrame()


def calculate_date_range(range_option):
    """
    Calculate date range based on selection.

    Args:
        range_option: Selected date range option

    Returns:
        Tuple of (date_from, date_to) or (None, None) for all time
    """
    from config import DATE_RANGE_OPTIONS

    days = DATE_RANGE_OPTIONS.get(range_option)

    if days is None:
        return None, None

    date_to = datetime.now().date()
    date_from = date_to - timedelta(days=days)

    return date_from, date_to
