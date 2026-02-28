# Dropsilo Data Spec — v0

> **Version**: 0.1
> **Status**: Draft — Pilot validation against Fiserv Premier (BA export)
> **Last updated**: 2026-02-20
> **Strategy reference**: `a. strategy/Dropsilo/3_product/001_dropsilo_technical_framework.md`

## Purpose

This document defines the Dropsilo canonical flat file schema — the standard format any core banking system must produce to onboard onto the Dropsilo platform. It is handed to bank IT teams at onboarding. Dropsilo ingests one format regardless of whether the source core is Jack Henry, Fiserv, FIS, or any other system.

The schema is designed backwards from the dbt Logic Views and NLQ use cases — it contains exactly what the analytics and AI layers need, no more.

---

## Format Requirements

| Property | Specification |
|----------|--------------|
| **File format** | UTF-8 CSV |
| **Delimiter** | Pipe (`\|`) — avoids comma conflicts in text fields |
| **Header row** | Required, row 1, field names exactly as specified |
| **Date format** | `YYYY-MM-DD` (e.g. `2025-11-30`) |
| **Amount format** | Decimal numeric, no currency symbol, no commas (e.g. `1234567.89`) |
| **Rate format** | Decimal percent, not basis points (e.g. `6.25` = 6.25%) |
| **Boolean** | `Y` or `N` |
| **Null / missing** | Empty string — never the literal string `NULL` or `N/A` |
| **Snapshot type** | Full daily snapshot (not incremental delta) |
| **File structure** | Three separate files — one per object (customers, loans, deposits). Combined files are not accepted. |
| **Frequency** | Minimum: nightly after end-of-day processing |
| **Delivery** | SFTP to Dropsilo-provided endpoint |
| **Filename convention** | `dropsilo_{object}_{YYYYMMDD}.csv` |

**Filename examples:**
```
dropsilo_customers_20260220.csv
dropsilo_loans_20260220.csv
dropsilo_deposits_20260220.csv
```

---

## File 1: Customers (`dropsilo_customers_YYYYMMDD.csv`)

One row per customer relationship. Includes both individual and business customers.

| # | Field Name | Type | Required | Description |
|---|-----------|------|----------|-------------|
| 1 | `customer_id` | string | YES | Core system's unique customer/relationship ID. Immutable. |
| 2 | `customer_type` | string | YES | `IND` (individual), `BUS` (business), `TRUST`, `GOV` |
| 3 | `customer_since_date` | date | YES | Date customer relationship opened |
| 4 | `city` | string | YES | Customer's primary city |
| 5 | `state` | string | YES | 2-letter state code (e.g. `TX`) |
| 6 | `zip` | string | YES | 5-digit ZIP code |
| 7 | `relationship_officer_id` | string | YES | Officer/RM ID from core — joins to officer table or loan records |
| 8 | `naics_code` | string | NO | 6-digit NAICS code (business customers only) |
| 9 | `kyc_status` | string | NO | `VERIFIED`, `PENDING`, `REVIEW`, `FAILED` |
| 10 | `aml_risk_rating` | string | NO | `LOW`, `MEDIUM`, `HIGH` — from core's BSA/AML module |
| 11 | `customer_status` | string | YES | `ACTIVE`, `INACTIVE`, `DECEASED`, `CLOSED` |
| 12 | `is_related_party` | boolean | NO | `Y` if insider/related party per bank's designation |

**PII note:** Do not include customer name, SSN/EIN, street address, or date of birth. `customer_id` is the key — Dropsilo does not need PII to run analytics. Name/identity data stays in the core.

---

## File 2: Loans (`dropsilo_loans_YYYYMMDD.csv`)

One row per loan account. Covers commercial, consumer, mortgage, and lines of credit.

### Identity & Relationship
| # | Field Name | Type | Required | Description |
|---|-----------|------|----------|-------------|
| 1 | `loan_id` | string | YES | Core system's unique loan account number |
| 2 | `customer_id` | string | YES | Foreign key — joins to customers file |
| 3 | `officer_id` | string | YES | Originating/managing officer ID |

### Classification
| # | Field Name | Type | Required | Description |
|---|-----------|------|----------|-------------|
| 4 | `loan_type_code` | string | YES | Core's loan type code. See mapping guide. Common: `CRE` (commercial real estate), `CI` (commercial & industrial), `CON` (consumer), `MTG` (mortgage), `LOC` (line of credit), `AG` (agricultural) |
| 5 | `loan_purpose_code` | string | NO | Core's purpose code if available |
| 6 | `collateral_type_code` | string | NO | `RE` (real estate), `EQ` (equipment), `AR` (accounts receivable), `VEH` (vehicle), `UNS` (unsecured), `CD` (certificate of deposit) |

