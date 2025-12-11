"""
Patient summary page - landing page when viewing a patient record
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from services.patient_service import get_patient_demographics, get_patient_registration_history, get_patient_ltc_summary
from services.record_service import get_observation_summary, get_medication_summary, get_appointment_summary
from utils.helpers import render_status_badge, get_status_badge_html, format_date, format_boolean, safe_str, format_month_year


def render_patient_summary():
    """
    Render the patient summary page with demographics and navigation.
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

    # Load patient data with spinner (before showing any UI)
    with st.spinner("Loading patient summary..."):
        # Load patient demographics
        demographics = get_patient_demographics(person_id)

        if demographics.empty:
            st.error("Failed to load patient demographics")
            return

        patient = demographics.iloc[0]

        # Get observation, medication, and appointment summaries
        obs_summary = get_observation_summary(person_id)
        med_summary = get_medication_summary(person_id)
        appt_summary = get_appointment_summary(person_id)

    # Back button
    if st.button("← Back to Search"):
        st.session_state.page = "search"
        st.session_state.search_results = None
        st.rerun()

    # Render patient header
    render_patient_header(patient)

    # Render summary metrics
    render_summary_metrics(obs_summary, med_summary, appt_summary, patient)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation buttons to different views
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 View Observations", use_container_width=True, type="primary"):
            st.session_state.page = "observations"
            st.rerun()

    with col2:
        if st.button("💊 View Medications", use_container_width=True, type="primary"):
            st.session_state.page = "medications"
            st.rerun()

    with col3:
        if st.button("📅 View Appointments", use_container_width=True, type="primary"):
            st.session_state.page = "appointments"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Demographics details in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Core Demographics", "🏥 Registration", "📍 Geography", "🗣️ Language"])

    with tab1:
        render_core_demographics(patient)

    with tab2:
        render_registration_info(patient)
        st.markdown("<br>", unsafe_allow_html=True)
        render_registration_history(person_id)

    with tab3:
        render_geography_info(patient)

    with tab4:
        render_language_info(patient)

    st.markdown("<br>", unsafe_allow_html=True)

    # Long-term conditions summary
    render_ltc_summary(person_id)


def render_patient_header(patient):
    """
    Render patient header with basic info.

    Args:
        patient: Patient demographics row
    """
    # Get badge HTML
    badge_html = get_status_badge_html(
        patient['IS_ACTIVE'],
        patient['IS_DECEASED'],
        patient.get('INACTIVE_REASON')
    )
    
    # Title with inline status badge
    st.markdown(f"## Patient Record: {patient['PERSON_ID']} {badge_html}", unsafe_allow_html=True)
    st.markdown(f"**SK Patient ID:** {patient['SK_PATIENT_ID']}")


def render_summary_metrics(obs_summary, med_summary, appt_summary, patient):
    """
    Render summary metrics.

    Args:
        obs_summary: Observation summary dictionary
        med_summary: Medication summary dictionary
        appt_summary: Appointment summary dictionary
        patient: Patient demographics row
    """
    st.markdown("### Record Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Observations", f"{obs_summary['total_observations']:,}")

    with col2:
        current_count = med_summary['current_medications']
        total_count = med_summary['total_medications']
        st.metric("Medications (Current)", f"{current_count:,}")
        st.caption(f"Total: {total_count:,}")

    with col3:
        appts_12m = appt_summary['appointments_last_12m']
        total_appts = appt_summary['total_appointments']
        st.metric("Appointments (12m)", f"{appts_12m:,}")
        st.caption(f"All time: {total_appts:,}")

    with col4:
        most_recent_obs = obs_summary['most_recent_date']
        most_recent_med = med_summary['most_recent_date']
        most_recent_appt = appt_summary['most_recent_date']
        most_recent = max(filter(None, [most_recent_obs, most_recent_med, most_recent_appt]), default=None)
        most_recent_str = format_date(most_recent) if most_recent else "N/A"
        st.metric("Most Recent", most_recent_str)


