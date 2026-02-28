#!/usr/bin/env python3
"""
Step 4: Collect and rank appraiser quotes for an order.
Records incoming quotes and generates ranked summaries for client presentation.

Usage:
    # Record a new quote
    python collect_quotes.py --record --order-id ORD-2024-12345 --appraiser-id APP-001 --fee 3500 --turnaround 12

    # Get quote summary for an order
    python collect_quotes.py --summary --order-id ORD-2024-12345

    # Send summary to client
    python collect_quotes.py --send-summary --order-id ORD-2024-12345

Returns JSON with quote data or summary.
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
from datetime import datetime
import random
import string

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from appraisal.sheets_utils import (
    ORDERS_SHEET_ID, QUOTES_SHEET_ID, PANEL_SHEET_ID,
    read_sheet, find_row_by_id, append_row, update_row,
    ORDERS_COLUMNS, QUOTES_COLUMNS
)


def generate_quote_id() -> str:
    """Generate unique quote ID."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.ascii_uppercase, k=4))
    return f"Q-{timestamp}-{random_part}"


def get_appraiser(appraiser_id: str) -> dict | None:
    """Get appraiser details by ID."""
    appraisers = read_sheet(PANEL_SHEET_ID, 'Appraiser Panel!A:Z')
    for a in appraisers:
        if a.get('appraiser_id') == appraiser_id:
            return a
    return None


def record_quote(
    order_id: str,
    appraiser_id: str,
    fee: float,
    turnaround_days: int,
    notes: str = ''
) -> dict:
    """
    Record a new quote submission.

    Args:
        order_id: Order ID
        appraiser_id: Appraiser ID
        fee: Quoted fee
        turnaround_days: Quoted turnaround in business days
        notes: Optional notes from appraiser

    Returns:
        Dict with result
    """

    # Verify order exists
    order_result = find_row_by_id(ORDERS_SHEET_ID, 'Orders', 'order_id', order_id)
    if not order_result:
        return {
            'success': False,
            'errors': [f'Order not found: {order_id}']
        }

    # Get appraiser details
    appraiser = get_appraiser(appraiser_id)
    if not appraiser:
        return {
            'success': False,
            'errors': [f'Appraiser not found: {appraiser_id}']
        }

    # Check for duplicate quote
    existing_quotes = read_sheet(QUOTES_SHEET_ID, 'Quotes!A:Z')
    for q in existing_quotes:
        if q.get('order_id') == order_id and q.get('appraiser_id') == appraiser_id:
            return {
                'success': False,
                'errors': [f'Quote already exists from {appraiser.get("name")} for order {order_id}']
            }

    # Create quote record
    quote = {
        'quote_id': generate_quote_id(),
        'order_id': order_id,
        'appraiser_id': appraiser_id,
        'appraiser_name': appraiser.get('name', ''),
        'appraiser_email': appraiser.get('email', ''),
        'fee': str(fee),
        'turnaround_days': str(turnaround_days),
        'notes': notes,
        'submitted_at': datetime.now().isoformat(),
        'selected': ''
    }

    # Save to sheet
    try:
        append_row(QUOTES_SHEET_ID, 'Quotes', quote, QUOTES_COLUMNS)
    except Exception as e:
        return {
            'success': False,
            'errors': [f'Failed to save quote: {str(e)}']
        }

    # Update order status if needed
    row_index, order = order_result
    if order.get('status') == 'rfp_sent':
        order['status'] = 'quotes_received'
        try:
            update_row(ORDERS_SHEET_ID, 'Orders', row_index, order, ORDERS_COLUMNS)
        except Exception as e:
            pass  # Non-critical, continue

    return {
        'success': True,
        'quote_id': quote['quote_id'],
        'quote': quote
    }


def get_quotes_for_order(order_id: str) -> list[dict]:
    """Get all quotes for an order."""
    all_quotes = read_sheet(QUOTES_SHEET_ID, 'Quotes!A:Z')
    return [q for q in all_quotes if q.get('order_id') == order_id]


def rank_quotes(quotes: list[dict]) -> list[dict]:
    """
    Rank quotes by value.

    Scoring (lower is better):
    - Fee (normalized)
    - Turnaround time
    - Appraiser quality score (from panel)
    """

    # Get appraiser quality scores
    appraisers = read_sheet(PANEL_SHEET_ID, 'Appraiser Panel!A:Z')
    quality_map = {a.get('appraiser_id'): float(a.get('quality_score', 3) or 3) for a in appraisers}

    def score(q):
        fee = float(q.get('fee', 5000) or 5000)
        turnaround = int(q.get('turnaround_days', 14) or 14)
        quality = quality_map.get(q.get('appraiser_id'), 3)

        # Composite score (lower is better)
        fee_score = fee / 500  # Normalize
        turnaround_score = turnaround * 0.5
        quality_bonus = (5 - quality) * 3  # Higher quality = lower score

        return fee_score + turnaround_score + quality_bonus

    ranked = sorted(quotes, key=score)

    for i, q in enumerate(ranked):
        q['rank'] = i + 1
        q['recommended'] = (i == 0)
        q['quality_score'] = quality_map.get(q.get('appraiser_id'), 'N/A')

    return ranked