### Balances & Limits
| # | Field Name | Type | Required | Description |
|---|-----------|------|----------|-------------|
| 7 | `original_balance` | decimal | YES | Balance at origination |
| 8 | `current_outstanding_balance` | decimal | YES | Outstanding principal as of export date |
| 9 | `committed_amount` | decimal | NO | Total credit limit (lines of credit) — use `current_outstanding_balance` for revolving balance |
| 10 | `collateral_value` | decimal | NO | Appraised / most recent collateral value |

### Rate & Terms
| # | Field Name | Type | Required | Description |
|---|-----------|------|----------|-------------|
| 11 | `interest_rate` | decimal | YES | Current note rate as decimal percent (e.g. `6.75`) |
| 12 | `rate_type` | string | YES | `FIXED` or `VARIABLE` |
| 13 | `rate_index` | string | NO | `PRIME`, `SOFR`, `LIBOR`, `FIXED`, other index name — required if `rate_type` = `VARIABLE` |
| 14 | `rate_spread` | decimal | NO | Spread over index in percent (e.g. `2.00` = Prime + 2.00%) |
| 15 | `origination_date` | date | YES | Date loan was funded |
| 16 | `maturity_date` | date | YES | Contractual maturity date |
| 17 | `next_payment_date` | date | NO | Date of next scheduled payment |
| 18 | `payment_amount` | decimal | NO | Scheduled payment amount |
| 19 | `payment_frequency` | string | NO | `MONTHLY`, `QUARTERLY`, `SEMIANNUAL`, `ANNUAL`, `INTEREST_ONLY`, `DEMAND` |

### Status & Credit Quality
| # | Field Name | Type | Required | Description |
|---|-----------|------|----------|-------------|
| 20 | `loan_status` | string | YES | `CURRENT`, `PAST_DUE`, `NON_ACCRUAL`, `CHARGEOFF`, `PAID`, `DEMAND` |
| 21 | `past_due_days` | integer | YES | Days past due as of export date. `0` if current. |
| 22 | `past_due_amount` | decimal | YES | Dollar amount past due. `0.00` if current. |
| 23 | `accrual_status` | string | YES | `ACCRUAL` or `NON_ACCRUAL` |
| 24 | `risk_rating` | string | NO | Bank's internal risk rating (e.g. `1`–`10` or `PASS`, `WATCH`, `SUBSTANDARD`, `DOUBTFUL`) |
| 25 | `regulatory_classification` | string | NO | `PASS`, `SPECIAL_MENTION`, `SUBSTANDARD`, `DOUBTFUL`, `LOSS` |

### Participation & Guarantees
| # | Field Name | Type | Required | Description |
|---|-----------|------|----------|-------------|
| 26 | `participation_sold_amount` | decimal | NO | Amount participated out to other institutions |
| 27 | `participation_purchased_amount` | decimal | NO | Amount purchased from lead bank |
| 28 | `guaranteed_amount` | decimal | NO | SBA/USDA/other guaranteed portion |
| 29 | `guarantor_flag` | boolean | NO | `Y` if personal or corporate guarantee exists |

### Charge-Off & Recovery
| # | Field Name | Type | Required | Description |
|---|-----------|------|----------|-------------|
| 30 | `charge_off_date` | date | NO | Date of charge-off (if applicable) |
| 31 | `charge_off_amount` | decimal | NO | Amount charged off |
| 32 | `recovery_amount_ytd` | decimal | NO | Recoveries year-to-date |

---

## File 3: Deposits (`dropsilo_deposits_YYYYMMDD.csv`)

One row per deposit account.

