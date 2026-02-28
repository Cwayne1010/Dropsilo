#!/usr/bin/env python3
"""
Google Sheets utilities for Appraisal Order Workflow.
Provides shared functions for reading/writing to the appraisal tracking sheets.
"""
from __future__ import annotations

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Error: Google API packages not installed. Run:")
    print("  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()

# OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
]

# Path to credentials (in execution/ directory)
EXECUTION_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = EXECUTION_DIR / 'credentials.json'
TOKEN_FILE = EXECUTION_DIR / 'token.json'

# Sheet IDs from environment
ORDERS_SHEET_ID = os.getenv('APPRAISAL_ORDERS_SHEET_ID')
PANEL_SHEET_ID = os.getenv('APPRAISAL_PANEL_SHEET_ID')
QUOTES_SHEET_ID = os.getenv('APPRAISAL_QUOTES_SHEET_ID')

# Client panels registry - maps client_id to their panel spreadsheet ID
# Format: CLIENT_PANEL_<client_id>=<spreadsheet_id>
def get_client_panel_sheet_id(client_id: str) -> str | None:
    """Get client-specific panel sheet ID if one exists."""
    if not client_id:
        return None
    # Check for CLIENT_PANEL_BANKONE, CLIENT_PANEL_ACME, etc.
    env_key = f"CLIENT_PANEL_{client_id.upper().replace('-', '_')}"
    return os.getenv(env_key)


def get_google_credentials():
    """
    Get or refresh Google OAuth credentials.

    Supports two modes:
    1. Local: Uses token.json and credentials.json files
    2. Modal/Cloud: Uses environment variables (GOOGLE_REFRESH_TOKEN, etc.)
    """
    creds = None

    # Check for environment-based credentials (Modal/cloud)
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if refresh_token and client_id and client_secret:
        # Build credentials from environment variables
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES
        )
        # Refresh to get a valid access token
        creds.refresh(Request())
        return creds

    # Fall back to file-based credentials (local development)
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}. "
                    "Set up Google OAuth credentials first."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_sheets_service():
    """Get Google Sheets API service."""
    creds = get_google_credentials()
    return build('sheets', 'v4', credentials=creds)


def read_sheet(spreadsheet_id: str, range_name: str) -> list[dict]:
    """
    Read data from a Google Sheet and return as list of dicts.
    First row is treated as headers.
    """
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])
    if not values or len(values) < 2:
        return []

    headers = values[0]
    rows = []
    for row in values[1:]:
        # Pad row to match headers length
        row = row + [''] * (len(headers) - len(row))
        rows.append(dict(zip(headers, row)))

    return rows


def append_row(spreadsheet_id: str, sheet_name: str, row_data: dict, columns: list[str]):
    """Append a single row to a sheet."""
    service = get_sheets_service()

    row = [row_data.get(col, '') for col in columns]

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:Z",
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={'values': [row]}
    ).execute()


def update_row(spreadsheet_id: str, sheet_name: str, row_index: int, row_data: dict, columns: list[str]):
    """Update a specific row (1-indexed, row 1 is headers)."""
    service = get_sheets_service()

    row = [row_data.get(col, '') for col in columns]

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A{row_index}:Z{row_index}",
        valueInputOption='USER_ENTERED',
        body={'values': [row]}
    ).execute()


def find_row_by_id(spreadsheet_id: str, sheet_name: str, id_column: str, id_value: str) -> tuple[int, dict] | None:
    """Find a row by ID column value. Returns (row_index, row_data) or None."""
    rows = read_sheet(spreadsheet_id, f"{sheet_name}!A:Z")

    for i, row in enumerate(rows):
        if row.get(id_column) == id_value:
            return (i + 2, row)  # +2 because 1-indexed and header row

    return None


def create_appraisal_spreadsheet(service, title: str, sheets_config: list[dict]) -> str:
    """
    Create a new spreadsheet with multiple sheets.

    Args:
        service: Google Sheets API service
        title: Spreadsheet title
        sheets_config: List of dicts with 'name' and 'columns' keys

    Returns:
        Spreadsheet ID
    """
    sheets = []
    for i, config in enumerate(sheets_config):
        sheets.append({
            'properties': {
                'sheetId': i,
                'title': config['name'],
                'gridProperties': {'frozenRowCount': 1}
            }
        })

    spreadsheet = {
        'properties': {'title': title},
        'sheets': sheets
    }

    result = service.spreadsheets().create(body=spreadsheet).execute()
    spreadsheet_id = result['spreadsheetId']

    # Add headers to each sheet
    for i, config in enumerate(sheets_config):
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{config['name']}!A1",
            valueInputOption='USER_ENTERED',
            body={'values': [config['columns']]}
        ).execute()

        # Format header row
        format_header(service, spreadsheet_id, i, len(config['columns']))

    return spreadsheet_id


def format_header(service, spreadsheet_id: str, sheet_id: int, num_columns: int):
    """Apply formatting to header row."""
    requests = [
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.3, 'blue': 0.5},
                        'textFormat': {
                            'bold': True,
                            'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                        },
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)',
            }
        },
        {
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': num_columns,
                }
            }
        }
    ]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()


# Column definitions for each sheet type
ORDERS_COLUMNS = [
    'order_id', 'status', 'property_address', 'property_city', 'property_state',
    'property_type', 'loan_amount', 'loan_purpose', 'scope', 'urgency',
    'client_id', 'contact_name', 'contact_email', 'special_instructions',
    'created_at', 'rfp_sent_at', 'quotes_deadline', 'engaged_appraiser_id',
    'engaged_appraiser_name', 'engaged_fee', 'due_date', 'delivered_at'
]

PANEL_COLUMNS = [
    'appraiser_id', 'name', 'email', 'phone', 'company',
    'states', 'property_types', 'certifications',
    'current_workload', 'capacity', 'avg_fee', 'avg_turnaround_days',
    'quality_score', 'active'
]

QUOTES_COLUMNS = [
    'quote_id', 'order_id', 'appraiser_id', 'appraiser_name', 'appraiser_email',
    'fee', 'turnaround_days', 'notes', 'submitted_at', 'selected'
]
