with source as (
    select * from {{ source('raw_tier1', 'raw_loans') }}
),

staged as (
    select
        -- Identity & Relationship
        loan_id,
        customer_id,
        trim(officer_id)                                            as officer_id,

        -- Classification
        trim(loan_type_code)                                        as loan_type_code,
        nullif(trim(loan_purpose_code), '')                         as loan_purpose_code,
        nullif(trim(collateral_type_code), '')                      as collateral_type_code,

        -- Balances
        original_balance::float                                     as original_balance,
        current_outstanding_balance::float                          as current_outstanding_balance,
        nullif(committed_amount, '')::float                         as committed_amount,
        nullif(collateral_value, '')::float                         as collateral_value,

        -- Rate & Terms
        interest_rate::float                                        as interest_rate,
        trim(rate_type)                                             as rate_type,
        nullif(trim(rate_index), '')                                as rate_index,
        nullif(rate_spread, '')::float                              as rate_spread,
        try_to_date(origination_date::string, 'YYYY-MM-DD')        as origination_date,
        try_to_date(maturity_date::string, 'YYYY-MM-DD')           as maturity_date,
        try_to_date(nullif(next_payment_date::string, ''), 'YYYY-MM-DD') as next_payment_date,
        nullif(payment_amount, '')::float                           as payment_amount,
        nullif(trim(payment_frequency), '')                         as payment_frequency,

        -- Status & Credit Quality
        trim(loan_status)                                           as loan_status,
        past_due_days::integer                                      as past_due_days,
        past_due_amount::float                                      as past_due_amount,
        trim(accrual_status)                                        as accrual_status,
        nullif(trim(risk_rating), '')                               as risk_rating,
        nullif(trim(regulatory_classification), '')                 as regulatory_classification,

        -- Participation & Guarantees
        nullif(participation_sold_amount, '')::float                as participation_sold_amount,
        nullif(participation_purchased_amount, '')::float           as participation_purchased_amount,
        nullif(guaranteed_amount, '')::float                        as guaranteed_amount,
        nullif(trim(guarantor_flag), '')                            as guarantor_flag,

        -- Charge-Off & Recovery
        try_to_date(nullif(charge_off_date::string, ''), 'YYYY-MM-DD') as charge_off_date,
        nullif(charge_off_amount, '')::float                        as charge_off_amount,
        nullif(recovery_amount_ytd, '')::float                      as recovery_amount_ytd,

        -- Metadata
        _ingested_at,
        _source_filename

    from source
)

select * from staged