| # | Field Name | Type | Required | Description |
|---|-----------|------|----------|-------------|
| 1 | `account_id` | string | YES | Core system's unique deposit account number |
| 2 | `customer_id` | string | YES | Foreign key — joins to customers file |
| 3 | `account_type_code` | string | YES | `DDA` (checking), `SAV` (savings), `MMA` (money market), `CD` (certificate of deposit), `IRA`, `LOC` (deposit line of credit) |
| 4 | `open_date` | date | YES | Date account was opened |
| 5 | `current_balance` | decimal | YES | Balance as of export date |
| 6 | `average_daily_balance_30` | decimal | NO | 30-day average daily balance |
| 7 | `average_daily_balance_90` | decimal | NO | 90-day average daily balance |
| 8 | `interest_rate` | decimal | NO | Current APY/interest rate |
| 9 | `maturity_date` | date | NO | Maturity date (CDs and IRAs only) |
| 10 | `officer_id` | string | NO | Assigned officer/RM |
| 11 | `account_status` | string | YES | `ACTIVE`, `DORMANT`, `CLOSED`, `FROZEN` |
| 12 | `overdraft_limit` | decimal | NO | Approved overdraft/ODP limit |

---

## Derived Fields (Do Not Include)

The following are **calculated by Dropsilo's dbt layer** — do not include in the export. Including pre-calculated versions will cause conflicts with governed metric definitions:

- Total exposure per customer (sum of loans minus participations sold)
- Customer health score
- Loan-to-value ratio
- Debt service coverage ratio
- Portfolio concentration percentages
- Past due aging buckets (30/60/90+)

---

## Validation Rules

Dropsilo's ingestion pipeline will validate every file on receipt. Files that fail validation are **rejected in full** — a corrected file must be re-submitted. Partial ingestion is not supported.

| Rule | Behavior on Failure |
|------|-------------------|
| Required field is empty | File rejected — log lists every row/field in violation |
| `customer_id` in loans or deposits does not exist in customers file | File rejected — foreign key violation |
| `loan_id` or `account_id` contains duplicates within a single file | File rejected |
| Date fields not in `YYYY-MM-DD` format | File rejected |
| Amount fields contain non-numeric characters | File rejected |
| `past_due_days` > 0 but `loan_status` = `CURRENT` | Warning logged, file accepted — flagged for review |
| File received without matching date-stamp in filename | Warning logged, file accepted — uses receipt date |

---

## Core System Mapping Guides

Each core system uses different field names and code values. Dropsilo maintains a mapping guide per core that translates the core's native fields to this spec. Current mapping guides:

| Core System | Status | Notes |
|-------------|--------|-------|
| **Fiserv Premier (BA export)** | In progress — pilot bank | First mapping guide; BA = Business Analytics module export |
| Jack Henry SilverLake | Planned — Tier 2 (jXchange) | Also needed for flat file fallback |
| Jack Henry CIF 20/20 | Not started | |
| FIS IBS / Horizon | Not started | |

### Fiserv Premier — Known Considerations

- Fiserv Premier's Business Analytics (BA) module can export account-level data to CSV — confirm delimiter and encoding with bank IT
- Premier uses numeric account type codes — requires translation table to Dropsilo's string codes (`DDA`, `SAV`, etc.)
- Risk rating field availability varies by Premier version and bank configuration — flag as optional for pilot
- `average_daily_balance` fields: confirm whether Premier BA exports 30/90-day averages natively or whether a calculation period needs to be configured
- Premier loan type codes are bank-configured, not standardized — pilot bank must provide their code-to-type mapping

---

## Delivery Setup Checklist (Bank IT)

- [ ] Confirm export tool (BA module, report writer, or custom query) can produce pipe-delimited CSV
- [ ] Confirm UTF-8 encoding (not EBCDIC or Latin-1)
- [ ] Configure nightly export trigger in BA module (post end-of-day processing, before midnight) — confirmed: Fiserv Premier BA supports automatic scheduling
- [ ] Set up SFTP connection to Dropsilo endpoint (credentials provided at onboarding)
- [ ] Deliver first test file (historical date, e.g. last month-end) for schema validation
- [ ] Provide core system's loan type code list and deposit account type code list for mapping guide

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2026-02-20 | Initial draft — working backwards from dbt Logic View requirements. Fiserv Premier pilot pending field mapping validation. |

## Open Questions (Resolve During Pilot)

1. ~~Does Fiserv Premier BA export produce one file per object (customers, loans, deposits) or a single combined file?~~ **Resolved 2026-02-20**: Three separate files — one per object. Separate files per object is the locked standard for all core systems.
2. What is the Premier field name for `aml_risk_rating` — is this populated in the pilot bank's configuration?
3. ~~Can the BA export be scheduled to trigger automatically post-EOD, or does it require manual initiation by bank IT?~~ **Resolved 2026-02-20**: Fiserv Premier BA module supports automatic nightly scheduled exports — no manual initiation required.
4. Does Premier expose `average_daily_balance_30/90` natively, or does this require a custom report?
