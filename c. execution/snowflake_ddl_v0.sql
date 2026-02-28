-- ==========================================
-- Dropsilo Canonical Schema (v0) - Snowflake DDL
-- Description: Raw staging tables and ingestion objects for Dropsilo Tier 1
-- Last Updated: 2026-02-22
-- ==========================================

-- 1. Create Warehouse, Database, and Schema
CREATE WAREHOUSE IF NOT EXISTS DROPSILO_WH
    WITH WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    COMMENT = 'Dropsilo compute warehouse';

USE WAREHOUSE DROPSILO_WH;

CREATE DATABASE IF NOT EXISTS DROPSILO_DB;
USE DATABASE DROPSILO_DB;
CREATE SCHEMA IF NOT EXISTS RAW_TIER1;
USE SCHEMA RAW_TIER1;


-- ==========================================
-- 2. File Format & Stage Configuration
-- ==========================================

-- Define the Dropsilo v0 canonical file format (Pipe delimited CSV)
CREATE OR REPLACE FILE FORMAT dropsilo_csv_format
    TYPE = CSV
    FIELD_DELIMITER = '|'
    SKIP_HEADER = 1
    NULL_IF = ('', 'NULL', 'N/A')
    EMPTY_FIELD_AS_NULL = TRUE
    COMPRESSION = AUTO
    ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE
    REPLACE_INVALID_CHARACTERS = TRUE
    ENCODING = 'UTF8'
    DATE_FORMAT = 'YYYY-MM-DD';

-- Create an internal stage for the Dropsilo application to push files into
-- (In production, this would likely be an external stage tied to an S3/Azure bucket)
CREATE OR REPLACE STAGE dropsilo_incoming_data_stage
    FILE_FORMAT = dropsilo_csv_format
    COMMENT = 'Internal stage for Dropsilo nightly batch feeds via SFTP integration';


-- ==========================================
-- 3. Raw Staging Tables
-- ==========================================

-- Table: CUSTOMERS
CREATE OR REPLACE TABLE raw_customers (
    customer_id VARCHAR(255) NOT NULL PRIMARY KEY COMMENT 'Core system unique customer/relationship ID',
    customer_type VARCHAR(50) NOT NULL COMMENT 'IND, BUS, TRUST, GOV',
    customer_since_date DATE NOT NULL COMMENT 'Date customer relationship opened',
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL COMMENT '2-letter state code',
    zip VARCHAR(10) NOT NULL COMMENT '5-digit ZIP code',
    relationship_officer_id VARCHAR(255) NOT NULL COMMENT 'Assigned officer ID',
    naics_code VARCHAR(10) COMMENT '6-digit NAICS code for businesses',
    kyc_status VARCHAR(50) COMMENT 'VERIFIED, PENDING, REVIEW, FAILED',
    aml_risk_rating VARCHAR(50) COMMENT 'LOW, MEDIUM, HIGH',
    customer_status VARCHAR(50) NOT NULL COMMENT 'ACTIVE, INACTIVE, DECEASED, CLOSED',
    is_related_party VARCHAR(1) COMMENT 'Y or N',
    
    -- Metadata columns for lineage and observability
    _ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_filename VARCHAR(255)
);

