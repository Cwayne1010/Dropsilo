with source as (
    select * from {{ source('raw_tier1', 'raw_customers') }}
),

staged as (
    select
        -- Identity
        customer_id,
        trim(customer_type)                                     as customer_type,
        trim(customer_status)                                   as customer_status,

        -- Dates
        try_to_date(customer_since_date::string, 'YYYY-MM-DD') as customer_since_date,

        -- Geography
        trim(city)                                              as city,
        trim(upper(state))                                      as state,
        trim(zip)                                               as zip,

        -- Relationship
        trim(relationship_officer_id)                           as relationship_officer_id,

        -- Optional fields — coerce empty string to NULL
        nullif(trim(naics_code), '')                            as naics_code,
        nullif(trim(kyc_status), '')                            as kyc_status,
        nullif(trim(aml_risk_rating), '')                       as aml_risk_rating,
        nullif(trim(is_related_party), '')                      as is_related_party,

        -- Metadata
        _ingested_at,
        _source_filename

    from source
)

select * from staged
