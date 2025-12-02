"""
Patient search page
"""

import streamlit as st
from services.patient_service import search_patient
from utils.helpers import render_status_badge, safe_str


def render_search():
    """
    Render the patient search page.
    """
    st.title("OLIDS Patient Record Explorer")

    st.markdown("### Patient Search")
    st.markdown("Search for a patient by entering their **person_id** or **sk_patient_id**")

    # Search container
    st.markdown('<div class="search-container">', unsafe_allow_html=True)

    # Search input
    search_term = st.text_input(
        "Patient Identifier",
        placeholder="Enter person_id or sk_patient_id",
        key="search_input",
        label_visibility="collapsed"
    )

    # Search button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        search_clicked = st.button("Search", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Perform search
    if search_clicked and search_term:
        with st.spinner("Searching..."):
            results = search_patient(search_term)

            if results.empty:
                st.warning(f"No patient found with identifier: {search_term}")
            else:
                # Display results
                st.markdown("---")
                st.markdown("### Search Results")

                for idx, row in results.iterrows():
                    render_patient_card(row)

    elif search_clicked and not search_term:
        st.warning("Please enter a patient identifier to search")

    # Display instructions
    if not search_clicked:
        st.markdown("---")
        st.markdown("#### Instructions")
        st.markdown("""
        - Enter a **person_id** (text identifier) or **sk_patient_id** (numeric identifier)
        - Click **Search** to find the patient
        - Click **View Record** on a result to view the patient's complete record
        """)


def render_patient_card(patient_row):
    """
    Render a patient search result card.

    Args:
        patient_row: Pandas Series with patient data
    """
    with st.container():
        # Patient header
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"#### Patient: {patient_row['PERSON_ID']}")
            st.markdown(f"**SK Patient ID:** {patient_row['SK_PATIENT_ID']}")

        with col2:
            render_status_badge(
                patient_row['IS_ACTIVE'],
                patient_row['IS_DECEASED'],
                patient_row.get('INACTIVE_REASON')
            )

        # Demographics summary
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Age", safe_str(patient_row['AGE']))

        with col2:
            st.metric("Gender", safe_str(patient_row['GENDER']))

        with col3:
            st.metric("Ethnicity", safe_str(patient_row['ETHNICITY_SUBCATEGORY']))

        with col4:
            # View record button
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("View Record", key=f"view_{patient_row['PERSON_ID']}", type="primary"):
                st.session_state.page = "patient_record"
                st.session_state.selected_patient = patient_row['PERSON_ID']
                st.rerun()

        # Practice info
        st.markdown(f"**Practice:** {safe_str(patient_row['PRACTICE_NAME'])}")
        st.markdown(f"**PCN:** {safe_str(patient_row['PCN_NAME'])}")

        st.markdown("---")
