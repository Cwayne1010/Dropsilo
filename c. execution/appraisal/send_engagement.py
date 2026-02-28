#!/usr/bin/env python3
"""
Step 5: Send engagement letter to selected appraiser and decline notices to others.
Finalizes appraiser selection, updates order, and notifies all parties.

Usage:
    # Engage an appraiser
    python send_engagement.py --order-id ORD-2024-12345 --quote-id Q-20240115-ABCD

    # Auto-engage recommended appraiser
    python send_engagement.py --order-id ORD-2024-12345 --auto

Returns JSON with engagement results.
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
    ORDERS_SHEET_ID, QUOTES_SHEET_ID,
    read_sheet, find_row_by_id, update_row,
    ORDERS_COLUMNS, QUOTES_COLUMNS
)
from appraisal.collect_quotes import get_quotes_for_order, rank_quotes


def get_smtp_config() -> dict:
    """Get SMTP configuration."""
    return {
        'host': os.getenv('SMTP_HOST'),
        'port': int(os.getenv('SMTP_PORT', 587)),
        'user': os.getenv('SMTP_USER'),
        'password': os.getenv('SMTP_PASSWORD'),
        'from_name': os.getenv('SENDER_NAME', 'Appraisal Order Desk')
    }


def send_email(to_email: str, subject: str, body: str, smtp_config: dict) -> bool:
    """Send email via SMTP."""
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


def calculate_due_date(turnaround_days: int) -> str:
    """Calculate due date based on turnaround days (business days)."""
    due = datetime.now()
    days_added = 0

    while days_added < turnaround_days:
        due += timedelta(days=1)
        # Skip weekends
        if due.weekday() < 5:
            days_added += 1

    return due.strftime('%Y-%m-%d')


def get_engagement_email(order: dict, quote: dict, due_date: str) -> tuple[str, str]:
    """Generate engagement letter email content."""

    company = os.getenv('COMPANY_NAME', 'Appraisal Management')

    subject = f"Engagement Confirmation - Order #{order.get('order_id')} - {order.get('property_address', '')[:40]}"

    body = f"""Dear {quote.get('appraiser_name', 'Appraiser')},

Congratulations! You have been selected for the following appraisal assignment.

ENGAGEMENT DETAILS
═══════════════════════════════════════════════════════════════════════════

Order Number:      {order.get('order_id')}
Property Address:  {order.get('property_address')}
Property Type:     {order.get('property_type')}
Scope of Work:     {order.get('scope', 'Full Appraisal')}

AGREED TERMS
─────────────────────────────────
Fee:               ${float(quote.get('fee', 0)):,.2f}
Due Date:          {due_date}
Turnaround:        {quote.get('turnaround_days')} business days

LOAN INFORMATION
─────────────────────────────────
Loan Amount:       ${float(order.get('loan_amount', 0)):,.0f}
Loan Purpose:      {order.get('loan_purpose', 'N/A')}

CLIENT CONTACT
─────────────────────────────────
Name:              {order.get('contact_name', 'N/A')}
Email:             {order.get('contact_email', 'N/A')}

{f"SPECIAL INSTRUCTIONS{chr(10)}─────────────────────────────────{chr(10)}{order.get('special_instructions')}{chr(10)}" if order.get('special_instructions') else ""}
NEXT STEPS
─────────────────────────────────
1. Please REPLY to confirm acceptance of this assignment
2. Schedule property inspection
3. Submit completed report by {due_date}

DELIVERY REQUIREMENTS
─────────────────────────────────
• PDF format required
• XML/MISMO format if available
• Email completed report to this address

If you have any questions or need to discuss the assignment, please
contact us immediately.

Best regards,
{company} Order Desk
{os.getenv('COMPANY_EMAIL', '')}
"""

    return subject, body


def get_decline_email(order: dict, quote: dict) -> tuple[str, str]:
    """Generate decline notification email content."""

    company = os.getenv('COMPANY_NAME', 'Appraisal Management')

    subject = f"Quote Update - Order #{order.get('order_id')}"

    body = f"""Dear {quote.get('appraiser_name', 'Appraiser')},

Thank you for submitting your quote for the appraisal assignment:

Order #{order.get('order_id')}
Property: {order.get('property_address')}

We appreciate your prompt response. However, we have selected another
appraiser for this particular assignment.

We value our relationship with you and look forward to working together
on future opportunities.