def render_core_demographics(patient):
    """Render core demographics section."""
    # Row 1: Personal demographics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Age**")
        life_stage = safe_str(patient['AGE_LIFE_STAGE'])
        st.markdown(f"{safe_str(patient['AGE'])} years ({life_stage})")
        birth_date = format_month_year(patient['BIRTH_DATE_APPROX'])
        st.markdown(f"<small>Born: {birth_date}</small>", unsafe_allow_html=True)

    with col2:
        st.markdown("**Gender**")
        st.markdown(safe_str(patient['GENDER']))

    with col3:
        st.markdown("**Ethnicity**")
        st.markdown(safe_str(patient['ETHNICITY_SUBCATEGORY']))
        st.markdown(f"<small>{safe_str(patient['ETHNICITY_CATEGORY'])}</small>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: Practice and deceased status
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**GP Practice**")
        st.markdown(safe_str(patient['PRACTICE_NAME']))
        st.markdown(f"<small>Code: {safe_str(patient['PRACTICE_CODE'])}</small>", unsafe_allow_html=True)

    with col2:
        st.markdown("**PCN**")
        st.markdown(safe_str(patient['PCN_NAME']))

    with col3:
        st.markdown("**Deceased**")
        st.markdown(format_boolean(patient['IS_DECEASED']))
        if patient['IS_DECEASED'] and patient['DEATH_DATE_APPROX']:
            death_date = format_month_year(patient['DEATH_DATE_APPROX'])
            st.markdown(f"<small>Died: {death_date}</small>", unsafe_allow_html=True)

    # Row 3: School age (only if under 18)
    if patient['AGE'] < 18:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
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


def render_registration_history(person_id):
    """
    Render registration history as a timeline chart and details.

    Args:
        person_id: Patient identifier
    """
    history = get_patient_registration_history(person_id)

    if history.empty:
        st.info("No registration history available")
        return

    total_periods = len(history)
    
    # Prepare data for timeline chart - sort by start date
    chart_data = []
    for idx, row in history.iterrows():
        start_date = pd.to_datetime(row['EFFECTIVE_START_DATE'])
        end_date = pd.to_datetime(row['EFFECTIVE_END_DATE']) if pd.notna(row['EFFECTIVE_END_DATE']) else datetime.now()
        
        chart_data.append({
            'period': f"Period {row['PERIOD_SEQUENCE']}",
            'practice': safe_str(row['PRACTICE_NAME']),
            'start_date': start_date,
            'end_date': end_date,
            'is_current': 'Current' if row['IS_CURRENT'] else 'Past',
            'is_active': row['IS_ACTIVE'],
            'practice_code': safe_str(row['PRACTICE_CODE']),
            'pcn': safe_str(row['PCN_NAME'])
        })
    
    chart_df = pd.DataFrame(chart_data)
    chart_df = chart_df.sort_values('start_date', ascending=False)
    chart_df['row_num'] = range(len(chart_df))
    
    # Create timeline chart
    st.markdown("### Registration Timeline")
    
    # Create timeline with bars - use practice as y-axis to handle overlaps naturally
    bars = alt.Chart(chart_df).mark_bar(
        opacity=0.7
    ).encode(
        x=alt.X('start_date:T', title='Date'),
        x2='end_date:T',
        y=alt.Y('row_num:O', title='Period', axis=alt.Axis(labels=False, ticks=False)),
        color=alt.Color(
            'is_current:N',
            scale=alt.Scale(
                domain=['Current', 'Past'],
                range=['#28a745', '#6c757d']
            ),
            legend=alt.Legend(title="Status")
        ),
        tooltip=[
            alt.Tooltip('period:N', title='Period'),
            alt.Tooltip('practice:N', title='Practice'),
            alt.Tooltip('practice_code:N', title='Code'),
            alt.Tooltip('pcn:N', title='PCN'),
            alt.Tooltip('start_date:T', title='Start', format='%d %b %Y'),
            alt.Tooltip('end_date:T', title='End', format='%d %b %Y')
        ]
    ).properties(
        height=max(300, len(chart_df) * 50),
        width="container"
    )
    
    # Add period labels on the left
    period_labels = alt.Chart(chart_df).mark_text(
        align='right',
        baseline='middle',
        dx=-5
    ).encode(
        x=alt.X('start_date:T', aggregate='min', title=''),
        y=alt.Y('row_num:O', sort=None),
        text=alt.Text('period:N'),
        color=alt.value('black')
    )
    
    # Add practice labels on the bars
    practice_labels = alt.Chart(chart_df).mark_text(
        align='left',
        baseline='middle',
        dx=5,
        fontSize=10
    ).encode(
        x='start_date:T',
        y=alt.Y('row_num:O', sort=None),
        text=alt.Text('practice:N'),
        color=alt.value('black')
    )
    
    timeline_chart = (bars + period_labels + practice_labels).configure_view(strokeWidth=0)
    
    st.altair_chart(timeline_chart, use_container_width=True)
    
    st.caption(f"Showing {total_periods} registration period(s)")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed history in expandable section
    with st.expander("📜 View Detailed Registration History", expanded=False):
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


def render_ltc_summary(person_id):
    """
    Render long-term conditions summary section.

    Args:
        person_id: Patient identifier
    """
    ltc_data = get_patient_ltc_summary(person_id)

    if ltc_data.empty:
        return

    st.markdown("### 🏥 Long-Term Conditions")

    # Group by clinical domain
    domains = ltc_data['CLINICAL_DOMAIN'].unique()

    for domain in sorted(domains):
        domain_conditions = ltc_data[ltc_data['CLINICAL_DOMAIN'] == domain]

        st.markdown(f"**{domain}**")

        # Display conditions as badges
        badges_html = ""
        for _, condition in domain_conditions.iterrows():
            qof_class = "condition-qof" if condition['IS_QOF'] else "condition-other"
            qof_badge = ' <span style="background-color: #084298; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75rem; margin-left: 4px;">QOF</span>' if condition['IS_QOF'] else ""
            earliest = format_date(condition['EARLIEST_DIAGNOSIS_DATE'])

            badges_html += f'<span class="condition-badge {qof_class}">{condition["CONDITION_NAME"]}{qof_badge}<br><small>Dx: {earliest}</small></span>'

        st.markdown(badges_html, unsafe_allow_html=True)
        st.markdown("")
