with source as (
    select * from {{ source('raw_tier1', 'raw_deposits') }}
),

staged as (
    select
        -- Identity & Relationship
        account_id,
        customer_id,
        trim(account_type_code)                                       as account_type_code,
        trim(account_status)                                          as account_status,

        -- Dates
        try_to_date(open_date::string, 'YYYY-MM-DD')                 as open_date,
        try_to_date(nullif(maturity_date::string, ''), 'YYYY-MM-DD') as maturity_date,

        -- Balances
        current_balance::float                                        as current_balance,
        nullif(average_daily_balance_30, '')::float                   as average_daily_balance_30,
        nullif(average_daily_balance_90, '')::float                   as average_daily_balance_90,
        nullif(overdraft_limit, '')::float                            as overdraft_limit,

        -- Rate
        nullif(interest_rate, '')::float                              as interest_rate,

        -- Relationship
        nullif(trim(officer_id), '')                                  as officer_id,

        -- Metadata
        _ingested_at,
        _source_filename

    from source
)

select * from staged
