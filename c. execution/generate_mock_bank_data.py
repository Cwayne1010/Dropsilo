import csv
import random
import os
from datetime import datetime, timedelta

# Dropsilo Data Spec v0 - Synthetic Data Generator
# Output Format: Pipe-delimited UTF-8 CSV
# This script generates synthetic banking data (customers, loans, deposits) 
# conforming strictly to the dropsilo_data_spec_v0 schema for local prototyping.

OUTPUT_DIR = ".tmp/mock_data"
NUM_CUSTOMERS = 100

def random_date(start_year=2010, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def generate_customers(num_customers):
    customers = []
    types = ['IND', 'BUS', 'TRUST', 'GOV']
    statuses = ['ACTIVE', 'INACTIVE', 'DECEASED', 'CLOSED']
    kyc_statuses = ['VERIFIED', 'PENDING', 'REVIEW']
    risk_ratings = ['LOW', 'MEDIUM', 'HIGH']
    
    for i in range(1, num_customers + 1):
        cust_id = f"CUST{i:06d}"
        cust_type = random.choices(types, weights=[0.6, 0.3, 0.08, 0.02])[0]
        since_date = random_date(2010, 2025).strftime("%Y-%m-%d")
        
        customers.append({
            'customer_id': cust_id,
            'customer_type': cust_type,
            'customer_since_date': since_date,
            'city': random.choice(['Austin', 'Dallas', 'Houston', 'San Antonio', 'Waco']),
            'state': 'TX',
            'zip': f"{random.randint(75000, 79999)}",
            'relationship_officer_id': f"OFF{random.randint(1, 10):03d}",
            'naics_code': f"{random.randint(111110, 999990)}" if cust_type == 'BUS' else "",
            'kyc_status': random.choice(kyc_statuses),
            'aml_risk_rating': random.choice(risk_ratings),
            'customer_status': random.choices(statuses, weights=[0.8, 0.12, 0.03, 0.05])[0],
            'is_related_party': random.choices(['Y', 'N'], weights=[0.02, 0.98])[0],
        })
    return customers

def generate_loans(customers):
    loans = []
    loan_types = ['CRE', 'CI', 'CON', 'MTG', 'LOC', 'AG']
    statuses = ['CURRENT', 'PAST_DUE', 'NON_ACCRUAL', 'CHARGEOFF', 'PAID', 'DEMAND']
    
    loan_counter = 1
    for cust in customers:
        if cust['customer_status'] == 'CLOSED':
            continue
            
        # 1 to 3 loans per customer
        for _ in range(random.randint(1, 3)):
            loan_id = f"LOAN{loan_counter:08d}"
            loan_counter += 1
            
            status = random.choices(statuses, weights=[0.80, 0.05, 0.02, 0.02, 0.08, 0.03])[0]
            is_past_due = status in ('PAST_DUE', 'NON_ACCRUAL')
            is_charged_off = status == 'CHARGEOFF'

            orig_bal = round(random.uniform(10000, 5000000), 2)
            curr_bal = 0.00 if status in ('PAID', 'CHARGEOFF') else round(random.uniform(1000, orig_bal), 2)
            
            rate_type = random.choice(['FIXED', 'VARIABLE'])
            loans.append({
                'loan_id': loan_id,
                'customer_id': cust['customer_id'],
                'officer_id': cust['relationship_officer_id'],
                'loan_type_code': random.choice(loan_types),
                'loan_purpose_code': "",
                'collateral_type_code': random.choice(['RE', 'EQ', 'AR', 'VEH', 'UNS']),
                'original_balance': f"{orig_bal:.2f}",
                'current_outstanding_balance': f"{curr_bal:.2f}",
                'committed_amount': f"{orig_bal:.2f}" if random.random() > 0.8 else "",
                'collateral_value': f"{orig_bal * random.uniform(1.2, 1.5):.2f}",
                'interest_rate': f"{random.uniform(4.0, 9.5):.2f}",
                'rate_type': rate_type,
                'rate_index': random.choice(['PRIME', 'SOFR']) if rate_type == 'VARIABLE' else '',
                'rate_spread': f"{random.uniform(0.5, 3.0):.2f}" if random.random() > 0.5 else "",
                'origination_date': random_date(2018, 2025).strftime("%Y-%m-%d"),
                'maturity_date': random_date(2026, 2035).strftime("%Y-%m-%d"),
                'next_payment_date': random_date(2026, 2026).strftime("%Y-%m-%d"),
                'payment_amount': f"{curr_bal * 0.01:.2f}",
                'payment_frequency': random.choice(['MONTHLY', 'QUARTERLY']),
                'loan_status': status,
                'past_due_days': str(random.randint(1, 90)) if is_past_due else "0",
                'past_due_amount': f"{random.uniform(500, 5000):.2f}" if is_past_due else "0.00",
                'accrual_status': 'NON_ACCRUAL' if status == 'NON_ACCRUAL' else 'ACCRUAL',
                'risk_rating': str(random.randint(1, 8)),
                'regulatory_classification': random.choice(['PASS', 'PASS', 'SPECIAL_MENTION', 'SUBSTANDARD']),
                'participation_sold_amount': "",
                'participation_purchased_amount': "",
                'guaranteed_amount': "",
                'guarantor_flag': random.choice(['Y', 'N']),
                'charge_off_date': random_date(2020, 2025).strftime("%Y-%m-%d") if is_charged_off else "",
                'charge_off_amount': f"{orig_bal:.2f}" if is_charged_off else "",
                'recovery_amount_ytd': f"{orig_bal * random.uniform(0, 0.3):.2f}" if is_charged_off else ""
            })
    return loans

def generate_deposits(customers):
    deposits = []
    acct_types = ['DDA', 'SAV', 'MMA', 'CD', 'IRA', 'LOC']
    statuses = ['ACTIVE', 'DORMANT', 'CLOSED', 'FROZEN']
    
    acct_counter = 1
    for cust in customers:
        if cust['customer_status'] == 'CLOSED':
            continue
            
        # 1 to 4 deposit accounts per customer
        for _ in range(random.randint(1, 4)):
            acct_id = f"DEP{acct_counter:08d}"
            acct_counter += 1
            
            status = random.choices(statuses, weights=[0.88, 0.05, 0.05, 0.02])[0]
            curr_bal = round(random.uniform(100, 250000), 2) if status != 'CLOSED' else 0.00
            
            deposits.append({
                'account_id': acct_id,
                'customer_id': cust['customer_id'],
                'account_type_code': random.choice(acct_types),
                'open_date': random_date(2015, 2025).strftime("%Y-%m-%d"),
                'current_balance': f"{curr_bal:.2f}",
                'average_daily_balance_30': f"{curr_bal * random.uniform(0.9, 1.1):.2f}",
                'average_daily_balance_90': f"{curr_bal * random.uniform(0.85, 1.15):.2f}",
                'interest_rate': f"{random.uniform(0.1, 4.5):.2f}",
                'maturity_date': random_date(2026, 2028).strftime("%Y-%m-%d") if random.random() > 0.8 else "",
                'officer_id': cust['relationship_officer_id'],
                'account_status': status,
                'overdraft_limit': f"{random.choice([0, 500, 1000, 2500]):.2f}"
            })
    return deposits

def write_csv(filename, data, fieldnames):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Generated {filepath} ({len(data)} rows)")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d")
    
    print("Generating synthetic bank data...")
    customers = generate_customers(NUM_CUSTOMERS)
    loans = generate_loans(customers)
    deposits = generate_deposits(customers)
    
    # Write Customers
    cust_fields = [
        'customer_id', 'customer_type', 'customer_since_date', 'city', 'state', 'zip', 
        'relationship_officer_id', 'naics_code', 'kyc_status', 'aml_risk_rating', 
        'customer_status', 'is_related_party'
    ]
    write_csv(f"dropsilo_customers_{today_str}.csv", customers, cust_fields)
    
    # Write Loans
    loan_fields = [
        'loan_id', 'customer_id', 'officer_id', 'loan_type_code', 'loan_purpose_code',
        'collateral_type_code', 'original_balance', 'current_outstanding_balance',
        'committed_amount', 'collateral_value', 'interest_rate', 'rate_type',
        'rate_index', 'rate_spread', 'origination_date', 'maturity_date',
        'next_payment_date', 'payment_amount', 'payment_frequency', 'loan_status',
        'past_due_days', 'past_due_amount', 'accrual_status', 'risk_rating',
        'regulatory_classification', 'participation_sold_amount',
        'participation_purchased_amount', 'guaranteed_amount', 'guarantor_flag',
        'charge_off_date', 'charge_off_amount', 'recovery_amount_ytd'
    ]
    write_csv(f"dropsilo_loans_{today_str}.csv", loans, loan_fields)
    
    # Write Deposits
    dep_fields = [
        'account_id', 'customer_id', 'account_type_code', 'open_date', 
        'current_balance', 'average_daily_balance_30', 'average_daily_balance_90',
        'interest_rate', 'maturity_date', 'officer_id', 'account_status', 'overdraft_limit'
    ]
    write_csv(f"dropsilo_deposits_{today_str}.csv", deposits, dep_fields)
    
    print("\nData generation complete. Ready for Snowflake or dbt import.")

if __name__ == "__main__":
    main()
