# Fiserv Premier — BA Export Setup Guide
### Dropsilo Data Feed Configuration

> **Version**: 1.0
> **Last updated**: 2026-02-20
> **Applies to**: Fiserv Premier core banking system — Business Analytics (BA) module
> **Spec reference**: `b. directives/Dropsilo/dropsilo_data_spec_v0.md`
> **Audience**: Bank IT staff or operations personnel configuring the Dropsilo data feed

---

## Overview

This guide walks through creating three scheduled BA reports that export nightly data files to Dropsilo. Once configured, the exports run automatically after end-of-day processing — no manual steps required.

**Three reports to create:**

| Report | Output Filename | Estimated Row Count |
|--------|----------------|-------------------|
| Customer Export | `dropsilo_customers_YYYYMMDD.csv` | 1 row per active customer |
| Loan Export | `dropsilo_loans_YYYYMMDD.csv` | 1 row per active loan account |
| Deposit Export | `dropsilo_deposits_YYYYMMDD.csv` | 1 row per active deposit account |

**Time required:** Approximately 2–3 hours for initial setup. Once configured, fully automated.

---

## Prerequisites

Before starting, confirm the following:

- [ ] You have access to the Fiserv Premier Business Analytics (BA) module
- [ ] Your user profile has report creation and scheduling permissions
- [ ] SFTP credentials have been provided by Dropsilo (host, port, username, SSH key or password)
- [ ] You have a list of your bank's loan type codes and deposit account type codes (needed for the mapping tables in each report)
- [ ] End-of-day (EOD) processing completion time is known — export schedule must trigger after EOD

---

## Global Format Settings

Apply these settings to **all three reports**. Configure once if BA allows global defaults; otherwise apply individually to each report.

| Setting | Value |
|---------|-------|
| File format | CSV |
| Delimiter | Pipe (`\|`) |
| Character encoding | UTF-8 |
| Include header row | Yes |
| Date format | YYYY-MM-DD |
| Amount format | Decimal numeric, no currency symbol, no thousands separator (e.g. `1234567.89`) |
| Null / empty fields | Export as empty string — do not use `NULL`, `N/A`, or `0` as placeholders for missing text |
| Compression | None (uncompressed) |

> **Note on encoding:** If Premier defaults to a different encoding (e.g. Latin-1), explicitly set UTF-8. If UTF-8 is not available, contact Dropsilo before proceeding — encoding mismatches cause silent data corruption.

---

## Report 1: Customer Export

### Step 1 — Create a New Report

1. Open the BA module from the Premier main menu
2. Select **New Report** (or equivalent — menu path varies by Premier version)
3. Select data source: **Customer Information File (CIF)** or **Customer Master**
4. Name the report: `DROPSILO_CUSTOMERS`
5. Set report type: **Detail** (one row per customer, not summary/aggregate)

### Step 2 — Add Fields

Add the following fields **in this exact column order**. The header row must match the Dropsilo field name exactly.

| Col # | Dropsilo Field Name (use as header) | Premier BA Field | Transformation Required |
|-------|-------------------------------------|-----------------|------------------------|
| 1 | `customer_id` | Customer Number / CIF Number | None — export as-is |
| 2 | `customer_type` | Customer Type / Customer Class | Map codes to Dropsilo values (see table below) |
| 3 | `customer_since_date` | Open Date / Relationship Open Date | Format as YYYY-MM-DD |
| 4 | `city` | City | None |
| 5 | `state` | State | 2-letter code — confirm Premier stores as abbreviation |
| 6 | `zip` | Zip Code / Postal Code | Export 5 digits only — strip ZIP+4 if present |
| 7 | `relationship_officer_id` | Primary Officer Code / Assigned Officer | None — export officer code, not name |
| 8 | `naics_code` | NAICS Code / SIC Code | Export NAICS if available; leave empty if not |
| 9 | `kyc_status` | KYC Status / CIP Status | Map to: `VERIFIED`, `PENDING`, `REVIEW`, `FAILED` — leave empty if not in your configuration |
| 10 | `aml_risk_rating` | BSA Risk Rating / AML Risk Rating | Map to: `LOW`, `MEDIUM`, `HIGH` — leave empty if not populated |
| 11 | `customer_status` | Customer Status / Active Flag | Map codes to: `ACTIVE`, `INACTIVE`, `DECEASED`, `CLOSED` |
| 12 | `is_related_party` | Related Party Flag / Insider Flag | Map to `Y` or `N` — leave empty if not tracked |

