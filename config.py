"""
Configuration settings for OLIDS Patient Record Explorer
"""

# Database configuration
DB_STAGING = "MODELLING.DBT_STAGING"
DB_DEMOGRAPHICS = "REPORTING.OLIDS_PERSON_DEMOGRAPHICS"

# Table names
TABLE_OBSERVATION = f"{DB_STAGING}.STG_OLIDS_OBSERVATION"
TABLE_PERSON = f"{DB_STAGING}.STG_OLIDS_PERSON"
TABLE_MEDICATION_ORDER = f"{DB_STAGING}.STG_OLIDS_MEDICATION_ORDER"
TABLE_MEDICATION_STATEMENT = f"{DB_STAGING}.STG_OLIDS_MEDICATION_STATEMENT"
TABLE_PRACTITIONER = f"{DB_STAGING}.STG_OLIDS_PRACTITIONER"
TABLE_DIM_PERSON = f"{DB_DEMOGRAPHICS}.DIM_PERSON_DEMOGRAPHICS"
TABLE_DIM_PERSON_HISTORICAL = f"{DB_DEMOGRAPHICS}.DIM_PERSON_DEMOGRAPHICS_HISTORICAL"

# Snowflake configuration
ROLE = "ENGINEER"
WAREHOUSE = "WH_NCL_ENGINEERING_XS"

# Page configuration
PAGE_CONFIG = {
    "page_title": "OLIDS Patient Record Explorer",
    "page_icon": "📋",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

# Query limits
MAX_OBSERVATIONS = 1000

# Date range filter options
DATE_RANGE_OPTIONS = {
    "Last 30 days": 30,
    "Last 90 days": 90,
    "Last 365 days": 365,
    "All time": None
}

# Custom CSS for styling
CUSTOM_CSS = """
<style>
    /* Status badges */
    .status-active {
        background-color: #d4edda;
        color: #155724;
        padding: 6px 16px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-inactive {
        background-color: #f8d7da;
        color: #721c24;
        padding: 6px 16px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-deceased {
        background-color: #495057;
        color: #ffffff;
        padding: 6px 16px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Demographics grid */
    .demo-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 16px;
        margin-top: 16px;
    }

    .demo-item {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #dee2e6;
    }

    .demo-label {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .demo-value {
        font-size: 1rem;
        color: #212529;
    }

    /* Search box styling */
    .search-container {
        max-width: 600px;
        margin: 40px auto;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 16px;
        border-radius: 8px;
    }
</style>
"""
