"""
Medications view page
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.record_service import get_patient_medications, calculate_date_range
from utils.helpers import format_date, safe_str, format_practitioner_name
from config import DATE_RANGE_OPTIONS


def render_medications():
    """
    Render the medications view page.
    """
    # Check if patient is selected
    if "selected_patient" not in st.session_state or not st.session_state.selected_patient:
        st.warning("No patient selected. Please search for a patient first.")
        if st.button("Back to Search"):
            st.session_state.page = "search"
            st.rerun()
        return

    person_id = st.session_state.selected_patient

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("← Back to Summary"):
            st.session_state.page = "patient_summary"
            st.rerun()
    with col2:
        if st.button("← Back to Search"):
            st.session_state.page = "search"
            st.session_state.search_results = None
            st.rerun()

    st.markdown(f"## 💊 Medications for Patient: {person_id}")

    # Filters
    st.markdown("### Filters")
    col1, col2 = st.columns([2, 3])

    with col1:
        date_range = st.selectbox(
            "Date Range",
            options=list(DATE_RANGE_OPTIONS.keys()),
            index=0
        )

    with col2:
        search_term = st.text_input(
            "Search by code or description",
            placeholder="e.g., medication name or SNOMED code",
            key="med_search"
        )

    # Calculate date range
    date_from, date_to = calculate_date_range(date_range)

    # Load medications
    with st.spinner("Loading medications..."):
        medications = get_patient_medications(person_id, date_from, date_to, search_term)

    if medications.empty:
        st.info("No medications found for the selected filters")
    else:
        st.markdown(f"**Showing {len(medications):,} medications** (limited to 10,000 most recent)")

        # Prepare display dataframe
        display_df = medications.copy()

        # Calculate medication status based on cancellation, expiry, and duration
        def calculate_medication_status(row):
            try:
                today = datetime.now()

                # Check if cancelled
                if not pd.isna(row['CANCELLATION_DATE']):
                    cancellation_date = pd.to_datetime(row['CANCELLATION_DATE'])
                    if cancellation_date <= today:
                        return "Cancelled"

                # Check statement expiry date
                if not pd.isna(row['EXPIRY_DATE']):
                    expiry_date = pd.to_datetime(row['EXPIRY_DATE'])
                    if expiry_date < today:
                        return "Expired"

                # Check statement is_active flag
                if not pd.isna(row['STATEMENT_IS_ACTIVE']) and row['STATEMENT_IS_ACTIVE'] == False:
                    return "Inactive"

                # Check duration-based expiry
                if not pd.isna(row['CLINICAL_EFFECTIVE_DATE']) and not pd.isna(row['DURATION_DAYS']):
                    start_date = pd.to_datetime(row['CLINICAL_EFFECTIVE_DATE'])
                    duration_days = int(row['DURATION_DAYS'])
                    end_date = start_date + timedelta(days=duration_days)

                    if today <= end_date:
                        return "Active"
                    else:
                        return "Expired"

                return "Unknown"
            except:
                return "Unknown"

        display_df['STATUS'] = display_df.apply(calculate_medication_status, axis=1)

        # Format date for display
        display_df['DATE_DISPLAY'] = display_df['CLINICAL_EFFECTIVE_DATE'].apply(format_date)

        # Format prescription type - use statement_issue_method as primary source
        display_df['TYPE'] = display_df.apply(
            lambda row: safe_str(row['STATEMENT_ISSUE_METHOD'])
            if row['STATEMENT_ISSUE_METHOD'] and row['STATEMENT_ISSUE_METHOD'] != 'N/A'
            else safe_str(row['ISSUE_METHOD']),
            axis=1
        )

        # Format dose and quantity
        display_df['DOSE_INFO'] = display_df['DOSE'].apply(safe_str)
        display_df['QUANTITY_INFO'] = display_df.apply(
            lambda row: f"{safe_str(row['QUANTITY_VALUE'])} {safe_str(row['QUANTITY_UNIT'])}"
            if row['QUANTITY_VALUE'] and row['QUANTITY_UNIT'] else safe_str(row['QUANTITY_VALUE']),
            axis=1
        )

        # Format duration if available
        display_df['DURATION_INFO'] = display_df.apply(
            lambda row: f"{int(row['DURATION_DAYS'])} days"
            if row['DURATION_DAYS'] and str(row['DURATION_DAYS']) != 'nan' else "",
            axis=1
        )

        # Format practitioner name
        display_df['PRACTITIONER'] = display_df.apply(
            lambda row: format_practitioner_name(
                row['PRACTITIONER_LAST_NAME'],
                row['PRACTITIONER_FIRST_NAME'],
                row['PRACTITIONER_TITLE']
            ),
            axis=1
        )

        # Select and rename columns for display
        display_df = display_df[[
            'DATE_DISPLAY',
            'STATUS',
            'TYPE',
            'MAPPED_CONCEPT_DISPLAY',
            'DOSE_INFO',
            'QUANTITY_INFO',
            'DURATION_INFO',
            'PRACTITIONER'
        ]]
        display_df.columns = ['Date', 'Status', 'Type', 'Medication', 'Dose', 'Quantity', 'Duration', 'Prescriber']

        # Display table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