-- Table: LOANS
CREATE OR REPLACE TABLE raw_loans (
    loan_id VARCHAR(255) NOT NULL PRIMARY KEY COMMENT 'Core system unique loan account number',
    customer_id VARCHAR(255) NOT NULL FOREIGN KEY REFERENCES raw_customers(customer_id) COMMENT 'Foreign key to raw_customers',
    officer_id VARCHAR(255) NOT NULL COMMENT 'Originating/managing officer ID',
    loan_type_code VARCHAR(50) NOT NULL COMMENT 'CRE, CI, CON, MTG, LOC, AG, etc.',
    loan_purpose_code VARCHAR(100),
    collateral_type_code VARCHAR(50) COMMENT 'RE, EQ, AR, VEH, UNS, CD',
    original_balance NUMBER(38, 2) NOT NULL COMMENT 'Balance at origination',
    current_outstanding_balance NUMBER(38, 2) NOT NULL COMMENT 'Outstanding principal as of export date',
    committed_amount NUMBER(38, 2) COMMENT 'Total credit limit for LOCs',
    collateral_value NUMBER(38, 2) COMMENT 'Appraised collateral value',
    interest_rate NUMBER(10, 4) NOT NULL COMMENT 'Current note rate as decimal percent',
    rate_type VARCHAR(50) NOT NULL COMMENT 'FIXED or VARIABLE',
    rate_index VARCHAR(100) COMMENT 'PRIME, SOFR, LIBOR, etc.',
    rate_spread NUMBER(10, 4) COMMENT 'Spread over index in percent',
    origination_date DATE NOT NULL COMMENT 'Date loan was funded',
    maturity_date DATE NOT NULL COMMENT 'Contractual maturity date',
    next_payment_date DATE COMMENT 'Date of next scheduled payment',
    payment_amount NUMBER(38, 2) COMMENT 'Scheduled payment amount',
    payment_frequency VARCHAR(50) COMMENT 'MONTHLY, QUARTERLY, etc.',
    loan_status VARCHAR(50) NOT NULL COMMENT 'CURRENT, PAST_DUE, NON_ACCRUAL, CHARGEOFF, PAID, DEMAND',
    past_due_days NUMBER(38, 0) NOT NULL COMMENT 'Days past due. 0 if current',
    past_due_amount NUMBER(38, 2) NOT NULL COMMENT 'Dollar amount past due. 0.00 if current',
    accrual_status VARCHAR(50) NOT NULL COMMENT 'ACCRUAL or NON_ACCRUAL',
    risk_rating VARCHAR(50) COMMENT 'Bank internal risk rating',
    regulatory_classification VARCHAR(50) COMMENT 'PASS, SPECIAL_MENTION, SUBSTANDARD, DOUBTFUL, LOSS',
    participation_sold_amount NUMBER(38, 2) COMMENT 'Amount participated out',
    participation_purchased_amount NUMBER(38, 2) COMMENT 'Amount purchased',
    guaranteed_amount NUMBER(38, 2) COMMENT 'SBA/USDA/other guaranteed portion',
    guarantor_flag VARCHAR(1) COMMENT 'Y or N',
    charge_off_date DATE COMMENT 'Date of charge-off',
    charge_off_amount NUMBER(38, 2) COMMENT 'Amount charged off',
    recovery_amount_ytd NUMBER(38, 2) COMMENT 'Recoveries year-to-date',
    
    -- Metadata limits
    _ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_filename VARCHAR(255)
);

-- Table: DEPOSITS
CREATE OR REPLACE TABLE raw_deposits (
    account_id VARCHAR(255) NOT NULL PRIMARY KEY COMMENT 'Core system unique deposit account number',
    customer_id VARCHAR(255) NOT NULL FOREIGN KEY REFERENCES raw_customers(customer_id) COMMENT 'Foreign key to raw_customers',
    account_type_code VARCHAR(50) NOT NULL COMMENT 'DDA, SAV, MMA, CD, IRA, LOC',
    open_date DATE NOT NULL COMMENT 'Date account was opened',
    current_balance NUMBER(38, 2) NOT NULL COMMENT 'Balance as of export date',
    average_daily_balance_30 NUMBER(38, 2) COMMENT '30-day average daily balance',
    average_daily_balance_90 NUMBER(38, 2) COMMENT '90-day average daily balance',
    interest_rate NUMBER(10, 4) COMMENT 'Current APY/interest rate',
    maturity_date DATE COMMENT 'Maturity date for CDs and IRAs',
    officer_id VARCHAR(255) COMMENT 'Assigned officer/RM',
    account_status VARCHAR(50) NOT NULL COMMENT 'ACTIVE, DORMANT, CLOSED, FROZEN',
    overdraft_limit NUMBER(38, 2) COMMENT 'Approved overdraft limit',
    
    -- Metadata
    _ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_filename VARCHAR(255)
);


-- ==========================================
-- 4. Example Bulk COPY Commands
-- ==========================================
-- These commands can be used to manually load the generated mock CSVs
-- from the Dropsilo temporary data factory into the raw Snowflake tables.

