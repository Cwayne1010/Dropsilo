with deposits as (
    select * from {{ ref('stg_deposits') }}
),

customers as (
    select
        customer_id,
        customer_type,
        customer_status,
        city,
        state,
        zip,
        relationship_officer_id
    from {{ ref('stg_customers') }}
),

enriched as (
    select
        -- Identity & Relationship
        d.account_id,
        d.customer_id,
        coalesce(d.officer_id, c.relationship_officer_id)      as officer_id,
        c.customer_type,
        c.customer_status                                       as customer_status,
        c.city                                                  as customer_city,
        c.state                                                 as customer_state,
        c.zip                                                   as customer_zip,

        -- Account Details
        d.account_type_code,
        d.account_status,
        d.open_date,
        d.maturity_date,

        -- Balances
        d.current_balance,
        d.average_daily_balance_30,
        d.average_daily_balance_90,
        d.overdraft_limit,
        case
            when d.current_balance < 10000           then '<$10k'
            when d.current_balance < 50000           then '$10k-$50k'
            when d.current_balance < 250000          then '$50k-$250k'
            else '$250k+'
        end                                                     as balance_tier,

        -- Rate
        d.interest_rate,

        -- Maturity Flags (CDs and IRAs only)
        iff(
            d.maturity_date is not null,
            datediff('day', current_date(), d.maturity_date),
            null
        )                                                       as days_to_maturity,
        (
            d.maturity_date is not null
            and datediff('day', current_date(), d.maturity_date) <= 90
            and d.account_type_code in ('CD', 'IRA')
        )                                                       as is_maturing_90_days,
        (
            d.maturity_date is not null
            and datediff('day', current_date(), d.maturity_date) <= 30
            and d.account_type_code in ('CD', 'IRA')
        )                                                       as is_maturing_30_days,

        -- Status Flags
        d.account_status = 'ACTIVE'                             as is_active,
        d.account_status in ('DORMANT', 'FROZEN')               as is_flagged,

        -- Metadata
        d._ingested_at,
        d._source_filename

    from deposits d
    left join customers c
        on d.customer_id = c.customer_id
)

select * from enriched
