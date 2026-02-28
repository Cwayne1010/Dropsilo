-- SCAFFOLD — disabled until fetch_census_geo.py populates RAW_EXTERNAL.census_zip_demographics
-- and the source block is added to models/sources.yml
--
-- Expected source: RAW_EXTERNAL.census_zip_demographics
-- Expected columns: zip, state, county_name, population, median_household_income,
--                   per_capita_income, housing_units, owner_occupied_rate, unemployment_rate
-- Fetch script to build: c. execution/fetch_census_geo.py
--   → Census Bureau ACS 5-year estimates (api.census.gov)
--   → CENSUS_API_KEY env var required (free at census.gov/developers)
--   → Pull for all ZIP codes in the bank's state(s) — start with TX for pilot
--
-- When activating:
--   1. Build fetch_census_geo.py
--   2. Add source block to models/sources.yml
--   3. Change enabled=true below
--   4. Update lv_customer_360.sql to activate the census join

{{ config(enabled=false, tags=['scaffold', 'external_source']) }}

with source as (
    select * from {{ source('raw_external', 'census_zip_demographics') }}
),

staged as (
    select
        trim(zip)                               as zip,
        upper(trim(state))                      as state,
        trim(county_name)                       as county_name,
        population::integer                     as population,
        median_household_income::integer        as median_household_income,
        per_capita_income::integer              as per_capita_income,
        housing_units::integer                  as housing_units,
        owner_occupied_rate::float              as owner_occupied_rate,
        unemployment_rate::float                as unemployment_rate,
        _ingested_at
    from source
)

select * from staged