/*
-- Upload local mock data to Snowflake internal stage (requires local SnowSQL client)
PUT file://.tmp/mock_data/dropsilo_customers_*.csv @dropsilo_incoming_data_stage AUTO_COMPRESS=TRUE;
PUT file://.tmp/mock_data/dropsilo_loans_*.csv @dropsilo_incoming_data_stage AUTO_COMPRESS=TRUE;
PUT file://.tmp/mock_data/dropsilo_deposits_*.csv @dropsilo_incoming_data_stage AUTO_COMPRESS=TRUE;

-- Load data into RAW tables mapping metadata fields from the stage
COPY INTO raw_customers 
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 
        CURRENT_TIMESTAMP(), METADATA$FILENAME
    FROM @dropsilo_incoming_data_stage
)
PATTERN='.*dropsilo_customers_.*\\.csv.*'
ON_ERROR='ABORT_STATEMENT';

COPY INTO raw_loans 
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, 
        $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $30, $31, $32,
        CURRENT_TIMESTAMP(), METADATA$FILENAME
    FROM @dropsilo_incoming_data_stage
)
PATTERN='.*dropsilo_loans_.*\\.csv.*'
ON_ERROR='ABORT_STATEMENT';

COPY INTO raw_deposits 
FROM (
    SELECT 
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
        CURRENT_TIMESTAMP(), METADATA$FILENAME
    FROM @dropsilo_incoming_data_stage
)
PATTERN='.*dropsilo_deposits_.*\\.csv.*'
ON_ERROR='ABORT_STATEMENT';
*/


-- ==========================================
-- 5. External Reference Data Schema (RAW_EXTERNAL)
-- Populated by fetch scripts in c. execution/
-- Activated in dbt when each table is populated
-- ==========================================

CREATE SCHEMA IF NOT EXISTS RAW_EXTERNAL;
USE SCHEMA RAW_EXTERNAL;

-- FRED interest rate series (Prime, SOFR, Fed Funds, yield curve points)
CREATE TABLE IF NOT EXISTS fred_rates (
    series_date     DATE          NOT NULL COMMENT 'Observation date',
    series_id       VARCHAR(50)   NOT NULL COMMENT 'FRED series ID (e.g. PRIME, SOFR, DFF, DGS10)',
    series_label    VARCHAR(100)  COMMENT  'Human-readable label (e.g. Bank Prime Loan Rate)',
    rate_value      NUMBER(10, 4) NOT NULL COMMENT 'Rate value in percent',
    _ingested_at    TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (series_date, series_id)
);

-- FFIEC Call Report peer benchmarks (aggregated ratios by peer group)
CREATE TABLE IF NOT EXISTS ffiec_call_reports (
    period_date          DATE          NOT NULL COMMENT 'Reporting period end date',
    peer_group           VARCHAR(50)   NOT NULL COMMENT 'Asset size peer group (e.g. $100M-$300M)',
    metric_name          VARCHAR(100)  NOT NULL COMMENT 'Ratio name (e.g. npa_ratio, nim, roa)',
    metric_value         NUMBER(10, 4) COMMENT    'Peer group median or mean value',
    metric_percentile_25 NUMBER(10, 4) COMMENT    '25th percentile for distribution context',
    metric_percentile_75 NUMBER(10, 4) COMMENT    '75th percentile for distribution context',
    _ingested_at         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (period_date, peer_group, metric_name)
);

