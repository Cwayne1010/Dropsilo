-- Logic View: Loan Portfolio
-- Use cases: Officer portfolio drill-down, CRE concentration analysis, maturity ladder,
--            past-due monitoring, rate repricing exposure.
-- Scope: All active loans (excludes PAID). Includes charged-off for historical reference.
-- NLQ examples:
--   "Show me all past-due loans assigned to Officer 003"
--   "What is our CRE concentration as a percentage of total loans?"
--   "Which loans mature in the next 12 months?"

select
    -- Identity
    loan_id,
    customer_id,
    officer_id,
    customer_type,
    customer_city,
    customer_state,
    customer_zip,

    -- Classification
    loan_type_code,
    loan_purpose_code,
    collateral_type_code,

    -- Balances
    original_balance,
    current_outstanding_balance,
    committed_amount,
    collateral_value,
    net_exposure,
    participation_sold_amount,
    participation_purchased_amount,
    guaranteed_amount,
    ltv,

    -- Rate & Terms
    interest_rate,
    rate_type,
    rate_index,
    rate_spread,
    current_benchmark_rate,
    spread_to_benchmark,
    origination_date,
    maturity_date,
    next_payment_date,
    payment_amount,
    payment_frequency,
    days_to_maturity,
    maturity_bucket,

    -- Status & Credit Quality
    loan_status,
    past_due_days,
    past_due_amount,
    past_due_bucket,
    accrual_status,
    is_non_accrual,
    is_classified,
    risk_rating,
    regulatory_classification,
    guarantor_flag,

    -- Charge-Off (populated for CHARGEOFF status loans)
    charge_off_date,
    charge_off_amount,
    recovery_amount_ytd,

    -- Metadata
    _ingested_at,
    _source_filename

from {{ ref('int_loan_enriched') }}
where loan_status != 'PAID'
order by net_exposure desc nulls last
