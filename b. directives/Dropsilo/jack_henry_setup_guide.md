# Jack Henry — Data Export Setup Guide
### Dropsilo Data Feed Configuration

> **Version**: 1.0
> **Last updated**: 2026-02-22
> **Applies to**: Jack Henry core banking systems (SilverLake / CIF 20/20) using standard data extraction tools (e.g., Jack Henry Data Hub, Operational Data Integration (ODI), or Cognos reporting)
> **Spec reference**: `b. directives/Dropsilo/dropsilo_data_spec_v0.md`
> **Audience**: Bank IT staff or operations personnel configuring the Dropsilo data feed

---

## Overview

This guide walks through creating three scheduled queries that export nightly data files to Dropsilo. Once configured, the exports run automatically after end-of-day (EOD) processing — no manual steps required.

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

- [ ] You have access to Jack Henry data extraction tools (e.g., Data Hub, ODI Custom Queries, Cognos, or Enterprise View)
- [ ] Your user profile has query creation and scheduling permissions
- [ ] SFTP credentials have been provided by Dropsilo (host, port, username, SSH key or password)
- [ ] You have a list of your bank's loan type codes and deposit account type codes
- [ ] EOD processing completion time is known — export schedule must trigger after EOD

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

### Step 1 — Create a New Query
1. Open your Jack Henry Data Hub, ODI, or Cognos reporting tool.
2. Select data source: **Customer Core (CustDetail / Cust_Acct)**.
3. Name the query: `DROPSILO_CUSTOMERS`
4. Set report type to detail (one row per customer).

### Step 2 — Add Fields
Add the following fields **in this exact column order**. The header row must match the Dropsilo field name exactly.

| Col # | Dropsilo Field Name (use as header) | Jack Henry Field |
|-------|-------------------------------------|-----------------|
| 1 | `customer_id` | Tax ID / CIF Number |
| 2 | `customer_type` | Tax Code / Entity Type (Map to Dropsilo: IND, BUS, TRUST, GOV) |
| 3 | `customer_since_date` | Date Opened |
| 4 | `city` | City |
| 5 | `state` | State |
| 6 | `zip` | Zip Code (5 digits only) |
| 7 | `relationship_officer_id` | Officer Code |
| 8 | `naics_code` | NAICS/SIC Code |
| 9 | `kyc_status` | CIP Status |
| 10 | `aml_risk_rating` | BSA Risk Rating |
| 11 | `customer_status` | CIF Status |
| 12 | `is_related_party` | Insider Code |

### Step 3 — Set Filters
Include all customers where status is not completely purged. Do not filter out inactive/dormant customers.

### Step 4 — Configure Output
- Output filename: `dropsilo_customers_{YYYYMMDD}.csv`
- Output path: SFTP delivery

---

## Report 2: Loan Export

### Step 1 — Create a New Query
1. Select data source: **Loan Master (Ln_Acct / Cust_Acct)**.
2. Name the query: `DROPSILO_LOANS`

### Step 2 — Add Fields

| Col # | Dropsilo Field Name | Jack Henry Field |
|-------|---------------------|-----------------|
| 1 | `loan_id` | Account Number / Note Number |
| 2 | `customer_id` | CIF Number / Tax ID |
| 3 | `officer_id` | Loan Officer Code |
| 4 | `loan_type_code` | Call Code / Loan Code (Map to: CRE, CI, CON, MTG, LOC, AG) |
| 5 | `loan_purpose_code` | Purpose Code |
| 6 | `collateral_type_code` | Collateral Code |
| 7 | `original_balance` | Original Amount |
| 8 | `current_outstanding_balance` | Current Principal Balance |
| 9 | `committed_amount` | Commitment/Credit Limit |
| 10 | `collateral_value` | Appraised Value |
| 11 | `interest_rate` | Current Interest Rate |
| 12 | `rate_type` | Rate Code (Fixed/Variable) |
| 13 | `rate_index` | Base Rate / Index Code |
| 14 | `rate_spread` | Variance / Margin |
| 15 | `origination_date` | Date Opened / Origination Date |
| 16 | `maturity_date` | Maturity Date |
| 17 | `next_payment_date` | Next Due Date |
| 18 | `payment_amount` | Payment Amount |
| 19 | `payment_frequency` | Payment Frequency Code |
| 20 | `loan_status` | Account Status |
| 21 | `past_due_days` | Days Past Due |
| 22 | `past_due_amount` | Past Due Amount |
| 23 | `accrual_status` | Non-Accrual Flag |
| 24 | `risk_rating` | Loan Grade / Risk Rating |
| 25 | `regulatory_classification` | Exam Grade |
| 26 | `participation_sold_amount` | Participation Sold |
| 27 | `participation_purchased_amount` | Participation Purchased |
| 28 | `guaranteed_amount` | Guaranteed Amount / SBA |
| 29 | `guarantor_flag` | Guarantor Code |
| 30 | `charge_off_date` | Date Charged Off |
| 31 | `charge_off_amount` | Charge Off Amount |
| 32 | `recovery_amount_ytd` | Recoveries YTD |

### Step 3 — Set Filters
Include active, past due, non-accrual, and recently charged-off loans. 

### Step 4 — Configure Output
- Output filename: `dropsilo_loans_{YYYYMMDD}.csv`

---

## Report 3: Deposit Export

### Step 1 — Create a New Query
1. Select data source: **Deposit Master (DepAcct / Dep_AcctTitle)**.
2. Name the query: `DROPSILO_DEPOSITS`

### Step 2 — Add Fields

| Col # | Dropsilo Field Name | Jack Henry Field |
|-------|---------------------|-----------------|
| 1 | `account_id` | Account Number |
| 2 | `customer_id` | Primary CIF Number |
| 3 | `account_type_code` | Application / Product Code (Map to: DDA, SAV, MMA, CD, IRA) |
| 4 | `open_date` | Date Opened |
| 5 | `current_balance` | Current Ledger Balance |
| 6 | `average_daily_balance_30` | Average Balance MTD |
| 7 | `average_daily_balance_90` | Average Balance YTD/QTD |
| 8 | `interest_rate` | Interest Rate / APY |
| 9 | `maturity_date` | Maturity Date (CDs/IRAs) |
| 10 | `officer_id` | Officer Code |
| 11 | `account_status` | Status Code / Active Flag |
| 12 | `overdraft_limit` | OD Limit |

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