-- FDIC institution directory (enables market and peer lookups)
CREATE TABLE IF NOT EXISTS fdic_institutions (
    cert_number          VARCHAR(20)   NOT NULL PRIMARY KEY COMMENT 'FDIC certificate number',
    institution_name     VARCHAR(255)  NOT NULL,
    city                 VARCHAR(100),
    state                VARCHAR(2),
    zip                  VARCHAR(10),
    asset_size           NUMBER(38, 0) COMMENT 'Total assets in thousands',
    asset_size_bucket    VARCHAR(50)   COMMENT 'e.g. <$100M, $100M-$300M, $300M-$1B, $1B+',
    institution_class    VARCHAR(10)   COMMENT 'FDIC institution class code',
    active               VARCHAR(1)    COMMENT 'Y if currently active',
    _ingested_at         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Census ZIP-level demographics (enriches customer geography)
CREATE TABLE IF NOT EXISTS census_zip_demographics (
    zip                      VARCHAR(10)   NOT NULL PRIMARY KEY,
    state                    VARCHAR(2),
    county_name              VARCHAR(100),
    population               NUMBER(38, 0),
    median_household_income  NUMBER(38, 0) COMMENT 'Median household income in dollars',
    per_capita_income        NUMBER(38, 0),
    housing_units            NUMBER(38, 0),
    owner_occupied_rate      NUMBER(10, 4) COMMENT 'Percent of owner-occupied housing units',
    unemployment_rate        NUMBER(10, 4),
    _ingested_at             TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- HMDA public loan data (fair lending analytics)
CREATE TABLE IF NOT EXISTS hmda_loans (
    activity_year        NUMBER(4, 0)  NOT NULL,
    lei                  VARCHAR(50)   COMMENT 'Legal Entity Identifier of reporting institution',
    loan_type            NUMBER(2, 0)  COMMENT '1=Conventional, 2=FHA, 3=VA, 4=USDA',
    loan_purpose         NUMBER(2, 0)  COMMENT '1=Purchase, 2=Improvement, 31=Refi, 32=Cash-out',
    property_type        NUMBER(2, 0)  COMMENT '1=Site-built, 2=Manufactured',
    occupancy_type       NUMBER(2, 0)  COMMENT '1=Principal, 2=2nd home, 3=Investment',
    action_taken         NUMBER(2, 0)  NOT NULL COMMENT '1=Originated, 2=App approved not accepted, 3=Denied, etc.',
    state                VARCHAR(2),
    county               VARCHAR(5)    COMMENT 'FIPS county code',
    census_tract         VARCHAR(11),
    loan_amount          NUMBER(38, 0) COMMENT 'Loan amount in dollars',
    _ingested_at         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- SBA 7(a) and 504 loan data (enriches guaranteed loan fields)
CREATE TABLE IF NOT EXISTS sba_loans (
    program              VARCHAR(10)   NOT NULL COMMENT '7a or 504',
    approval_fiscal_year NUMBER(4, 0),
    approval_date        DATE,
    gross_approval       NUMBER(38, 2) COMMENT 'Approved loan amount',
    initial_interest_rate NUMBER(10, 4),
    loan_status          VARCHAR(50)   COMMENT 'PIF, CHGOFF, CANCLD, EXEMPT, DISBURSED',
    naics_code           VARCHAR(10),
    state                VARCHAR(2),
    business_type        VARCHAR(100),
    _ingested_at         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);


-- ==========================================
-- 6. Unstructured Document Ingestion Schema (RAW_UNSTRUCTURED)
-- Populated via Snowflake Cortex document processing pipeline
-- Supports: loan files, financial statements, appraisals, regulatory docs, policies/SOPs
-- ==========================================

CREATE SCHEMA IF NOT EXISTS RAW_UNSTRUCTURED;
USE SCHEMA RAW_UNSTRUCTURED;

CREATE TABLE IF NOT EXISTS documents (
    document_id      VARCHAR(255)  NOT NULL PRIMARY KEY COMMENT 'Unique document identifier',
    customer_id      VARCHAR(255)  COMMENT 'FK to RAW_TIER1.raw_customers — null for institution-level docs',
    loan_id          VARCHAR(255)  COMMENT 'FK to RAW_TIER1.raw_loans — null if not loan-specific',
    document_type    VARCHAR(100)  NOT NULL COMMENT 'LOAN_FILE, FINANCIAL_STATEMENT, APPRAISAL, REGULATORY, POLICY, SOP, OTHER',
    document_subtype VARCHAR(100)  COMMENT 'e.g. CREDIT_MEMO, TAX_RETURN, PHASE1_ENV, EXAM_REPORT',
    raw_text         TEXT          COMMENT 'Full extracted text from document (OCR or native)',
    extracted_json   VARIANT       COMMENT 'Structured fields extracted by Cortex/LLM (key-value pairs)',
    source_date      DATE          COMMENT 'Document date (not ingestion date)',
    ingested_at      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source_filename  VARCHAR(500)  COMMENT 'Original filename or S3/Azure path',
    page_count       NUMBER(5, 0),
    file_size_bytes  NUMBER(38, 0),
    processing_status VARCHAR(50)  DEFAULT 'PENDING' COMMENT 'PENDING, PROCESSED, FAILED, REVIEW'
);