Best regards,
{company} Order Desk
"""

    return subject, body


def engage_appraiser(
    order_id: str,
    quote_id: str = None,
    auto: bool = False,
    dry_run: bool = False
) -> dict:
    """
    Engage an appraiser for an order.

    Args:
        order_id: Order ID
        quote_id: Specific quote ID to accept
        auto: Auto-select recommended appraiser
        dry_run: Preview without sending

    Returns:
        Dict with results
    """

    # Get order
    order_result = find_row_by_id(ORDERS_SHEET_ID, 'Orders', 'order_id', order_id)
    if not order_result:
        return {
            'success': False,
            'errors': [f'Order not found: {order_id}']
        }

    order_row_index, order = order_result

    # Get quotes
    quotes = get_quotes_for_order(order_id)
    if not quotes:
        return {
            'success': False,
            'errors': ['No quotes found for this order']
        }

    # Find selected quote
    selected_quote = None

    if quote_id:
        for q in quotes:
            if q.get('quote_id') == quote_id:
                selected_quote = q
                break
        if not selected_quote:
            return {
                'success': False,
                'errors': [f'Quote not found: {quote_id}']
            }
    elif auto:
        ranked = rank_quotes(quotes)
        selected_quote = ranked[0]
    else:
        return {
            'success': False,
            'errors': ['Either --quote-id or --auto required']
        }

    # Calculate due date
    turnaround = int(selected_quote.get('turnaround_days', 14))
    due_date = calculate_due_date(turnaround)

    smtp_config = get_smtp_config()
    results = {'engagement': None, 'declines': []}

    # Send engagement letter
    eng_subject, eng_body = get_engagement_email(order, selected_quote, due_date)

    if dry_run:
        results['engagement'] = {
            'to': selected_quote.get('appraiser_email'),
            'subject': eng_subject,
            'status': 'dry_run'
        }
    else:
        try:
            send_email(
                selected_quote.get('appraiser_email'),
                eng_subject,
                eng_body,
                smtp_config
            )
            results['engagement'] = {
                'to': selected_quote.get('appraiser_email'),
                'appraiser_name': selected_quote.get('appraiser_name'),
                'status': 'sent'
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [f'Failed to send engagement email: {str(e)}']
            }

    # Send decline notices to others
    for q in quotes:
        if q.get('quote_id') == selected_quote.get('quote_id'):
            continue

        dec_subject, dec_body = get_decline_email(order, q)

        if dry_run:
            results['declines'].append({
                'to': q.get('appraiser_email'),
                'appraiser_name': q.get('appraiser_name'),
                'status': 'dry_run'
            })
        else:
            try:
                send_email(q.get('appraiser_email'), dec_subject, dec_body, smtp_config)
                results['declines'].append({
                    'to': q.get('appraiser_email'),
                    'appraiser_name': q.get('appraiser_name'),
                    'status': 'sent'
                })
            except Exception as e:
                results['declines'].append({
                    'to': q.get('appraiser_email'),
                    'appraiser_name': q.get('appraiser_name'),
                    'status': 'failed',
                    'error': str(e)
                })

    # Update order
    if not dry_run:
        order['status'] = 'engaged'
        order['engaged_appraiser_id'] = selected_quote.get('appraiser_id')
        order['engaged_appraiser_name'] = selected_quote.get('appraiser_name')
        order['engaged_fee'] = selected_quote.get('fee')
        order['due_date'] = due_date

        try:
            update_row(ORDERS_SHEET_ID, 'Orders', order_row_index, order, ORDERS_COLUMNS)
        except Exception as e:
            results['warning'] = f'Emails sent but failed to update order: {str(e)}'

        # Mark quote as selected
        all_quotes = read_sheet(QUOTES_SHEET_ID, 'Quotes!A:Z')
        for i, q in enumerate(all_quotes):
            if q.get('quote_id') == selected_quote.get('quote_id'):
                q['selected'] = 'TRUE'
                try:
                    update_row(QUOTES_SHEET_ID, 'Quotes', i + 2, q, QUOTES_COLUMNS)
                except:
                    pass
                break

    return {
        'success': True,
        'order_id': order_id,
        'engaged_appraiser': selected_quote.get('appraiser_name'),
        'fee': selected_quote.get('fee'),
        'due_date': due_date,
        'results': results,
        'dry_run': dry_run
    }


def main():
    parser = argparse.ArgumentParser(
        description="Send engagement letter and decline notices"
    )
    parser.add_argument("--order-id", required=True, help="Order ID")
    parser.add_argument("--quote-id", help="Quote ID to accept")
    parser.add_argument("--auto", action="store_true", help="Auto-select recommended")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")

    args = parser.parse_args()

    if not args.quote_id and not args.auto:
        print("Error: Either --quote-id or --auto required", file=sys.stderr)
        sys.exit(1)

    result = engage_appraiser(
        order_id=args.order_id,
        quote_id=args.quote_id,
        auto=args.auto,
        dry_run=args.dry_run
    )

    print(json.dumps(result, indent=2))

    if result.get('success'):
        if args.dry_run:
            print(f"\n✓ Dry run complete", file=sys.stderr)
        else:
            print(f"\n✓ Engaged {result.get('engaged_appraiser')} for ${float(result.get('fee', 0)):,.0f}", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"\n✗ Failed: {result.get('errors')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
