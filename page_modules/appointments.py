"""
Appointments view page
"""

import streamlit as st
import pandas as pd
import altair as alt
from services.record_service import get_patient_appointments, calculate_date_range
from utils.helpers import format_date, safe_str, format_practitioner_name
from config import DATE_RANGE_OPTIONS


def render_appointments():
    """
    Render the appointments view page with visualization and table.
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

    st.markdown(f"## 📅 Appointments for Patient: {person_id}")

    # Filters
    st.markdown("### Filters")
    date_range = st.selectbox(
        "Date Range",
        options=list(DATE_RANGE_OPTIONS.keys()),
        index=0
    )

    # Calculate date range
    date_from, date_to = calculate_date_range(date_range)

    # Load appointments
    with st.spinner("Loading appointments..."):
        appointments = get_patient_appointments(person_id, date_from, date_to)

    if appointments.empty:
        st.info("No appointments found for the selected filters")
    else:
        st.markdown(f"**Showing {len(appointments):,} appointments** (limited to 10,000 most recent)")

        # Prepare display dataframe
        display_df = appointments.copy()

        # Convert start_date to datetime for plotting
        display_df["START_DATE"] = pd.to_datetime(display_df["START_DATE"])

        # Create year-month for grouping
        display_df["YEAR_MONTH"] = display_df["START_DATE"].dt.to_period("M").astype(str)

        # Map status concepts to readable names
        status_mapping = {
            "booked": "Booked",
            "arrived": "Arrived",
            "fulfilled": "Fulfilled",
            "cancelled": "Cancelled",
            "noshow": "No Show",
            "entered-in-error": "Error"
        }
        display_df["STATUS"] = display_df["APPOINTMENT_STATUS_CONCEPT_ID"].apply(
            lambda x: status_mapping.get(str(x).lower(), safe_str(x)) if pd.notna(x) else "Unknown"
        )

        # Clean up slot category names
        display_df["SLOT_CATEGORY"] = display_df["NATIONAL_SLOT_CATEGORY_NAME"].apply(
            lambda x: safe_str(x) if x and x != "N/A" else "Not Specified"
        )

        # Visualization Section
        st.markdown("### 📊 Appointment Trends")

        # Group by month and status
        status_counts = display_df.groupby(["YEAR_MONTH", "STATUS"]).size().reset_index(name="COUNT")

        # Create timeline chart colored by status using Altair
        status_chart = alt.Chart(status_counts).mark_bar().encode(
            x=alt.X("YEAR_MONTH:N", title="Month", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("COUNT:Q", title="Number of Appointments"),
            color=alt.Color("STATUS:N", title="Status"),
            tooltip=["YEAR_MONTH:N", "STATUS:N", "COUNT:Q"]
        ).properties(
            title="Appointments Over Time by Status",
            height=400
        )
        st.altair_chart(status_chart, use_container_width=True)

        # Second chart: by slot category
        slot_counts = display_df.groupby(["YEAR_MONTH", "SLOT_CATEGORY"]).size().reset_index(name="COUNT")

        slot_chart = alt.Chart(slot_counts).mark_bar().encode(
            x=alt.X("YEAR_MONTH:N", title="Month", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("COUNT:Q", title="Number of Appointments"),
            color=alt.Color("SLOT_CATEGORY:N", title="Slot Category"),
            tooltip=["YEAR_MONTH:N", "SLOT_CATEGORY:N", "COUNT:Q"]
        ).properties(
            title="Appointments Over Time by Slot Category",
            height=400
        )
        st.altair_chart(slot_chart, use_container_width=True)

        st.markdown("### 📋 Appointment Details")

        # Format for table display
        display_df["DATE_DISPLAY"] = display_df["START_DATE"].apply(
            lambda x: x.strftime("%d %b %Y %H:%M") if pd.notna(x) else "N/A"
        )

        # Map contact mode
        contact_mapping = {
            "face-to-face": "Face-to-Face",
            "telephone": "Telephone",
            "video": "Video",
            "online": "Online"
        }
        display_df["CONTACT_MODE"] = display_df["CONTACT_MODE_CONCEPT_ID"].apply(
            lambda x: contact_mapping.get(str(x).lower(), safe_str(x)) if pd.notna(x) else "Not Specified"
        )

        # Format practitioner name
        display_df["PRACTITIONER"] = display_df.apply(
            lambda row: format_practitioner_name(
                row["PRACTITIONER_LAST_NAME"],
                row["PRACTITIONER_FIRST_NAME"],
                row["PRACTITIONER_TITLE"]
            ),
            axis=1
        )

        # Format duration
        display_df["DURATION"] = display_df["PLANNED_DURATION"].apply(
            lambda x: f"{int(x)} min" if pd.notna(x) else "N/A"
        )

        # Select and rename columns for display
        table_df = display_df[[
            "DATE_DISPLAY",
            "STATUS",
            "SLOT_CATEGORY",
            "CONTACT_MODE",
            "DURATION",
            "PRACTITIONER"
        ]]
        table_df.columns = ["Date & Time", "Status", "Slot Category", "Contact Mode", "Duration", "Practitioner"]

        # Display table
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