**Do NOT include:** Customer name, SSN/EIN, street address, date of birth, phone number, email. These fields must remain in Premier.

#### Customer Type Code Mapping

Premier uses bank-configured codes. Map your bank's codes to Dropsilo values:

| Your Premier Code | Dropsilo Value | Description |
|------------------|---------------|-------------|
| _(confirm)_ | `IND` | Individual / personal |
| _(confirm)_ | `BUS` | Business / commercial |
| _(confirm)_ | `TRUST` | Trust |
| _(confirm)_ | `GOV` | Government / municipality |

### Step 3 — Set Filters

Include all customers where status is not permanently closed/purged. Recommended filter:

- `customer_status` is not equal to: _(your code for purged/archived)_

Do not filter out inactive or dormant customers — Dropsilo needs the full picture.

### Step 4 — Configure Output

- Output filename: `dropsilo_customers_{YYYYMMDD}.csv`
  - Use BA's date variable token for YYYYMMDD — typically `{RUNDATE}` or `%DATE%` (confirm token syntax in your Premier version)
- Output path: SFTP delivery (configured in Step 6)

---

## Report 2: Loan Export

### Step 1 — Create a New Report

1. Select **New Report**
2. Select data source: **Loan Master** or **Loan Account File**
3. Name the report: `DROPSILO_LOANS`
4. Report type: **Detail** (one row per loan account)

### Step 2 — Add Fields

