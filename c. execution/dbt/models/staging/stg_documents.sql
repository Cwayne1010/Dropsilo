-- SCAFFOLD — disabled until the Snowflake Cortex document pipeline populates
-- RAW_UNSTRUCTURED.documents and the source block is added to models/sources.yml
--
-- Expected source: RAW_UNSTRUCTURED.documents
-- Expected columns: document_id, customer_id, loan_id, document_type, document_subtype,
--                   raw_text, extracted_json (VARIANT), source_date, ingested_at,
--                   source_filename, page_count, file_size_bytes, processing_status
--
-- Document types: LOAN_FILE, FINANCIAL_STATEMENT, APPRAISAL, REGULATORY, POLICY, SOP, OTHER
--
-- Pipeline to build (directive needed):
--   1. Documents land in S3/Azure Blob → Snowflake external stage
--   2. Snowflake Cortex PARSE_DOCUMENT + EXTRACT_ANSWER for structured field extraction
--   3. Extracted JSON stored in extracted_json VARIANT column
--   4. This staging model flattens key extracted fields for dbt joins
--
-- When activating:
--   1. Build Cortex document pipeline
--   2. Add source block to models/sources.yml
--   3. Change enabled=true below
--   4. Extend int_loan_enriched.sql to join document extracts to loans

{{ config(enabled=false, tags=['scaffold', 'unstructured']) }}

with source as (
    select * from {{ source('raw_unstructured', 'documents') }}
),

staged as (
    select
        document_id,
        customer_id,
        loan_id,
        trim(document_type)      as document_type,
        trim(document_subtype)   as document_subtype,
        trim(processing_status)  as processing_status,
        source_date,
        ingested_at,
        source_filename,
        page_count,
        file_size_bytes,

        -- Flattened extracted fields (populated from extracted_json VARIANT by Cortex)
        extracted_json:borrower_name::string            as extracted_borrower_name,
        extracted_json:appraised_value::float           as extracted_appraised_value,
        extracted_json:appraisal_date::string           as extracted_appraisal_date,
        extracted_json:net_income::float                as extracted_net_income,
        extracted_json:total_assets::float              as extracted_total_assets,
        extracted_json:total_liabilities::float         as extracted_total_liabilities,
        extracted_json:dscr::float                      as extracted_dscr,

        raw_text

    from source
    where processing_status = 'PROCESSED'
)

select * from staged
