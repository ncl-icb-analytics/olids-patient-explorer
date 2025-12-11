"""
Patient search and demographics service
"""

import streamlit as st
import pandas as pd
from config import TABLE_DIM_PERSON, TABLE_DIM_PERSON_HISTORICAL, TABLE_LTC_SUMMARY
from database import get_connection


def search_patient(search_term):
    """
    Search for patient by sk_patient_id or person_id.

    Args:
        search_term: Either sk_patient_id (integer) or person_id (string)

    Returns:
        DataFrame with patient search results
    """
    conn = get_connection()

    try:
        # Try to convert to integer for sk_patient_id search (primary)
        search_int = int(search_term)
        query = f"""
        SELECT
            person_id,
            sk_patient_id,
            age,
            gender,
            birth_date_approx,
            is_active,
            is_deceased,
            inactive_reason,
            practice_name,
            pcn_name,
            ethnicity_subcategory
        FROM {TABLE_DIM_PERSON}
        WHERE sk_patient_id = {search_int} OR person_id = '{search_term}'
        """
    except ValueError:
        # Not an integer, search by person_id (fallback)
        query = f"""
        SELECT
            person_id,
            sk_patient_id,
            age,
            gender,
            birth_date_approx,
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


def get_patient_demographics(sk_patient_id):
    """
    Get full demographics for a patient.

    Args:
        sk_patient_id: Patient identifier (sk_patient_id)

    Returns:
        DataFrame with full patient demographics
    """
    conn = get_connection()

    query = f"""
    SELECT *
    FROM {TABLE_DIM_PERSON}
    WHERE sk_patient_id = {sk_patient_id}
    """

    try:
        result = conn.sql(query).to_pandas()
        if result.empty:
            st.error(f"Patient {sk_patient_id} not found")
            return pd.DataFrame()
        return result
    except Exception as e:
        st.error(f"Error loading patient demographics: {str(e)}")
        return pd.DataFrame()


def get_patient_registration_history(sk_patient_id):
    """
    Get registration history for a patient from historical table.

    Args:
        sk_patient_id: Patient identifier (sk_patient_id)

    Returns:
        DataFrame with registration history
    """
    conn = get_connection()

    # First get person_id from sk_patient_id
    person_lookup = conn.sql(f"""
        SELECT person_id
        FROM {TABLE_DIM_PERSON}
        WHERE sk_patient_id = {sk_patient_id}
        LIMIT 1
    """).to_pandas()
    
    if person_lookup.empty:
        return pd.DataFrame()
    
    person_id = person_lookup.iloc[0]['PERSON_ID']

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

def get_patient_ltc_summary(sk_patient_id):
    """
    Get long-term conditions summary for a patient.

    Args:
        sk_patient_id: Patient identifier (sk_patient_id)

    Returns:
        DataFrame with LTC conditions
    """
    conn = get_connection()

    # First get person_id from sk_patient_id
    person_lookup = conn.sql(f"""
        SELECT person_id
        FROM {TABLE_DIM_PERSON}
        WHERE sk_patient_id = {sk_patient_id}
        LIMIT 1
    """).to_pandas()
    
    if person_lookup.empty:
        return pd.DataFrame()
    
    person_id = person_lookup.iloc[0]['PERSON_ID']

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
