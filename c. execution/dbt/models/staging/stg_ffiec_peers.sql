-- SCAFFOLD — disabled until fetch_ffiec_peers.py populates RAW_EXTERNAL.ffiec_call_reports
-- and the source block is added to models/sources.yml
--
-- Expected source: RAW_EXTERNAL.ffiec_call_reports
-- Expected columns: period_date, peer_group, metric_name, metric_value,
--                   metric_percentile_25, metric_percentile_75
-- Fetch script to build: c. execution/fetch_ffiec_peers.py
--   → FFIEC CDR bulk data download (https://cdr.ffiec.gov/public/pws/downloadbulkdata.aspx)
--   → Key metrics: npa_ratio, nim, roa, roe, tier1_ratio, cre_concentration_ratio
--   → Peer groups by asset size: <$100M, $100M-$300M, $300M-$1B, $1B+
--
-- When activating:
--   1. Build fetch_ffiec_peers.py
--   2. Add source block to models/sources.yml
--   3. Change enabled=true below
--   4. Update lv_credit_quality.sql to activate peer comparison columns

{{ config(enabled=false, tags=['scaffold', 'external_source']) }}

with source as (
    select * from {{ source('raw_external', 'ffiec_call_reports') }}
),

staged as (
    select
        try_to_date(period_date::string, 'YYYY-MM-DD') as period_date,
        trim(peer_group)                                as peer_group,
        trim(metric_name)                               as metric_name,
        metric_value::float                             as metric_value,
        metric_percentile_25::float                     as metric_percentile_25,
        metric_percentile_75::float                     as metric_percentile_75,
        _ingested_at
    from source
)

select * from staged
