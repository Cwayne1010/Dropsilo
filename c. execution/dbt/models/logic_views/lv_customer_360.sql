-- Logic View: Customer 360
-- Use cases: Full relationship view, top relationships by value, relationship manager dashboard,
--            customer health scoring inputs, maturity / repricing alerts.
-- Scope: All customers regardless of status.
-- NLQ examples:
--   "Who are our top 20 relationships by total value?"
--   "Show me the full relationship summary for customer CUST000042"
--   "Which active customers have both a classified loan and a maturing CD?"

with base as (
    select * from {{ ref('int_customer_summary') }}
),

-- Census demographic enrichment — activates when stg_census_geo is enabled.
-- The LEFT JOIN is null-safe: if the table doesn't exist yet, all census columns return null.
-- To activate: enable stg_census_geo + add source block + uncomment the join below.
census as (
    select
        null::varchar    as zip,
        null::varchar    as county_name,
        null::integer    as population,
        null::integer    as median_household_income,
        null::float      as owner_occupied_rate,
        null::float      as unemployment_rate
    where false
    -- When stg_census_geo is active, replace this CTE with:
    -- select zip, county_name, population, median_household_income,
    --        owner_occupied_rate, unemployment_rate
    -- from stg_census_geo (ref disabled until fetch_census.py is built)
)

select
    -- Customer Identity
    b.customer_id,
    b.customer_type,
    b.customer_status,
    b.customer_since_date,
    datediff('year', b.customer_since_date, current_date()) as tenure_years,
    b.city,
    b.state,
    b.zip,
    b.relationship_officer_id,

    -- Compliance Flags
    b.kyc_status,
    b.aml_risk_rating,
    b.is_related_party,

    -- Loan Relationship
    b.loan_count,
    b.total_loan_exposure,
    b.total_outstanding_balance,
    b.primary_loan_type,
    b.loan_types_held,
    b.last_origination_date,
    b.classified_loan_count,
    b.classified_exposure,
    b.non_accrual_loan_count,
    b.has_classified_loan,
    b.has_non_accrual_loan,
    b.max_past_due_days,

    -- Deposit Relationship
    b.deposit_account_count,
    b.total_deposits,
    b.total_dda_balance,
    b.total_savings_balance,
    b.total_cd_ira_balance,
    b.has_maturing_cd_90_days,

    -- Combined Relationship Value
    b.total_relationship_value,
    iff(
        b.total_relationship_value > 0,
        b.total_deposits / b.total_relationship_value,
        null
    )                                                                   as deposit_to_total_ratio,

    -- Census / Geographic Enrichment (null until stg_census_geo activated)
    cen.county_name,
    cen.population                                                      as zip_population,
    cen.median_household_income                                         as zip_median_income,
    cen.owner_occupied_rate                                             as zip_owner_occupied_rate,
    cen.unemployment_rate                                               as zip_unemployment_rate,

    -- Metadata
    b._ingested_at

from base b
left join census cen
    on b.zip = cen.zip

order by b.total_relationship_value desc nulls last
