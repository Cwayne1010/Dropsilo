with loans as (
    select * from {{ ref('stg_loans') }}
),

customers as (
    select
        customer_id,
        customer_type,
        customer_status,
        customer_since_date,
        city,
        state,
        zip,
        relationship_officer_id
    from {{ ref('stg_customers') }}
),

-- FRED rate join: left join on rate_index to pull the most recent benchmark rate.
-- This CTE resolves to an empty result set when stg_fred_rates is disabled (scaffold).
-- Activate by enabling stg_fred_rates and its source block.
current_benchmark_rates as (
    {% if execute %}
        {% set fred_enabled = true %}
    {% else %}
        {% set fred_enabled = false %}
    {% endif %}

    select series_id, rate_value as benchmark_rate
    from (
        select
            series_id,
            rate_value,
            row_number() over (partition by series_id order by series_date desc) as rn
        -- When stg_fred_rates is activated, replace this placeholder with:
        -- from stg_fred_rates (ref disabled until fetch_fred_rates.py is built)
        from (select null::varchar as series_id, null::float as rate_value, null::date as series_date)
        where false
    )
    where rn = 1
),

enriched as (
    select
        -- Identity & Relationship
        l.loan_id,
        l.customer_id,
        l.officer_id,
        c.customer_type,
        c.customer_status                                               as customer_status,
        c.city                                                          as customer_city,
        c.state                                                         as customer_state,
        c.zip                                                           as customer_zip,

        -- Classification
        l.loan_type_code,
        l.loan_purpose_code,
        l.collateral_type_code,

        -- Balances
        l.original_balance,
        l.current_outstanding_balance,
        l.committed_amount,
        l.collateral_value,
        l.current_outstanding_balance
            - coalesce(l.participation_sold_amount, 0)                  as net_exposure,
        iff(
            l.collateral_value is not null and l.collateral_value > 0,
            l.current_outstanding_balance / l.collateral_value,
            null
        )                                                               as ltv,

        -- Rate & Terms
        l.interest_rate,
        l.rate_type,
        l.rate_index,
        l.rate_spread,
        cbr.benchmark_rate                                              as current_benchmark_rate,
        iff(
            cbr.benchmark_rate is not null,
            l.interest_rate - cbr.benchmark_rate,
            null
        )                                                               as spread_to_benchmark,
        l.origination_date,
        l.maturity_date,
        l.next_payment_date,
        l.payment_amount,
        l.payment_frequency,
        datediff('day', current_date(), l.maturity_date)                as days_to_maturity,
        case
            when datediff('day', current_date(), l.maturity_date) < 365     then '<1yr'
            when datediff('day', current_date(), l.maturity_date) < 1096    then '1-3yr'
            when datediff('day', current_date(), l.maturity_date) < 1826    then '3-5yr'
            else '5yr+'
        end                                                             as maturity_bucket,

        -- Status & Credit Quality
        l.loan_status,
        l.past_due_days,
        l.past_due_amount,
        l.accrual_status,
        l.risk_rating,
        l.regulatory_classification,
        case
            when l.past_due_days = 0                    then 'current'
            when l.past_due_days between 1 and 29       then '1-29'
            when l.past_due_days between 30 and 59      then '30-59'
            when l.past_due_days between 60 and 89      then '60-89'
            else '90+'
        end                                                             as past_due_bucket,
        l.regulatory_classification in (
            'SPECIAL_MENTION', 'SUBSTANDARD', 'DOUBTFUL', 'LOSS'
        )                                                               as is_classified,
        l.loan_status = 'NON_ACCRUAL'                                   as is_non_accrual,
        l.loan_status in ('PAID', 'CHARGEOFF')                          as is_closed,

        -- Participation & Guarantees
        l.participation_sold_amount,
        l.participation_purchased_amount,
        l.guaranteed_amount,
        l.guarantor_flag,

        -- Charge-Off & Recovery
        l.charge_off_date,
        l.charge_off_amount,
        l.recovery_amount_ytd,

        -- Metadata
        l._ingested_at,
        l._source_filename

    from loans l
    left join customers c
        on l.customer_id = c.customer_id
    left join current_benchmark_rates cbr
        on upper(l.rate_index) = cbr.series_id
)

select * from enriched
