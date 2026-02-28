#!/usr/bin/env python3
"""
Step 2: Find and rank qualified appraisers for an order.
Queries the appraiser panel, filters by qualifications, and ranks candidates.

Usage:
    python find_appraisers.py --order-id ORD-2024-12345
    python find_appraisers.py --property-state IL --property-type Office

Returns JSON with ranked appraiser candidates.
"""
from __future__ import annotations

import argparse
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from appraisal.sheets_utils import (
    PANEL_SHEET_ID, ORDERS_SHEET_ID,
    read_sheet, find_row_by_id, get_client_panel_sheet_id
)


def get_appraisers(client_id: str = None) -> tuple[list[dict], str]:
    """
    Load appraisers from appropriate panel.

    Args:
        client_id: Optional client ID to check for client-specific panel

    Returns:
        Tuple of (appraisers list, panel_source description)
    """
    # Check for client-specific panel first
    if client_id:
        client_panel_id = get_client_panel_sheet_id(client_id)
        if client_panel_id:
            try:
                appraisers = read_sheet(client_panel_id, 'Appraiser Panel!A:Z')
                if appraisers:
                    return appraisers, f"client:{client_id}"
            except Exception:
                pass  # Fall back to master panel

    # Use master panel
    if not PANEL_SHEET_ID:
        raise ValueError("APPRAISAL_PANEL_SHEET_ID not configured in .env")

    return read_sheet(PANEL_SHEET_ID, 'Appraiser Panel!A:Z'), "master"


def get_order(order_id: str) -> dict | None:
    """Load order by ID."""
    if not ORDERS_SHEET_ID:
        raise ValueError("APPRAISAL_ORDERS_SHEET_ID not configured in .env")

    result = find_row_by_id(ORDERS_SHEET_ID, 'Orders', 'order_id', order_id)
    return result[1] if result else None


def filter_appraisers(
    appraisers: list[dict],
    property_state: str,
    property_type: str,
    excluded_ids: list[str] = None
) -> list[dict]:
    """
    Filter appraisers by qualifications.

    Criteria:
    - Active status
    - Licensed in property state
    - Handles property type
    - Under capacity threshold
    - Quality score >= 4.0
    - Not in exclusion list
    """
    excluded_ids = excluded_ids or []
    qualified = []

    for a in appraisers:
        # Skip inactive
        if a.get('active', '').upper() != 'TRUE':
            continue

        # Skip excluded
        if a.get('appraiser_id') in excluded_ids:
            continue

        # Check state coverage (comma-separated list)
        states = [s.strip().upper() for s in a.get('states', '').split(',')]
        if property_state.upper() not in states:
            continue

        # Check property type coverage
        types = [t.strip() for t in a.get('property_types', '').split(',')]
        if property_type not in types:
            continue

        # Check capacity
        try:
            workload = int(a.get('current_workload', 0) or 0)
            capacity = int(a.get('capacity', 5) or 5)
            if workload >= capacity:
                continue
        except ValueError:
            pass  # Skip capacity check if not numeric

        # Check quality score
        try:
            quality = float(a.get('quality_score', 0) or 0)
            if quality < 4.0:
                continue
        except ValueError:
            pass  # Skip quality check if not numeric

        qualified.append(a)

    return qualified


def rank_appraisers(appraisers: list[dict]) -> list[dict]:
    """
    Rank appraisers by desirability.

    Scoring factors (lower is better):
    - Quality score (inverted - higher quality = lower score)
    - Turnaround time
    - Current workload ratio
    - Average fee (normalized)
    """

    def score(a):
        quality = float(a.get('quality_score', 3) or 3)
        turnaround = float(a.get('avg_turnaround_days', 14) or 14)
        workload = int(a.get('current_workload', 0) or 0)
        capacity = int(a.get('capacity', 5) or 5)
        fee = float(a.get('avg_fee', 3000) or 3000)

        # Composite score (lower is better)
        quality_score = (5 - quality) * 10  # Quality inverted, weighted heavily
        turnaround_score = turnaround * 0.5
        workload_score = (workload / capacity) * 5 if capacity > 0 else 0
        fee_score = fee / 1000  # Normalize fee

        return quality_score + turnaround_score + workload_score + fee_score

    ranked = sorted(appraisers, key=score)

    # Add rank to each
    for i, a in enumerate(ranked):
        a['rank'] = i + 1

    return ranked


def find_appraisers_for_order(
    order_id: str = None,
    property_state: str = None,
    property_type: str = None,
    client_id: str = None,
    excluded_ids: list[str] = None,
    limit: int = 5
) -> dict:
    """
    Main function to find appraisers for an order.

    Args:
        order_id: Order ID to look up (gets state/type/client from order)
        property_state: Property state code (e.g., "IL")
        property_type: Property type (e.g., "Office")
        client_id: Client ID to check for client-specific panel
        excluded_ids: Appraiser IDs to exclude
        limit: Max number of candidates to return

    Returns:
        Dict with candidates list and metadata
    """

    # Get order details if order_id provided
    if order_id:
        order = get_order(order_id)
        if not order:
            return {
                'success': False,
                'errors': [f'Order not found: {order_id}']
            }
        property_state = property_state or order.get('property_state')
        property_type = property_type or order.get('property_type')
        client_id = client_id or order.get('client_id')

    if not property_state or not property_type:
        return {
            'success': False,
            'errors': ['property_state and property_type are required']
        }

    # Load appraisers (checks for client-specific panel first)
    try:
        appraisers, panel_source = get_appraisers(client_id)
    except Exception as e:
        return {
            'success': False,
            'errors': [f'Failed to load appraiser panel: {str(e)}']
        }

    if not appraisers:
        return {
            'success': False,
            'errors': ['No appraisers found in panel'],
            'panel_source': panel_source
        }

    # Filter
    qualified = filter_appraisers(
        appraisers,
        property_state,
        property_type,
        excluded_ids
    )

    if not qualified:
        return {
            'success': True,
            'candidates': [],
            'total_in_panel': len(appraisers),
            'qualified_count': 0,
            'panel_source': panel_source,
            'message': f'No qualified appraisers found for {property_type} in {property_state}'
        }

    # Rank
    ranked = rank_appraisers(qualified)

    # Limit
    candidates = ranked[:limit]

    return {
        'success': True,
        'candidates': candidates,
        'total_in_panel': len(appraisers),
        'qualified_count': len(qualified),
        'returned_count': len(candidates),
        'panel_source': panel_source,
        'criteria': {
            'property_state': property_state,
            'property_type': property_type,
            'client_id': client_id,
            'excluded_ids': excluded_ids or []
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Find and rank qualified appraisers for an order"
    )
    parser.add_argument(
        "--order-id",
        help="Order ID to find appraisers for"
    )
    parser.add_argument(
        "--property-state",
        help="Property state code (e.g., IL)"
    )
    parser.add_argument(
        "--property-type",
        help="Property type (e.g., Office, Retail)"
    )
    parser.add_argument(
        "--client-id",
        help="Client ID (checks for client-specific panel)"
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        help="Appraiser IDs to exclude"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Max candidates to return (default: 5)"
    )

    args = parser.parse_args()

    result = find_appraisers_for_order(
        order_id=args.order_id,
        property_state=args.property_state,
        property_type=args.property_type,
        client_id=args.client_id,
        excluded_ids=args.exclude,
        limit=args.limit
    )

    print(json.dumps(result, indent=2))

    if result['success']:
        count = result.get('returned_count', 0)
        print(f"\n✓ Found {count} qualified appraiser(s)", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"\n✗ Failed: {result['errors']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
