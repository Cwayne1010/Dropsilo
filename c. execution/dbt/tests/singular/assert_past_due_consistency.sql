-- Test: Past-due days must be 0 when loan status is CURRENT.
-- Fails if any row has loan_status = 'CURRENT' AND past_due_days > 0.
-- A non-zero result from this query means the test has failed.

select
    loan_id,
    loan_status,
    past_due_days
from {{ ref('stg_loans') }}
where
    loan_status = 'CURRENT'
    and past_due_days > 0
