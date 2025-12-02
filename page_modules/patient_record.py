"""
Patient record view page
"""

import streamlit as st
import pandas as pd
from services.patient_service import get_patient_demographics, get_patient_registration_history
from services.record_service import get_observation_summary, get_patient_observations, calculate_date_range
from utils.helpers import render_status_badge, format_date, format_boolean, safe_str, format_value_with_unit
from config import DATE_RANGE_OPTIONS


def render_patient_record():
    """
    Render the patient record view page.
    """
    # Check if patient is selected
    if "selected_patient" not in st.session_state or not st.session_state.selected_patient:
        st.warning("No patient selected. Please search for a patient first.")
        if st.button("Back to Search"):
            st.session_state.page = "search"
            st.session_state.search_results = None
            st.rerun()
        return

    person_id = st.session_state.selected_patient

    # Back button
    if st.button("← Back to Search"):
        st.session_state.page = "search"
        st.session_state.search_results = None
        st.rerun()

    # Load patient demographics
    demographics = get_patient_demographics(person_id)

    if demographics.empty:
        st.error("Failed to load patient demographics")
        return

    patient = demographics.iloc[0]

    # Render patient header
    render_patient_header(patient)

    # Get observation summary
    summary = get_observation_summary(person_id)

    # Render summary metrics
    render_summary_metrics(summary, patient)

    # Registration history (optional expandable section)
    render_registration_history(person_id)

    # Render observations section
    render_observations_section(person_id)


def render_patient_header(patient):
    """
    Render patient header with demographics.

    Args:
        patient: Patient demographics row
    """
    st.markdown('<div class="patient-header">', unsafe_allow_html=True)

    # Title and status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## Patient Record: {patient['PERSON_ID']}")
        st.markdown(f"**SK Patient ID:** {patient['SK_PATIENT_ID']}")
    with col2:
        render_status_badge(
            patient['IS_ACTIVE'],
            patient['IS_DECEASED'],
            patient.get('INACTIVE_REASON')
        )

    st.markdown("---")

    # Core demographics in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Core Demographics", "🏥 Registration", "📍 Geography", "🗣️ Language"])

    with tab1:
        render_core_demographics(patient)

    with tab2:
        render_registration_info(patient)

    with tab3:
        render_geography_info(patient)

    with tab4:
        render_language_info(patient)

    st.markdown('</div>', unsafe_allow_html=True)


def render_core_demographics(patient):
    """Render core demographics section."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**Age**")
        st.markdown(f"{safe_str(patient['AGE'])} years")
        st.markdown(f"<small>Born: {safe_str(patient['BIRTH_YEAR'])}</small>", unsafe_allow_html=True)

    with col2:
        st.markdown("**Gender**")
        st.markdown(safe_str(patient['GENDER']))

    with col3:
        st.markdown("**Ethnicity**")
        st.markdown(safe_str(patient['ETHNICITY_SUBCATEGORY']))
        st.markdown(f"<small>{safe_str(patient['ETHNICITY_CATEGORY'])}</small>", unsafe_allow_html=True)

    with col4:
        st.markdown("**Life Stage**")
        st.markdown(safe_str(patient['AGE_LIFE_STAGE']))
        st.markdown(f"<small>{safe_str(patient['AGE_BAND_NHS'])}</small>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Deceased**")
        st.markdown(format_boolean(patient['IS_DECEASED']))
        if patient['IS_DECEASED'] and patient['DEATH_YEAR']:
            st.markdown(f"<small>Year: {safe_str(patient['DEATH_YEAR'])}</small>", unsafe_allow_html=True)

    with col2:
        st.markdown("**Dummy Patient**")
        st.markdown(format_boolean(patient['IS_DUMMY_PATIENT']))

    with col3:
        st.markdown("**School Age**")
        primary = format_boolean(patient['IS_PRIMARY_SCHOOL_AGE'])
        secondary = format_boolean(patient['IS_SECONDARY_SCHOOL_AGE'])
        st.markdown(f"Primary: {primary}")
        st.markdown(f"Secondary: {secondary}")


def render_registration_info(patient):
    """Render registration information section."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Practice**")
        st.markdown(safe_str(patient['PRACTICE_NAME']))
        st.markdown(f"<small>Code: {safe_str(patient['PRACTICE_CODE'])}</small>", unsafe_allow_html=True)

        st.markdown("<br>**PCN**", unsafe_allow_html=True)
        st.markdown(safe_str(patient['PCN_NAME']))
        st.markdown(f"<small>Code: {safe_str(patient['PCN_CODE'])}</small>", unsafe_allow_html=True)

    with col2:
        st.markdown("**Registration Dates**")
        st.markdown(f"Start: {format_date(patient['REGISTRATION_START_DATE'])}")
        st.markdown(f"End: {format_date(patient['REGISTRATION_END_DATE'])}")

        st.markdown("<br>**ICB**", unsafe_allow_html=True)
        st.markdown(safe_str(patient['ICB_NAME']))
        st.markdown(f"<small>{safe_str(patient['BOROUGH_REGISTERED'])}</small>", unsafe_allow_html=True)


