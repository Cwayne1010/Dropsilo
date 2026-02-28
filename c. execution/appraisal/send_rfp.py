#!/usr/bin/env python3
"""
Step 3: Send RFP (Request for Proposal) emails to selected appraisers.
Sends quote request emails and updates order status.

Usage:
    python send_rfp.py --order-id ORD-2024-12345
    python send_rfp.py --order-id ORD-2024-12345 --appraisers APP-001 APP-002 APP-003

Returns JSON with email send results.
"""
from __future__ import annotations

import argparse
import json
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from appraisal.sheets_utils import (
    ORDERS_SHEET_ID, PANEL_SHEET_ID,
    read_sheet, find_row_by_id, update_row, ORDERS_COLUMNS
)
from appraisal.find_appraisers import find_appraisers_for_order


def get_smtp_config() -> dict:
    """Get SMTP configuration from environment."""
    return {
        'host': os.getenv('SMTP_HOST'),
        'port': int(os.getenv('SMTP_PORT', 587)),
        'user': os.getenv('SMTP_USER'),
        'password': os.getenv('SMTP_PASSWORD'),
        'from_name': os.getenv('SENDER_NAME', 'Appraisal Order Desk')
    }


def get_rfp_email_content(order: dict, appraiser: dict, deadline: str) -> tuple[str, str]:
    """
    Generate RFP email subject and body.

    Returns:
        (subject, body) tuple
    """
    company_name = os.getenv('COMPANY_NAME', 'Appraisal Management')

    subject = f"Quote Request - {order.get('property_type', 'Commercial')} Appraisal - {order.get('property_city', '')}, {order.get('property_state', '')}"

    body = f"""Dear {appraiser.get('name', 'Appraiser')},

We have an appraisal assignment available and would like to request your fee and turnaround quote.

ORDER DETAILS
─────────────────────────────────
Order #: {order.get('order_id', '')}
Property: {order.get('property_address', '')}
Type: {order.get('property_type', '')}
Scope: {order.get('scope', 'Full Appraisal')}
Urgency: {order.get('urgency', 'Standard')}

LOAN INFORMATION
─────────────────────────────────
Loan Amount: ${int(float(order.get('loan_amount', 0) or 0)):,}
Purpose: {order.get('loan_purpose', 'N/A')}

QUOTE DEADLINE
─────────────────────────────────
Please submit your quote by: {deadline}

TO SUBMIT YOUR QUOTE
─────────────────────────────────
Reply to this email with:
• Your fee for this assignment
• Your turnaround time (business days)
• Any questions or clarifications needed

If you are unavailable or unable to take this assignment, please let us know so we can reassign promptly.

{f"SPECIAL INSTRUCTIONS: {order.get('special_instructions')}" if order.get('special_instructions') else ""}

Best regards,
{company_name} Order Desk
"""

    return subject, body


def send_email(to_email: str, subject: str, body: str, smtp_config: dict) -> bool:
    """Send a single email via SMTP."""
    if not all([smtp_config['host'], smtp_config['user'], smtp_config['password']]):
        raise ValueError("SMTP configuration incomplete. Check SMTP_HOST, SMTP_USER, SMTP_PASSWORD in .env")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{smtp_config['from_name']} <{smtp_config['user']}>"
    msg['To'] = to_email

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
        server.starttls()
        server.login(smtp_config['user'], smtp_config['password'])
        server.send_message(msg)

    return True


def send_rfp_emails(order_id: str, appraiser_ids: list[str] = None, dry_run: bool = False) -> dict:
    """
    Send RFP emails for an order.

    Args:
        order_id: Order ID
        appraiser_ids: Specific appraiser IDs to contact (optional, will auto-select if not provided)
        dry_run: If True, don't actually send emails

    Returns:
        Dict with results
    """

    # Get order
    result = find_row_by_id(ORDERS_SHEET_ID, 'Orders', 'order_id', order_id)
    if not result:
        return {
            'success': False,
            'errors': [f'Order not found: {order_id}']
        }

    row_index, order = result

    # Get appraisers
    if appraiser_ids:
        # Load specific appraisers
        all_appraisers = read_sheet(PANEL_SHEET_ID, 'Appraiser Panel!A:Z')
        appraisers = [a for a in all_appraisers if a.get('appraiser_id') in appraiser_ids]
    else:
        # Auto-select appraisers
        find_result = find_appraisers_for_order(order_id=order_id)
        if not find_result['success']:
            return find_result
        appraisers = find_result.get('candidates', [])

    if not appraisers:
        return {
            'success': False,
            'errors': ['No appraisers to send RFP to']
        }

    # Calculate deadline (48 hours from now)
    deadline = (datetime.now() + timedelta(hours=48)).strftime('%B %d, %Y at %I:%M %p')

    # Get SMTP config
    smtp_config = get_smtp_config()

    # Send emails
    results = []
    for appraiser in appraisers:
        email = appraiser.get('email')
        if not email:
            results.append({
                'appraiser_id': appraiser.get('appraiser_id'),
                'name': appraiser.get('name'),
                'status': 'skipped',
                'reason': 'No email address'
            })
            continue

        subject, body = get_rfp_email_content(order, appraiser, deadline)

        if dry_run:
            results.append({
                'appraiser_id': appraiser.get('appraiser_id'),
                'name': appraiser.get('name'),
                'email': email,
                'status': 'dry_run',
                'subject': subject
            })
        else:
            try:
                send_email(email, subject, body, smtp_config)
                results.append({
                    'appraiser_id': appraiser.get('appraiser_id'),
                    'name': appraiser.get('name'),
                    'email': email,
                    'status': 'sent'
                })
            except Exception as e:
                results.append({
                    'appraiser_id': appraiser.get('appraiser_id'),
                    'name': appraiser.get('name'),
                    'email': email,
                    'status': 'failed',
                    'error': str(e)
                })

    # Update order status
    sent_count = sum(1 for r in results if r['status'] == 'sent')
    if sent_count > 0 and not dry_run:
        order['status'] = 'rfp_sent'
        order['rfp_sent_at'] = datetime.now().isoformat()
        order['quotes_deadline'] = (datetime.now() + timedelta(hours=48)).isoformat()

        try:
            update_row(ORDERS_SHEET_ID, 'Orders', row_index, order, ORDERS_COLUMNS)
        except Exception as e:
            return {
                'success': True,
                'warning': f'Emails sent but failed to update order: {str(e)}',
                'results': results,
                'sent_count': sent_count
            }

    return {
        'success': True,
        'order_id': order_id,
        'results': results,
        'sent_count': sent_count,
        'deadline': deadline,
        'dry_run': dry_run
    }


def main():
    parser = argparse.ArgumentParser(
        description="Send RFP emails to appraisers for an order"
    )
    parser.add_argument(
        "--order-id",
        required=True,
        help="Order ID"
    )
    parser.add_argument(
        "--appraisers",
        nargs="*",
        help="Specific appraiser IDs to contact (auto-selects if not provided)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview emails without sending"
    )

    args = parser.parse_args()

    result = send_rfp_emails(
        order_id=args.order_id,
        appraiser_ids=args.appraisers,
        dry_run=args.dry_run
    )

    print(json.dumps(result, indent=2))

    if result['success']:
        count = result.get('sent_count', 0)
        if args.dry_run:
            print(f"\n✓ Dry run: would send {len(result.get('results', []))} email(s)", file=sys.stderr)
        else:
            print(f"\n✓ Sent {count} RFP email(s)", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"\n✗ Failed: {result.get('errors')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
