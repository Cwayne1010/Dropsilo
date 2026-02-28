-- Test: Rate index must be populated for variable rate loans.
-- Fails if any row has rate_type = 'VARIABLE' AND rate_index IS NULL.
-- A non-zero result from this query means the test has failed.

select
    loan_id,
    rate_type,
    rate_index
from {{ ref('stg_loans') }}
where
    rate_type = 'VARIABLE'
    and rate_index is null
