with customers as (
    select * from {{ ref('stg_customers') }}
),

loan_summary as (
    select
        customer_id,
        count(*)                                                        as loan_count,
        sum(case when not is_closed then net_exposure else 0 end)       as total_loan_exposure,
        sum(case when not is_closed then current_outstanding_balance
                 else 0 end)                                            as total_outstanding_balance,
        max(past_due_days)                                              as max_past_due_days,
        sum(case when not is_closed and is_classified then 1 else 0
            end)                                                        as classified_loan_count,
        sum(case when not is_closed and is_classified then net_exposure
                 else 0 end)                                            as classified_exposure,
        sum(case when not is_closed and is_non_accrual then 1 else 0
            end)                                                        as non_accrual_loan_count,
        max(is_classified::integer)::boolean                            as has_classified_loan,
        max(is_non_accrual::integer)::boolean                           as has_non_accrual_loan,
        max(origination_date)                                           as last_origination_date,
        listagg(distinct loan_type_code, ', ')
            within group (order by loan_type_code)                      as loan_types_held

    from {{ ref('int_loan_enriched') }}
    group by customer_id
),

-- Snowflake has no MODE() — use window function to find most frequent loan type
primary_loan_type as (
    select customer_id, loan_type_code as primary_loan_type
    from (
        select
            customer_id,
            loan_type_code,
            count(*)                                                    as type_count,
            row_number() over (
                partition by customer_id
                order by count(*) desc, loan_type_code asc
            )                                                           as rn
        from {{ ref('int_loan_enriched') }}
        where not is_closed
        group by customer_id, loan_type_code
    )
    where rn = 1
),

deposit_summary as (
    select
        customer_id,
        count(*)                                                        as deposit_account_count,
        sum(current_balance)                                            as total_deposits,
        sum(case when account_type_code = 'DDA' then current_balance
                 else 0 end)                                            as total_dda_balance,
        sum(case when account_type_code in ('SAV', 'MMA') then current_balance
                 else 0 end)                                            as total_savings_balance,
        sum(case when account_type_code in ('CD', 'IRA') then current_balance
                 else 0 end)                                            as total_cd_ira_balance,
        max(is_maturing_90_days::integer)::boolean                      as has_maturing_cd_90_days,
        count(case when is_active then 1 end)                           as active_account_count

    from {{ ref('int_deposit_enriched') }}
    group by customer_id
),

combined as (
    select
        c.customer_id,
        c.customer_type,
        c.customer_status,
        c.customer_since_date,
        c.city,
        c.state,
        c.zip,
        c.relationship_officer_id,
        c.kyc_status,
        c.aml_risk_rating,
        c.is_related_party,

        -- Loan aggregates
        coalesce(ls.loan_count, 0)                                      as loan_count,
        coalesce(ls.total_loan_exposure, 0)                             as total_loan_exposure,
        coalesce(ls.total_outstanding_balance, 0)                       as total_outstanding_balance,
        coalesce(ls.max_past_due_days, 0)                               as max_past_due_days,
        coalesce(ls.classified_loan_count, 0)                           as classified_loan_count,
        coalesce(ls.classified_exposure, 0)                             as classified_exposure,
        coalesce(ls.non_accrual_loan_count, 0)                          as non_accrual_loan_count,
        coalesce(ls.has_classified_loan, false)                         as has_classified_loan,
        coalesce(ls.has_non_accrual_loan, false)                        as has_non_accrual_loan,
        ls.last_origination_date,
        ls.loan_types_held,
        plt.primary_loan_type,

        -- Deposit aggregates
        coalesce(ds.deposit_account_count, 0)                           as deposit_account_count,
        coalesce(ds.total_deposits, 0)                                  as total_deposits,
        coalesce(ds.total_dda_balance, 0)                               as total_dda_balance,
        coalesce(ds.total_savings_balance, 0)                           as total_savings_balance,
        coalesce(ds.total_cd_ira_balance, 0)                            as total_cd_ira_balance,
        coalesce(ds.has_maturing_cd_90_days, false)                     as has_maturing_cd_90_days,

        -- Combined relationship metrics
        coalesce(ls.total_loan_exposure, 0)
            + coalesce(ds.total_deposits, 0)                            as total_relationship_value,

        -- Metadata
        c._ingested_at

    from customers c
    left join loan_summary ls
        on c.customer_id = ls.customer_id
    left join primary_loan_type plt
        on c.customer_id = plt.customer_id
    left join deposit_summary ds
        on c.customer_id = ds.customer_id
)

select * from combined
