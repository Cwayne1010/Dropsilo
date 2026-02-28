-- Logic View: Officer Performance
-- Use cases: Portfolio ranking by officer, delinquency attribution, origination velocity,
--            deposit book management, management reporting, incentive tracking.
-- Scope: One row per officer_id. Aggregates both loan and deposit portfolios.
-- NLQ examples:
--   "Rank all officers by total loan portfolio balance"
--   "Which officer has the highest delinquency rate?"
--   "How many new loans did each officer originate in the last 12 months?"

with loan_metrics as (
    select
        officer_id,
        count(*)                                                        as total_loan_count,
        sum(net_exposure)                                               as total_loan_balance,
        sum(case when not is_closed then net_exposure else 0 end)       as active_loan_balance,

        -- Delinquency
        sum(case when past_due_days > 0 and not is_closed then 1 else 0
            end)                                                        as past_due_loan_count,
        sum(case when past_due_days > 0 and not is_closed
                 then net_exposure else 0 end)                          as past_due_balance,
        iff(
            count(case when not is_closed then 1 end) > 0,
            sum(case when past_due_days > 0 and not is_closed then 1 else 0 end)
                / count(case when not is_closed then 1 end)::float,
            0
        )                                                               as delinquency_rate,

        -- Credit Quality
        sum(case when is_classified and not is_closed then 1 else 0
            end)                                                        as classified_loan_count,
        sum(case when is_classified and not is_closed then net_exposure
                 else 0 end)                                            as classified_balance,
        sum(case when is_non_accrual then 1 else 0 end)                 as non_accrual_count,

        -- Average Risk Rating (numeric ratings only)
        avg(
            try_to_number(risk_rating)
        )                                                               as avg_risk_rating,

        -- Originations in last 12 months
        sum(
            case when origination_date >= dateadd('year', -1, current_date()) then 1 else 0 end
        )                                                               as originations_12m,
        sum(
            case when origination_date >= dateadd('year', -1, current_date())
                 then original_balance else 0 end
        )                                                               as origination_volume_12m,

        -- Loan Type Mix
        listagg(distinct loan_type_code, ', ')
            within group (order by loan_type_code)                      as loan_types_managed

    from {{ ref('int_loan_enriched') }}
    group by officer_id
),

deposit_metrics as (
    select
        officer_id,
        count(*)                                                        as total_deposit_accounts,
        sum(current_balance)                                            as total_deposit_balance,
        sum(case when account_type_code = 'DDA' then current_balance
                 else 0 end)                                            as dda_balance,
        sum(case when account_type_code in ('SAV', 'MMA') then current_balance
                 else 0 end)                                            as savings_mma_balance,
        sum(case when account_type_code in ('CD', 'IRA') then current_balance
                 else 0 end)                                            as cd_ira_balance,
        sum(case when is_maturing_90_days then current_balance
                 else 0 end)                                            as maturing_cd_90_days_balance

    from {{ ref('int_deposit_enriched') }}
    where officer_id is not null
    group by officer_id
)

select
    coalesce(lm.officer_id, dm.officer_id)                              as officer_id,

    -- Loan Portfolio
    coalesce(lm.total_loan_count, 0)                                    as total_loan_count,
    coalesce(lm.total_loan_balance, 0)                                  as total_loan_balance,
    coalesce(lm.active_loan_balance, 0)                                 as active_loan_balance,
    coalesce(lm.past_due_loan_count, 0)                                 as past_due_loan_count,
    coalesce(lm.past_due_balance, 0)                                    as past_due_balance,
    coalesce(lm.delinquency_rate, 0)                                    as delinquency_rate,
    coalesce(lm.classified_loan_count, 0)                               as classified_loan_count,
    coalesce(lm.classified_balance, 0)                                  as classified_balance,
    coalesce(lm.non_accrual_count, 0)                                   as non_accrual_count,
    lm.avg_risk_rating,
    coalesce(lm.originations_12m, 0)                                    as originations_12m,
    coalesce(lm.origination_volume_12m, 0)                              as origination_volume_12m,
    lm.loan_types_managed,

    -- Deposit Portfolio
    coalesce(dm.total_deposit_accounts, 0)                              as total_deposit_accounts,
    coalesce(dm.total_deposit_balance, 0)                               as total_deposit_balance,
    coalesce(dm.dda_balance, 0)                                         as dda_balance,
    coalesce(dm.savings_mma_balance, 0)                                 as savings_mma_balance,
    coalesce(dm.cd_ira_balance, 0)                                      as cd_ira_balance,
    coalesce(dm.maturing_cd_90_days_balance, 0)                         as maturing_cd_90_days_balance,

    -- Combined Book
    coalesce(lm.active_loan_balance, 0)
        + coalesce(dm.total_deposit_balance, 0)                         as total_book_value

from loan_metrics lm
full outer join deposit_metrics dm
    on lm.officer_id = dm.officer_id

order by total_loan_balance desc nulls last