| Col # | Dropsilo Field Name | Premier BA Field | Transformation Required |
|-------|---------------------|-----------------|------------------------|
| 1 | `loan_id` | Account Number / Loan Number | None |
| 2 | `customer_id` | Customer Number / CIF Number | None — must match customer_id in customers file |
| 3 | `officer_id` | Officer Code / Loan Officer | None — export code, not name |
| 4 | `loan_type_code` | Loan Type / Product Code | Map to Dropsilo values (see table below) |
| 5 | `loan_purpose_code` | Purpose Code | Export as-is if available; leave empty if not |
| 6 | `collateral_type_code` | Collateral Type / Collateral Code | Map to: `RE`, `EQ`, `AR`, `VEH`, `UNS`, `CD` |
| 7 | `original_balance` | Original Amount / Note Amount | Decimal, no formatting |
| 8 | `current_outstanding_balance` | Current Balance / Principal Balance | Decimal, no formatting |
| 9 | `committed_amount` | Commitment Amount / Credit Limit | For lines of credit only; leave empty for term loans |
| 10 | `collateral_value` | Collateral Value / Appraised Value | Most recent value on file; leave empty if not tracked |
| 11 | `interest_rate` | Interest Rate / Note Rate | Decimal percent (e.g. `6.75`) — confirm Premier stores as percent not decimal fraction |
| 12 | `rate_type` | Rate Type / Fixed-Variable Flag | Map to `FIXED` or `VARIABLE` |
| 13 | `rate_index` | Rate Index / Index Code | Map to: `PRIME`, `SOFR`, `FIXED` — leave empty for fixed rate loans |
| 14 | `rate_spread` | Rate Margin / Spread / Variance | Decimal percent — leave empty for fixed rate loans |
| 15 | `origination_date` | Origination Date / Open Date | Format as YYYY-MM-DD |
| 16 | `maturity_date` | Maturity Date | Format as YYYY-MM-DD |
| 17 | `next_payment_date` | Next Due Date / Next Payment Date | Format as YYYY-MM-DD |
| 18 | `payment_amount` | Payment Amount / Regular Payment | Decimal |
| 19 | `payment_frequency` | Payment Frequency / Payment Code | Map to: `MONTHLY`, `QUARTERLY`, `SEMIANNUAL`, `ANNUAL`, `INTEREST_ONLY`, `DEMAND` |
| 20 | `loan_status` | Loan Status / Account Status | Map to: `CURRENT`, `PAST_DUE`, `NON_ACCRUAL`, `CHARGEOFF`, `PAID`, `DEMAND` |
| 21 | `past_due_days` | Days Past Due / Delinquency Days | Integer — export `0` if current |
| 22 | `past_due_amount` | Past Due Amount / Delinquent Amount | Decimal — export `0.00` if current |
| 23 | `accrual_status` | Accrual Code / Non-Accrual Flag | Map to `ACCRUAL` or `NON_ACCRUAL` |
| 24 | `risk_rating` | Risk Rating / Loan Grade | Export as-is (bank's own scale is acceptable) |
| 25 | `regulatory_classification` | Regulatory Classification / Exam Grade | Map to: `PASS`, `SPECIAL_MENTION`, `SUBSTANDARD`, `DOUBTFUL`, `LOSS` |
| 26 | `participation_sold_amount` | Participation Sold / Sold Participation | Decimal; leave empty if not applicable |
| 27 | `participation_purchased_amount` | Participation Purchased / Purchased Participation | Decimal; leave empty if not applicable |
| 28 | `guaranteed_amount` | Guaranteed Amount / SBA Guarantee | Decimal; leave empty if not applicable |
| 29 | `guarantor_flag` | Guarantor Flag / Guaranty Code | Map to `Y` or `N` |
| 30 | `charge_off_date` | Charge Off Date | Format as YYYY-MM-DD; leave empty if not charged off |
| 31 | `charge_off_amount` | Charge Off Amount | Decimal; leave empty if not charged off |
| 32 | `recovery_amount_ytd` | Recovery Amount YTD / Recoveries | Decimal; leave empty if none |

#### Loan Type Code Mapping

Premier loan type codes are bank-configured. Map your bank's codes to Dropsilo standard values:

| Your Premier Code | Dropsilo Value | Description |
|------------------|---------------|-------------|
| _(confirm)_ | `CRE` | Commercial Real Estate |
| _(confirm)_ | `CI` | Commercial & Industrial |
| _(confirm)_ | `CON` | Consumer |
| _(confirm)_ | `MTG` | Residential Mortgage |
| _(confirm)_ | `LOC` | Line of Credit |
| _(confirm)_ | `AG` | Agricultural |
| _(confirm)_ | _(other)_ | Add rows as needed |

### Step 3 — Set Filters

Include all active and recently closed/charged-off loans. Recommended:

- Include: `CURRENT`, `PAST_DUE`, `NON_ACCRUAL`, `CHARGEOFF`
- Exclude: `PAID` loans closed more than 12 months ago (reduces file size; adjust window as needed)

### Step 4 — Configure Output

- Output filename: `dropsilo_loans_{YYYYMMDD}.csv`

---

## Report 3: Deposit Export

### Step 1 — Create a New Report

1. Select **New Report**
2. Select data source: **Deposit Master** or **Deposit Account File**
3. Name the report: `DROPSILO_DEPOSITS`
4. Report type: **Detail** (one row per account)

### Step 2 — Add Fields

| Col # | Dropsilo Field Name | Premier BA Field | Transformation Required |
|-------|---------------------|-----------------|------------------------|
| 1 | `account_id` | Account Number | None |
| 2 | `customer_id` | Customer Number / Primary CIF | None — must match customer_id in customers file |
| 3 | `account_type_code` | Account Type / Product Code | Map to: `DDA`, `SAV`, `MMA`, `CD`, `IRA`, `LOC` (see table below) |
| 4 | `open_date` | Open Date | Format as YYYY-MM-DD |
| 5 | `current_balance` | Current Balance / Ledger Balance | Decimal |
| 6 | `average_daily_balance_30` | Average Daily Balance (30-day) | Decimal; leave empty if not available natively |
| 7 | `average_daily_balance_90` | Average Daily Balance (90-day) | Decimal; leave empty if not available natively |
| 8 | `interest_rate` | Interest Rate / Dividend Rate / APY | Decimal percent |
| 9 | `maturity_date` | Maturity Date | Format as YYYY-MM-DD; CDs and IRAs only |
| 10 | `officer_id` | Officer Code / Assigned Officer | Export code, not name; leave empty if not assigned |
| 11 | `account_status` | Account Status / Active Flag | Map to: `ACTIVE`, `DORMANT`, `CLOSED`, `FROZEN` |
| 12 | `overdraft_limit` | Overdraft Limit / ODP Limit | Decimal; leave empty if no ODP |

#### Deposit Account Type Code Mapping

| Your Premier Code | Dropsilo Value | Description |
|------------------|---------------|-------------|
| _(confirm)_ | `DDA` | Demand Deposit / Checking |
| _(confirm)_ | `SAV` | Savings |
| _(confirm)_ | `MMA` | Money Market |
| _(confirm)_ | `CD` | Certificate of Deposit |
| _(confirm)_ | `IRA` | Individual Retirement Account |
| _(confirm)_ | `LOC` | Deposit Line of Credit |

### Step 3 — Set Filters

- Include: `ACTIVE`, `DORMANT`, `FROZEN`
- Exclude: `CLOSED` accounts closed more than 12 months ago

### Step 4 — Configure Output

- Output filename: `dropsilo_deposits_{YYYYMMDD}.csv`

---

## Step 5 — Schedule All Three Reports

Configure each report to run on the same nightly schedule:

| Setting | Value |
|---------|-------|
| Frequency | Daily |
| Trigger | After EOD processing completes |
| Recommended run time | 11:00 PM – 2:00 AM (confirm your EOD window) |
| Run days | Monday – Sunday (all days) |
| Execution order | Customers first → Loans second → Deposits third |

> **Why order matters:** The validation step confirms that all `customer_id` values in the loans and deposits files exist in the customers file. Running customers first ensures it is always the most current file if any timing gap occurs.

---

## Step 6 — Configure SFTP Delivery

For each report, configure automated file delivery to Dropsilo's SFTP endpoint:

| Setting | Value |
|---------|-------|
| Delivery method | SFTP |
| Host | _(provided by Dropsilo)_ |
| Port | _(provided by Dropsilo — typically 22)_ |
| Username | _(provided by Dropsilo)_ |
| Authentication | SSH key or password _(provided by Dropsilo)_ |
| Remote directory | `/incoming/` _(confirm with Dropsilo)_ |
| Post-delivery action | Leave source file in place (do not auto-delete) |

> **Firewall note:** Your IT team may need to whitelist the Dropsilo SFTP server IP on your outbound firewall. Request the static IP from Dropsilo before testing.

---

## Step 7 — First-Run Test

Before activating the live nightly schedule, run a manual test using a historical date.

### Test procedure

1. Run each report manually with a prior month-end date (e.g. January 31)
2. Deliver the three test files to Dropsilo via SFTP
3. Notify Dropsilo that test files have been delivered — provide the date used
4. Dropsilo will run validation and return a report within 1 business day

### What Dropsilo validates on the test file

- [ ] All required fields are present and non-empty
- [ ] `customer_id` values in loans and deposits files match customers file
- [ ] No duplicate `loan_id` or `account_id` values
- [ ] Date fields are in YYYY-MM-DD format
- [ ] Amount fields are numeric with no formatting characters
- [ ] File encoding is UTF-8
- [ ] Delimiter is pipe (`|`)
- [ ] Filename follows `dropsilo_{object}_{YYYYMMDD}.csv` convention

### Common first-run issues

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| Dates appear as `MM/DD/YYYY` | BA defaults to display format | Change BA date output format to ISO 8601 |
| Amounts include `$` or `,` | BA applying display formatting | Disable currency/number formatting on amount fields |
| File opens with garbled characters | Encoding mismatch | Confirm UTF-8 is selected; check for BOM header |
| `customer_id` mismatch errors | Loans/deposits referencing customers not in export | Check customer export filter — ensure all active customers are included |
| Duplicate loan IDs | Report pulling same loan twice | Check for join issues in report definition — likely a collateral or guarantor sub-table join |

---

## Step 8 — Activate Live Schedule

After Dropsilo confirms the test file passes validation:

1. Activate the nightly schedule for all three reports
2. Confirm the first live run completes and files arrive at Dropsilo SFTP
3. Notify Dropsilo that live feed is active

From this point, no manual action is required. Dropsilo monitors file receipt and will contact you if a file is missing or fails validation.

---

## Ongoing Maintenance

| Event | Action Required |
|-------|----------------|
| Premier version upgrade | Re-test all three reports — field names or code values may change |
| New loan type code added | Update the loan type code mapping table and notify Dropsilo |
| New deposit product type added | Update deposit account type mapping and notify Dropsilo |
| EOD processing time changes | Update scheduled run time to remain post-EOD |
| SFTP credentials rotate | Update BA delivery configuration with new credentials |

---

## Support Contacts

| Contact | Purpose |
|---------|---------|
| Dropsilo onboarding team | SFTP credentials, validation results, data questions |
| Fiserv Premier support | BA module configuration, scheduling, encoding settings |

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2026-02-20 | Initial release — Fiserv Premier pilot. Field mapping tables to be completed during pilot. |
