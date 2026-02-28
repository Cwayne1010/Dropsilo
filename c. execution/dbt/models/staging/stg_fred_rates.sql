-- SCAFFOLD — disabled until fetch_fred_rates.py populates RAW_EXTERNAL.fred_rates
-- and the source block is added to models/sources.yml
--
-- Expected source: RAW_EXTERNAL.fred_rates
-- Expected columns: series_date, series_id, series_label, rate_value
-- Fetch script to build: c. execution/fetch_fred_rates.py
--   → Uses FRED API (api.stlouisfed.org) with FRED_API_KEY env var
--   → Series to pull: PRIME, SOFR, DFF (Fed Funds), DGS10 (10yr Treasury), DGS2 (2yr Treasury)
--
-- When activating:
--   1. Build and run fetch_fred_rates.py to populate RAW_EXTERNAL.fred_rates
--   2. Add source block to models/sources.yml under raw_external
--   3. Change enabled=true below
--   4. Update int_loan_enriched.sql to activate the FRED join (search for "stg_fred_rates")

{{ config(enabled=false, tags=['scaffold', 'external_source']) }}

with source as (
    select * from {{ source('raw_external', 'fred_rates') }}
),

staged as (
    select
        series_date,
        upper(trim(series_id))   as series_id,
        trim(series_label)       as series_label,
        rate_value::float        as rate_value,
        _ingested_at
    from source
)

select * from staged
