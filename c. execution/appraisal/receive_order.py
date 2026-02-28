#!/usr/bin/env python3
"""
Step 1: Receive and validate appraisal order requests.
Generates order ID, validates required fields, and logs to tracking sheet.

Usage:
    python receive_order.py --json '{"property_address": "123 Main St...", ...}'
    python receive_order.py --test  # Create a test order

Returns JSON with order_id and status.
"""
from __future__ import annotations

import argparse
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
import random
import string

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from appraisal.sheets_utils import (
    ORDERS_SHEET_ID, append_row, ORDERS_COLUMNS
)

# Required fields for a valid order
REQUIRED_FIELDS = [
    'property_address',
    'property_type',
    'client_id',
    'contact_email',
]

# Valid property types
VALID_PROPERTY_TYPES = [
    'Office', 'Retail', 'Industrial', 'Multifamily',
    'Mixed-Use', 'Special Purpose', 'Land', 'Hotel'
]

# Valid urgency levels
VALID_URGENCY = ['Standard', 'Rush', 'Super Rush']

# Valid scope options
VALID_SCOPE = ['Full Appraisal', 'Limited Appraisal', 'Evaluation']


def generate_order_id() -> str:
    """Generate unique order ID: ORD-YYYY-XXXXX"""
    year = datetime.now().year
    random_part = ''.join(random.choices(string.digits, k=5))
    return f"ORD-{year}-{random_part}"


def parse_address(address: str) -> dict:
    """Extract city and state from address string."""
    # Try to parse "123 Main St, Chicago, IL 60601" format
    parts = address.split(',')
    result = {'city': '', 'state': ''}

    if len(parts) >= 2:
        result['city'] = parts[-2].strip()

    if len(parts) >= 1:
        # Last part often has "STATE ZIP"
        last = parts[-1].strip()
        state_match = re.search(r'\b([A-Z]{2})\b', last)
        if state_match:
            result['state'] = state_match.group(1)

    return result


def validate_order(data: dict) -> tuple[bool, list[str]]:
    """Validate order data. Returns (is_valid, error_messages)."""
    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")

    # Validate email format
    email = data.get('contact_email', '')
    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append(f"Invalid email format: {email}")

    # Validate property type
    prop_type = data.get('property_type', '')
    if prop_type and prop_type not in VALID_PROPERTY_TYPES:
        errors.append(f"Invalid property type: {prop_type}. Must be one of: {', '.join(VALID_PROPERTY_TYPES)}")

    # Validate urgency if provided
    urgency = data.get('urgency', 'Standard')
    if urgency not in VALID_URGENCY:
        errors.append(f"Invalid urgency: {urgency}. Must be one of: {', '.join(VALID_URGENCY)}")

    # Validate scope if provided
    scope = data.get('scope', 'Full Appraisal')
    if scope not in VALID_SCOPE:
        errors.append(f"Invalid scope: {scope}. Must be one of: {', '.join(VALID_SCOPE)}")

    return (len(errors) == 0, errors)


def create_order(data: dict) -> dict:
    """Create and log a new order. Returns order data with ID."""

    # Validate
    is_valid, errors = validate_order(data)
    if not is_valid:
        return {
            'success': False,
            'errors': errors
        }

    # Generate order ID
    order_id = generate_order_id()

    # Parse address for city/state
    address_parts = parse_address(data.get('property_address', ''))

    # Build order record
    order = {
        'order_id': order_id,
        'status': 'pending',
        'property_address': data.get('property_address', ''),
        'property_city': data.get('property_city') or address_parts['city'],
        'property_state': data.get('property_state') or address_parts['state'],
        'property_type': data.get('property_type', ''),
        'loan_amount': str(data.get('loan_amount', '')),
        'loan_purpose': data.get('loan_purpose', ''),
        'scope': data.get('scope', 'Full Appraisal'),
        'urgency': data.get('urgency', 'Standard'),
        'client_id': data.get('client_id', ''),
        'contact_name': data.get('contact_name', ''),
        'contact_email': data.get('contact_email', ''),
        'special_instructions': data.get('special_instructions', ''),
        'created_at': datetime.now().isoformat(),
        'rfp_sent_at': '',
        'quotes_deadline': '',
        'engaged_appraiser_id': '',
        'engaged_appraiser_name': '',
        'engaged_fee': '',
        'due_date': '',
        'delivered_at': ''
    }

    # Check if sheet ID is configured
    if not ORDERS_SHEET_ID:
        return {
            'success': False,
            'errors': ['APPRAISAL_ORDERS_SHEET_ID not configured in .env'],
            'order': order  # Return order data anyway for testing
        }

    # Log to sheet
    try:
        append_row(ORDERS_SHEET_ID, 'Orders', order, ORDERS_COLUMNS)
    except Exception as e:
        return {
            'success': False,
            'errors': [f'Failed to log order: {str(e)}'],
            'order': order
        }

    return {
        'success': True,
        'order_id': order_id,
        'order': order
    }


def get_test_order() -> dict:
    """Return sample order data for testing."""
    return {
        'property_address': '123 Main Street, Chicago, IL 60601',
        'property_type': 'Office',
        'loan_amount': 5000000,
        'loan_purpose': 'Refinance',
        'client_id': 'BANK-001',
        'contact_name': 'John Smith',
        'contact_email': 'jsmith@examplebank.com',
        'urgency': 'Standard',
        'scope': 'Full Appraisal',
        'special_instructions': 'Interior access available M-F 9am-5pm'
    }


def main():
    parser = argparse.ArgumentParser(
        description="Receive and validate appraisal order requests"
    )
    parser.add_argument(
        "--json",
        help="Order data as JSON string"
    )
    parser.add_argument(
        "--file",
        help="Order data from JSON file"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Create a test order with sample data"
    )

    args = parser.parse_args()

    # Get order data
    if args.test:
        data = get_test_order()
        print("Using test order data:", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
    elif args.json:
        try:
            data = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(json.dumps({'success': False, 'errors': [f'Invalid JSON: {e}']}))
            sys.exit(1)
    elif args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
    else:
        # Read from stdin
        data = json.load(sys.stdin)

    # Create order
    result = create_order(data)

    # Output result
    print(json.dumps(result, indent=2))

    if result['success']:
        print(f"\n✓ Order created: {result['order_id']}", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"\n✗ Order failed: {result['errors']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
