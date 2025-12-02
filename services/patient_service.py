"""
Patient search and demographics service
"""

import streamlit as st
import pandas as pd
from config import TABLE_DIM_PERSON, TABLE_DIM_PERSON_HISTORICAL, TABLE_LTC_SUMMARY
from database import get_connection


def search_patient(search_term):
    """
    Search for patient by person_id or sk_patient_id.

    Args:
        search_term: Either person_id or sk_patient_id

    Returns:
        DataFrame with patient search results
    """
    conn = get_connection()

    try:
        # Try to convert to integer for sk_patient_id search
        search_int = int(search_term)
        query = f"""
        SELECT
            person_id,
            sk_patient_id,
            age,
            gender,
            is_active,
            is_deceased,
            inactive_reason,
            practice_name,
            pcn_name,
            ethnicity_subcategory
        FROM {TABLE_DIM_PERSON}
        WHERE person_id = '{search_term}' OR sk_patient_id = {search_int}
        """
    except ValueError:
        # Not an integer, search only by person_id
        query = f"""
        SELECT
            person_id,
            sk_patient_id,
            age,
            gender,
            is_active,
            is_deceased,
            inactive_reason,
            practice_name,
            pcn_name,
            ethnicity_subcategory
        FROM {TABLE_DIM_PERSON}
        WHERE person_id = '{search_term}'
        """

    try:
        result = conn.sql(query).to_pandas()
        return result
    except Exception as e:
        st.error(f"Error searching for patient: {str(e)}")
        return pd.DataFrame()


def get_patient_demographics(person_id):
    """
    Get full demographics for a patient.

    Args:
        person_id: Patient identifier

    Returns:
        DataFrame with full patient demographics
    """
    conn = get_connection()

    query = f"""
    SELECT *
    FROM {TABLE_DIM_PERSON}
    WHERE person_id = '{person_id}'
    """

    try:
        result = conn.sql(query).to_pandas()
        if result.empty:
            st.error(f"Patient {person_id} not found")
            return pd.DataFrame()
        return result
    except Exception as e:
        st.error(f"Error loading patient demographics: {str(e)}")
        return pd.DataFrame()


def get_patient_registration_history(person_id):
    """
    Get registration history for a patient from historical table.

    Args:
        person_id: Patient identifier

    Returns:
        DataFrame with registration history
    """
    conn = get_connection()

    query = f"""
    SELECT
        effective_start_date,
        effective_end_date,
        is_current,
        period_sequence,
        is_active,
        practice_name,
        practice_code,
        pcn_name,
        registration_start_date,
        registration_end_date,
        ethnicity_subcategory,
        borough_registered,
        borough_resident,
        local_authority_name
    FROM {TABLE_DIM_PERSON_HISTORICAL}
    WHERE person_id = '{person_id}'
    ORDER BY effective_start_date DESC
    """

    try:
        result = conn.sql(query).to_pandas()
        return result
    except Exception as e:
        st.warning(f"Could not load registration history: {str(e)}")
        return pd.DataFrame()

def get_patient_ltc_summary(person_id):
    """
    Get long-term conditions summary for a patient.

    Args:
        person_id: Patient identifier

    Returns:
        DataFrame with LTC conditions
    """
    conn = get_connection()

    query = f"""
    SELECT
        condition_code,
        condition_name,
        clinical_domain,
        is_on_register,
        is_qof,
        earliest_diagnosis_date,
        latest_diagnosis_date
    FROM {TABLE_LTC_SUMMARY}
    WHERE person_id = '{person_id}'
        AND is_on_register = TRUE
    ORDER BY
        is_qof DESC,
        clinical_domain,
        condition_name
    """

    try:
        result = conn.sql(query).to_pandas()
        return result
    except Exception as e:
        st.warning(f"Could not load LTC summary: {str(e)}")
        return pd.DataFrame()
