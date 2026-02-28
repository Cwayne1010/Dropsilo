-- Logic View: Credit Quality & Risk
-- Use cases: Classified asset review, exam preparation, non-accrual monitoring,
--            ALCO credit quality reporting, BSA/AML high-risk customer overlap.
-- Scope: Classified loans + all non-accrual + all past-due loans. Excludes PAID.
-- NLQ examples:
--   "Show all classified assets by regulatory classification"
--   "Which non-accrual loans have collateral below 80% LTV?"
--   "List loans that are both past due and flagged AML HIGH risk"

with problem_loans as (
    select * from {{ ref('int_loan_enriched') }}
    where
        is_classified
        or is_non_accrual
        or past_due_days > 0
        or loan_status = 'CHARGEOFF'
),

customers as (
    select
        customer_id,
        kyc_status,
        aml_risk_rating,
        is_related_party,
        naics_code
    from {{ ref('stg_customers') }}
),

-- FFIEC peer benchmark enrichment — activates when stg_ffiec_peers is enabled.
-- Placeholder returns nulls until the fetch script and source are built.
peer_benchmarks as (
    select
        null::varchar as peer_group,
        null::varchar as metric_name,
        null::float   as peer_median,
        null::float   as peer_p25,
        null::float   as peer_p75
    -- When stg_ffiec_peers is active, replace with a relevant metric subquery, e.g.:
    -- select peer_group, metric_name, metric_value as peer_median,
    --        metric_percentile_25 as peer_p25, metric_percentile_75 as peer_p75
    -- from stg_ffiec_peers (ref disabled until fetch_ffiec_peers.py is built)
    -- where metric_name = 'npa_ratio' and period_date = (select max(period_date) from ...)
)

select
    -- Identity
    pl.loan_id,
    pl.customer_id,
    pl.officer_id,
    pl.customer_type,
    pl.customer_city,
    pl.customer_state,

    -- Compliance Context
    c.kyc_status,
    c.aml_risk_rating,
    c.is_related_party,
    c.naics_code,

    -- Classification & Status
    pl.loan_status,
    pl.regulatory_classification,
    pl.accrual_status,
    pl.is_classified,
    pl.is_non_accrual,
    pl.risk_rating,

    -- Past Due Detail
    pl.past_due_days,
    pl.past_due_amount,
    pl.past_due_bucket,

    -- Balances & Collateral
    pl.loan_type_code,
    pl.collateral_type_code,
    pl.current_outstanding_balance,
    pl.net_exposure,
    pl.collateral_value,
    pl.ltv,
    pl.guaranteed_amount,
    pl.guarantor_flag,

    -- Maturity
    pl.maturity_date,
    pl.days_to_maturity,
    pl.maturity_bucket,

    -- Charge-Off
    pl.charge_off_date,
    pl.charge_off_amount,
    pl.recovery_amount_ytd,

    -- Peer Benchmarks (null until stg_ffiec_peers activated)
    pb.peer_group                                                       as ffiec_peer_group,
    pb.peer_median                                                      as ffiec_npa_ratio_peer_median,
    pb.peer_p25                                                         as ffiec_npa_ratio_peer_p25,
    pb.peer_p75                                                         as ffiec_npa_ratio_peer_p75,

    -- Metadata
    pl._ingested_at,
    pl._source_filename

from problem_loans pl
left join customers c
    on pl.customer_id = c.customer_id
cross join peer_benchmarks pb

order by
    case pl.regulatory_classification
        when 'LOSS'             then 1
        when 'DOUBTFUL'         then 2
        when 'SUBSTANDARD'      then 3
        when 'SPECIAL_MENTION'  then 4
        else 5
    end,
    pl.net_exposure desc nulls last
