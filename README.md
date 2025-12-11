# OLIDS Patient Record Explorer

Streamlit application for exploring individual patient records from OLIDS data, providing an EHR-style view of patient observations and demographics.

## Features

- **Patient Search**: Universal search by `sk_patient_id` or `person_id`
- **Comprehensive Demographics**: View detailed patient information including:
  - Core demographics (age, gender, ethnicity, life stage)
  - Registration history (practice, PCN, ICB)
  - Geographic information (borough, deprivation indices)
  - Language and interpreter requirements
- **Registration History**: Track changes in practice registrations over time
- **Observations**: Browse patient observations with filtering by:
  - Date range (last 30/90/365 days, all time)
  - SNOMED code or description search
  - Displays values with units, sorted by most recent first

## Project Structure

```
olids-patient-explorer/
├── streamlit_app.py              # Main entry point
├── config.py                     # Database config & constants
├── database.py                   # Snowflake connection
├── environment.yml               # Conda dependencies
│
├── services/                     # Data access layer
│   ├── patient_service.py        # Patient search & demographics
│   └── record_service.py         # Observations queries
│
├── page_modules/                 # Page implementations
│   ├── search.py                 # Patient search page
│   └── patient_record.py         # EHR-style record view
│
└── utils/                        # Helper functions
    └── helpers.py                # Formatting utilities
```

## Database Schema

### Tables Used

- `MODELLING.DBT_STAGING.STG_OLIDS_OBSERVATION`: Patient observations (deduplicated and tested)
- `MODELLING.DBT_STAGING.STG_OLIDS_PERSON`: Person records (deduplicated and tested)
- `MODELLING.DBT_STAGING.STG_OLIDS_MEDICATION_ORDER`: Medication orders (deduplicated and tested)
- `REPORTING.OLIDS_PERSON_DEMOGRAPHICS.DIM_PERSON_DEMOGRAPHICS`: Current patient demographics
- `REPORTING.OLIDS_PERSON_DEMOGRAPHICS.DIM_PERSON_DEMOGRAPHICS_HISTORICAL`: Historical demographic changes (SCD-2)

The staging tables mirror the source data but have data quality tests and deduplication applied.

## Deployment

This application is designed to run on Snowflake's Streamlit platform.

### Requirements

- Python 3.11
- Snowflake Snowpark Python
- Streamlit

### Environment Setup

```bash
conda env create -f environment.yml
conda activate app_environment
```

### Running Locally

```bash
streamlit run streamlit_app.py
```

## Configuration

Database connection and configuration settings are managed in `config.py`. The application uses:

- **Role**: `ENGINEER`
- **Warehouse**: `WH_NCL_ENGINEERING_XS`
- **Schemas**:
  - `MODELLING.DBT_STAGING` for staging clinical data
  - `REPORTING.OLIDS_PERSON_DEMOGRAPHICS` for demographics

## Privacy Considerations

This application includes OLIDS data. Do not publish or share outputs without DAC approval.

## License

Internal use only - NCL ICB Analytics
