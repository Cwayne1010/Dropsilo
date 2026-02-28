# FIS — Data Export Setup Guide
### Dropsilo Data Feed Configuration

> **Version**: 1.0
> **Last updated**: 2026-02-22
> **Applies to**: FIS core banking systems (Horizon / IBS) using HORIZON 360 Business Intelligence, IBS Integrated BI, or User-Defined Extract capabilities.
> **Spec reference**: `b. directives/Dropsilo/dropsilo_data_spec_v0.md`
> **Audience**: Bank IT staff or operations personnel configuring the Dropsilo data feed

---

## Overview

This guide walks through creating scheduled extracts that export nightly data files to Dropsilo. Once configured, the exports run automatically after end-of-day (EOD) processing — no manual steps required.

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

- [ ] You have access to FIS BI reporting tools or custom extraction capabilities (HORIZON 360, IBS Insight, or User-Defined Extracts).
- [ ] Your user profile has query creation and scheduling permissions.
- [ ] SFTP credentials have been provided by Dropsilo.
- [ ] You have a list of your bank's loan type codes and deposit product codes.
- [ ] EOD processing completion time is known — export schedule must trigger after EOD.

---

## Global Format Settings

Apply these settings to **all three queries**.

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

---

## Report 1: Customer Export

### Step 1 — Create a New Extract
1. Open your FIS BI or Report Control Service module.
2. Select data source: **Customer Information System (CIS) / Profile Data**.
3. Name the query: `DROPSILO_CUSTOMERS`
4. Set report type to detail (one row per customer).

### Step 2 — Add Fields
Add the following fields **in this exact column order**. The header row must match the Dropsilo field name exactly.

| Col # | Dropsilo Field Name (use as header) | FIS Field (approximate) |
|-------|-------------------------------------|-----------------|
| 1 | `customer_id` | Customer ID / Primary Tax ID |
| 2 | `customer_type` | Entity Code / Customer Type (Map to Dropsilo: IND, BUS, TRUST, GOV) |
| 3 | `customer_since_date` | Date Opened |
| 4 | `city` | City |
| 5 | `state` | State |
| 6 | `zip` | Zip Code (5 digits only) |
| 7 | `relationship_officer_id` | Officer Code |
| 8 | `naics_code` | Industry / NAICS Code |
| 9 | `kyc_status` | KYC Status |
| 10 | `aml_risk_rating` | Risk Score / Risk Rating |
| 11 | `customer_status` | Status |
| 12 | `is_related_party` | Insider Indicator |

### Step 3 — Set Filters
Include all active customers.

### Step 4 — Configure Output
- Output filename: `dropsilo_customers_{YYYYMMDD}.csv`
- Output path: SFTP delivery

---

## Report 2: Loan Export

### Step 1 — Create a New Extract
1. Select data source: **Loan Core Data**.
2. Name the query: `DROPSILO_LOANS`

### Step 2 — Add Fields

| Col # | Dropsilo Field Name | FIS Field (approximate) |
|-------|---------------------|-----------------|
| 1 | `loan_id` | Loan Account Number |
| 2 | `customer_id` | Customer ID |
| 3 | `officer_id` | Assigned Officer Code |
| 4 | `loan_type_code` | Product Code / Loan Class (Map to: CRE, CI, CON, MTG, LOC, AG) |
| 5 | `loan_purpose_code` | Purpose Code |
| 6 | `collateral_type_code` | Collateral Code |
| 7 | `original_balance` | Original Commitment / Note Amount |
| 8 | `current_outstanding_balance` | Principal Balance |
| 9 | `committed_amount` | Credit Limit / Total Commitment |
| 10 | `collateral_value` | Market Value |
| 11 | `interest_rate` | Current Rate |
| 12 | `rate_type` | Rate Type (Fixed/Var) |
| 13 | `rate_index` | Index Code |
| 14 | `rate_spread` | Margin |
| 15 | `origination_date` | Origination Date |
| 16 | `maturity_date` | Maturity Date |
| 17 | `next_payment_date` | Next Payment Date |
| 18 | `payment_amount` | Payment Amount |
| 19 | `payment_frequency` | Payment Freq |
| 20 | `loan_status` | Status |
| 21 | `past_due_days` | Days Delinquent |
| 22 | `past_due_amount` | Amount Delinquent |
| 23 | `accrual_status` | Accrual Indicator |
| 24 | `risk_rating` | Risk Grade |
| 25 | `regulatory_classification` | Call Report Class / Reg Class |
| 26 | `participation_sold_amount` | Part Sold |
| 27 | `participation_purchased_amount` | Part Purchased |
| 28 | `guaranteed_amount` | Guarantee Amount |
| 29 | `guarantor_flag` | Guarantor Indicator |
| 30 | `charge_off_date` | Charge-Off Date |
| 31 | `charge_off_amount` | Charge-Off Amount |
| 32 | `recovery_amount_ytd` | YTD Recoveries |

### Step 3 — Set Filters
Include active, past due, non-accrual, and recently charged-off loans.

### Step 4 — Configure Output
- Output filename: `dropsilo_loans_{YYYYMMDD}.csv`

---

## Report 3: Deposit Export

### Step 1 — Create a New Extract
1. Select data source: **Deposit Information System / Deposit Core Data**.
2. Name the query: `DROPSILO_DEPOSITS`

### Step 2 — Add Fields

| Col # | Dropsilo Field Name | FIS Field (approximate) |
|-------|---------------------|-----------------|
| 1 | `account_id` | Deposit Account Number |
| 2 | `customer_id` | Primary Customer ID |
| 3 | `account_type_code` | Product Type (Map to: DDA, SAV, MMA, CD, IRA) |
| 4 | `open_date` | Date Opened |
| 5 | `current_balance` | Ledger Balance |
| 6 | `average_daily_balance_30` | Average Balance (Current Cycle) |
| 7 | `average_daily_balance_90` | Average Balance (YTD) |
| 8 | `interest_rate` | Interest Rate |
| 9 | `maturity_date` | Maturity Date (Time Deposits) |
| 10 | `officer_id` | Officer Code |
| 11 | `account_status` | Status |
| 12 | `overdraft_limit` | OD Limit / LOC |

### Step 3 — Set Filters
Include active, dormant, and frozen accounts.

### Step 4 — Configure Output
- Output filename: `dropsilo_deposits_{YYYYMMDD}.csv`

---

## Step 5 — Schedule All Three Reports
Configure each report to run daily, after EOD processing completes. **Execution order:** Customers first → Loans second → Deposits third.

---

## Step 6 — Configure SFTP Delivery
Configure automated file delivery to Dropsilo's SFTP endpoint using the credentials provided by Dropsilo. Leave source file in place (do not auto-delete).

---

## Step 7 — First-Run Test
Run a manual test using a historical month-end date. Deliver the files via SFTP and notify Dropsilo. Dropsilo will validate the files.

---

## Step 8 — Activate Live Schedule
Once validation passes, activate the nightly schedule.