def render_geography_info(patient):
    """Render geography information section."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Resident Location**")
        st.markdown(f"Borough: {safe_str(patient['BOROUGH_RESIDENT'])}")
        st.markdown(f"ICB: {safe_str(patient['ICB_RESIDENT'])}")
        st.markdown(f"Local Authority: {safe_str(patient['LOCAL_AUTHORITY_NAME'])}")
        st.markdown(f"London Resident: {format_boolean(patient['IS_LONDON_RESIDENT'])}")

    with col2:
        st.markdown("**Area Classifications**")
        st.markdown(f"Neighbourhood: {safe_str(patient['NEIGHBOURHOOD_RESIDENT'])}")
        st.markdown(f"LSOA: {safe_str(patient['LSOA_NAME_21'])}")
        st.markdown(f"Ward: {safe_str(patient['WARD_NAME'])}")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Deprivation (IMD 2019)**")
        st.markdown(f"Quintile: {safe_str(patient['IMD_QUINTILE_19'])}")
        st.markdown(f"Decile: {safe_str(patient['IMD_DECILE_19'])}")


def render_language_info(patient):
    """Render language information section."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Main Language**")
        st.markdown(safe_str(patient['MAIN_LANGUAGE']))
        st.markdown(f"<small>Type: {safe_str(patient['LANGUAGE_TYPE'])}</small>", unsafe_allow_html=True)

    with col2:
        st.markdown("**Interpreter**")
        st.markdown(f"Needed: {format_boolean(patient['INTERPRETER_NEEDED'])}")
        if patient['INTERPRETER_NEEDED']:
            st.markdown(f"Type: {safe_str(patient['INTERPRETER_TYPE'])}")


def render_summary_metrics(summary, patient):
    """
    Render summary metrics.

    Args:
        summary: Observation summary dictionary
        patient: Patient demographics row
    """
    st.markdown("### Record Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Observations", f"{summary['total_observations']:,}")

    with col2:
        earliest = format_date(summary['earliest_date']) if summary['earliest_date'] else "N/A"
        st.metric("Earliest Record", earliest)

    with col3:
        most_recent = format_date(summary['most_recent_date']) if summary['most_recent_date'] else "N/A"
        st.metric("Most Recent Record", most_recent)

    with col4:
        status = "Active" if patient['IS_ACTIVE'] else "Inactive"
        st.metric("Registration Status", status)


def render_registration_history(person_id):
    """
    Render registration history expandable section.

    Args:
        person_id: Patient identifier
    """
    with st.expander("📜 Registration History", expanded=False):
        history = get_patient_registration_history(person_id)

        if history.empty:
            st.info("No registration history available")
        else:
            st.markdown(f"**{len(history)} registration periods found**")
            st.markdown("<br>", unsafe_allow_html=True)

            for idx, row in history.iterrows():
                current_badge = " 🟢 **CURRENT**" if row['IS_CURRENT'] else ""
                active_status = "Active" if row['IS_ACTIVE'] else "Inactive"

                st.markdown(f"#### Period {row['PERIOD_SEQUENCE']}{current_badge}")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Effective Dates**")
                    st.markdown(f"Start: {format_date(row['EFFECTIVE_START_DATE'])}")
                    st.markdown(f"End: {format_date(row['EFFECTIVE_END_DATE'])}")

                    st.markdown(f"<br>**Registration**", unsafe_allow_html=True)
                    st.markdown(f"Start: {format_date(row['REGISTRATION_START_DATE'])}")
                    st.markdown(f"End: {format_date(row['REGISTRATION_END_DATE'])}")
                    st.markdown(f"Status: {active_status}")

                with col2:
                    st.markdown(f"**Practice**")
                    st.markdown(f"{safe_str(row['PRACTICE_NAME'])}")
                    st.markdown(f"<small>Code: {safe_str(row['PRACTICE_CODE'])}</small>", unsafe_allow_html=True)

                    st.markdown(f"<br>**Location**", unsafe_allow_html=True)
                    st.markdown(f"PCN: {safe_str(row['PCN_NAME'])}")
                    st.markdown(f"Borough: {safe_str(row['BOROUGH_REGISTERED'])}")

                if idx < len(history) - 1:
                    st.markdown("---")


def render_observations_section(person_id):
    """
    Render observations section with filters and table.

    Args:
        person_id: Patient identifier
    """
    st.markdown("---")
    st.markdown("### Observations")

    # Filters
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
            placeholder="e.g., '38341003' or 'blood pressure'",
            key="obs_search"
        )

    # Calculate date range
    date_from, date_to = calculate_date_range(date_range)

    # Load observations
    with st.spinner("Loading observations..."):
        observations = get_patient_observations(person_id, date_from, date_to, search_term)

    if observations.empty:
        st.info("No observations found for the selected filters")
    else:
        st.markdown(f"**Showing {len(observations):,} observations** (limited to 1,000 most recent)")

        # Prepare display dataframe
        display_df = observations.copy()
        display_df['CLINICAL_EFFECTIVE_DATE'] = display_df['CLINICAL_EFFECTIVE_DATE'].apply(format_date)

        # Combine result_value and result_text, preferring numeric value if present
        display_df['VALUE'] = display_df.apply(
            lambda row: format_value_with_unit(
                row['RESULT_VALUE'] if pd.notna(row['RESULT_VALUE']) else row['RESULT_TEXT'],
                row['RESULT_UNIT_DISPLAY']
            ),
            axis=1
        )

        # Select and rename columns for display
        display_df = display_df[[
            'CLINICAL_EFFECTIVE_DATE',
            'MAPPED_CONCEPT_CODE',
            'MAPPED_CONCEPT_DISPLAY',
            'VALUE'
        ]]
        display_df.columns = ['Date', 'SNOMED Code', 'Description', 'Value']

        # Display table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
