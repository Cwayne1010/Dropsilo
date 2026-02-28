#!/usr/bin/env python3
"""
Set up Google Sheets for Appraisal Order Workflow.
Creates the three required sheets: Orders, Appraiser Panel, and Quotes.

Usage:
    python setup_sheets.py

This will create one spreadsheet with three tabs and print the sheet ID
to add to your .env file.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from appraisal.sheets_utils import (
    get_sheets_service, create_appraisal_spreadsheet,
    ORDERS_COLUMNS, PANEL_COLUMNS, QUOTES_COLUMNS
)


def main():
    print("Setting up Appraisal Order Workflow Google Sheets...")
    print()

    service = get_sheets_service()

    # Create main tracking spreadsheet with all three sheets
    sheets_config = [
        {'name': 'Orders', 'columns': ORDERS_COLUMNS},
        {'name': 'Appraiser Panel', 'columns': PANEL_COLUMNS},
        {'name': 'Quotes', 'columns': QUOTES_COLUMNS},
    ]

    spreadsheet_id = create_appraisal_spreadsheet(
        service,
        "Appraisal Order Tracking",
        sheets_config
    )

    print("✓ Spreadsheet created!")
    print()
    print(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print()
    print("Add these to your .env file:")
    print()
    print(f"APPRAISAL_ORDERS_SHEET_ID={spreadsheet_id}")
    print(f"APPRAISAL_PANEL_SHEET_ID={spreadsheet_id}")
    print(f"APPRAISAL_QUOTES_SHEET_ID={spreadsheet_id}")
    print()
    print("(All three use the same spreadsheet ID since they're tabs in one sheet)")
    print()
    print("Next steps:")
    print("1. Add some test appraisers to the 'Appraiser Panel' tab")
    print("2. Run: python receive_order.py --test to create a test order")


if __name__ == "__main__":
    main()