def get_quote_summary(order_id: str) -> dict:
    """
    Get ranked quote summary for an order.

    Returns:
        Dict with order details, ranked quotes, and recommendation
    """

    # Get order
    order_result = find_row_by_id(ORDERS_SHEET_ID, 'Orders', 'order_id', order_id)
    if not order_result:
        return {
            'success': False,
            'errors': [f'Order not found: {order_id}']
        }

    _, order = order_result

    # Get quotes
    quotes = get_quotes_for_order(order_id)
    if not quotes:
        return {
            'success': True,
            'order_id': order_id,
            'quotes': [],
            'quote_count': 0,
            'message': 'No quotes received yet'
        }

    # Rank quotes
    ranked = rank_quotes(quotes)

    return {
        'success': True,
        'order_id': order_id,
        'property_address': order.get('property_address'),
        'property_type': order.get('property_type'),
        'quotes': ranked,
        'quote_count': len(ranked),
        'recommended': ranked[0] if ranked else None
    }


def format_summary_email(summary: dict) -> tuple[str, str]:
    """Format quote summary as email content."""

    order_id = summary.get('order_id')
    address = summary.get('property_address', 'N/A')
    quotes = summary.get('quotes', [])

    subject = f"Appraisal Quotes Ready - Order #{order_id}"

    # Build quote table
    table_rows = []
    for q in quotes:
        rec = "★ RECOMMENDED" if q.get('recommended') else ""
        table_rows.append(
            f"  {q.get('appraiser_name', 'N/A'):<25} ${float(q.get('fee', 0)):>8,.0f}    {q.get('turnaround_days', 'N/A'):>3} days    {q.get('quality_score', 'N/A')}    {rec}"
        )

    table = "\n".join(table_rows)

    recommended = summary.get('recommended')
    rec_text = ""
    if recommended:
        rec_text = f"""
RECOMMENDATION
─────────────────────────────────
We recommend {recommended.get('appraiser_name')} based on their combination of
competitive fee (${float(recommended.get('fee', 0)):,.0f}), turnaround ({recommended.get('turnaround_days')} days),
and quality rating ({recommended.get('quality_score')}/5.0).
"""

    body = f"""Quote summary for Order #{order_id}

PROPERTY
─────────────────────────────────
{address}

QUOTES RECEIVED ({len(quotes)})
─────────────────────────────────
  {"Appraiser":<25} {"Fee":>10}    {"Time":>8}    Rating

{table}
{rec_text}
NEXT STEPS
─────────────────────────────────
Reply to this email with your selection, or we will proceed with the
recommended appraiser if no response is received within 24 hours.

Best regards,
{os.getenv('COMPANY_NAME', 'Appraisal Management')} Order Desk
"""

    return subject, body


def send_summary_to_client(order_id: str, dry_run: bool = False) -> dict:
    """Send quote summary email to client."""

    summary = get_quote_summary(order_id)
    if not summary.get('success'):
        return summary

    if not summary.get('quotes'):
        return {
            'success': False,
            'errors': ['No quotes to summarize']
        }

    # Get client email from order
    order_result = find_row_by_id(ORDERS_SHEET_ID, 'Orders', 'order_id', order_id)
    if not order_result:
        return {
            'success': False,
            'errors': [f'Order not found: {order_id}']
        }

    _, order = order_result
    client_email = order.get('contact_email')

    if not client_email:
        return {
            'success': False,
            'errors': ['No client email on order']
        }

    subject, body = format_summary_email(summary)

    if dry_run:
        return {
            'success': True,
            'dry_run': True,
            'to': client_email,
            'subject': subject,
            'body': body
        }

    # Send email
    smtp_config = {
        'host': os.getenv('SMTP_HOST'),
        'port': int(os.getenv('SMTP_PORT', 587)),
        'user': os.getenv('SMTP_USER'),
        'password': os.getenv('SMTP_PASSWORD'),
        'from_name': os.getenv('SENDER_NAME', 'Appraisal Order Desk')
    }

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{smtp_config['from_name']} <{smtp_config['user']}>"
        msg['To'] = client_email
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['user'], smtp_config['password'])
            server.send_message(msg)

    except Exception as e:
        return {
            'success': False,
            'errors': [f'Failed to send email: {str(e)}']
        }

    return {
        'success': True,
        'sent_to': client_email,
        'quote_count': len(summary.get('quotes', []))
    }


def main():
    parser = argparse.ArgumentParser(
        description="Collect and manage appraiser quotes"
    )
    parser.add_argument("--order-id", required=True, help="Order ID")

    # Actions
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--record", action="store_true", help="Record a new quote")
    action.add_argument("--summary", action="store_true", help="Get quote summary")
    action.add_argument("--send-summary", action="store_true", help="Send summary to client")

    # Record options
    parser.add_argument("--appraiser-id", help="Appraiser ID (for --record)")
    parser.add_argument("--fee", type=float, help="Quoted fee (for --record)")
    parser.add_argument("--turnaround", type=int, help="Turnaround days (for --record)")
    parser.add_argument("--notes", default="", help="Quote notes (for --record)")

    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")

    args = parser.parse_args()

    if args.record:
        if not all([args.appraiser_id, args.fee, args.turnaround]):
            print("Error: --record requires --appraiser-id, --fee, and --turnaround", file=sys.stderr)
            sys.exit(1)

        result = record_quote(
            order_id=args.order_id,
            appraiser_id=args.appraiser_id,
            fee=args.fee,
            turnaround_days=args.turnaround,
            notes=args.notes
        )

    elif args.summary:
        result = get_quote_summary(args.order_id)

    elif args.send_summary:
        result = send_summary_to_client(args.order_id, dry_run=args.dry_run)

    print(json.dumps(result, indent=2))

    if result.get('success'):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
