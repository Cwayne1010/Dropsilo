#!/usr/bin/env python3
"""
Dropsilo Tier 1 Flat File Ingestion Script
-------------------------------------------
Loads pipe-delimited CSV files into Snowflake RAW_TIER1 tables.

Usage:
    python ingest_flat_files.py                         # Load from .tmp/mock_data/
    python ingest_flat_files.py --data-dir /path/to/   # Load from custom directory
    python ingest_flat_files.py --truncate              # Clear tables before loading
    python ingest_flat_files.py --dry-run               # Validate CSVs without connecting

Supports files matching:
    dropsilo_customers_*.csv  → raw_customers
    dropsilo_loans_*.csv      → raw_loans
    dropsilo_deposits_*.csv   → raw_deposits

Requirements:
    pip install snowflake-connector-python[pandas] pandas python-dotenv
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

try:
    import pandas as pd
except ImportError:
    print("Error: pandas not installed. Run: pip install pandas")
    sys.exit(1)

# snowflake-connector-python is imported lazily in get_connection() so
# --dry-run works without the package installed.


# ── Paths ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_DATA_DIR = REPO_ROOT / ".tmp" / "mock_data"
DDL_FILE = Path(__file__).parent / "snowflake_ddl_v0.sql"

# File pattern → target table mapping
FILE_TABLE_MAP = {
    "customers": "RAW_CUSTOMERS",
    "loans":     "RAW_LOANS",
    "deposits":  "RAW_DEPOSITS",
}


# ── Validation ────────────────────────────────────────────────────────────────

# Expected columns per table (must match DDL, minus metadata cols)
EXPECTED_COLUMNS = {
    "RAW_CUSTOMERS": {
        "customer_id", "customer_type", "customer_since_date", "city", "state",
        "zip", "relationship_officer_id", "naics_code", "kyc_status",
        "aml_risk_rating", "customer_status", "is_related_party",
    },
    "RAW_LOANS": {
        "loan_id", "customer_id", "officer_id", "loan_type_code",
        "loan_purpose_code", "collateral_type_code", "original_balance",
        "current_outstanding_balance", "committed_amount", "collateral_value",
        "interest_rate", "rate_type", "rate_index", "rate_spread",
        "origination_date", "maturity_date", "next_payment_date",
        "payment_amount", "payment_frequency", "loan_status", "past_due_days",
        "past_due_amount", "accrual_status", "risk_rating",
        "regulatory_classification", "participation_sold_amount",
        "participation_purchased_amount", "guaranteed_amount", "guarantor_flag",
        "charge_off_date", "charge_off_amount", "recovery_amount_ytd",
    },
    "RAW_DEPOSITS": {
        "account_id", "customer_id", "account_type_code", "open_date",
        "current_balance", "average_daily_balance_30", "average_daily_balance_90",
        "interest_rate", "maturity_date", "officer_id", "account_status",
        "overdraft_limit",
    },
}


def resolve_table(filepath: Path) -> str | None:
    """Return the target Snowflake table name based on filename, or None if unrecognized."""
    name = filepath.stem.lower()  # e.g. dropsilo_customers_20260222
    for keyword, table in FILE_TABLE_MAP.items():
        if keyword in name:
            return table
    return None


def validate_csv(filepath: Path, table: str) -> tuple[pd.DataFrame, list[str]]:
    """
    Read and validate a CSV against the expected schema.
    Returns (dataframe, list_of_warnings).
    Raises on hard errors (missing required columns, empty file).
    """
    df = pd.read_csv(filepath, sep="|", dtype=str, keep_default_na=False)

    if df.empty:
        raise ValueError(f"{filepath.name} is empty.")

    actual_cols = set(df.columns.str.lower())
    expected = EXPECTED_COLUMNS[table]

    missing = expected - actual_cols
    if missing:
        raise ValueError(
            f"{filepath.name} is missing required columns: {sorted(missing)}"
        )

    extra = actual_cols - expected
    warnings = []
    if extra:
        warnings.append(f"Extra columns (will be ignored): {sorted(extra)}")

    # Normalise column names to uppercase to match Snowflake conventions
    df.columns = [c.upper() for c in df.columns]

    # Drop any extra columns not in DDL
    keep = {c.upper() for c in expected}
    df = df[[c for c in df.columns if c in keep]]

    return df, warnings


def add_metadata(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """Append _INGESTED_AT and _SOURCE_FILENAME metadata columns."""
    df = df.copy()
    df["_INGESTED_AT"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    df["_SOURCE_FILENAME"] = filename
    return df


def replace_empty_with_none(df: pd.DataFrame) -> pd.DataFrame:
    """Convert empty strings to None so Snowflake receives NULL."""
    return df.replace({"": None})


# ── Snowflake helpers ─────────────────────────────────────────────────────────

def get_connection():
    """Open a Snowflake connection using .env credentials."""
    try:
        import snowflake.connector  # noqa: F401 — imported for side-effect (registers connector)
    except ImportError:
        print("Error: snowflake-connector-python not installed. Run:")
        print("  pip install snowflake-connector-python[pandas]")
        sys.exit(1)

    required = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise EnvironmentError(
            f"Missing Snowflake env vars: {missing}\n"
            "Fill these in your .env file before running."
        )

    import snowflake.connector as sf

    authenticator = os.getenv("SNOWFLAKE_AUTHENTICATOR", "snowflake")
    connect_kwargs = dict(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        authenticator=authenticator,
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        # Warehouse/database/schema are set after DDL creates them
    )
    if authenticator == "snowflake":
        connect_kwargs["password"] = os.environ["SNOWFLAKE_PASSWORD"]

    return sf.connect(**connect_kwargs)


def ensure_schema(conn):
    """
    Create the database, schema, and tables if they don't already exist.
    Reads and executes the DDL file, splitting on statement boundaries.
    Skips the commented-out COPY block.
    """
    if not DDL_FILE.exists():
        print(f"  Warning: DDL file not found at {DDL_FILE}. Assuming schema exists.")
        return

    ddl_text = DDL_FILE.read_text()

    # Strip block comments (the example COPY commands are wrapped in /* ... */)
    import re
    ddl_text = re.sub(r"/\*.*?\*/", "", ddl_text, flags=re.DOTALL)

    # Split on semicolons, skip blanks
    statements = [s.strip() for s in ddl_text.split(";") if s.strip()]

    cur = conn.cursor()
    for stmt in statements:
        try:
            cur.execute(stmt)
        except Exception as e:
            # IF NOT EXISTS / CREATE OR REPLACE handle most cases;
            # surface anything unexpected
            if "already exists" not in str(e).lower():
                print(f"  DDL warning: {e}")
    cur.close()
    print("  Schema verified / created.")


def truncate_table(conn, table: str):
    cur = conn.cursor()
    cur.execute(f"TRUNCATE TABLE DROPSILO_DB.RAW_TIER1.{table}")
    cur.close()
    print(f"  Truncated {table}.")


def count_rows(conn, table: str) -> int:
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM DROPSILO_DB.RAW_TIER1.{table}")
    result = cur.fetchone()[0]
    cur.close()
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    load_dotenv(REPO_ROOT / ".env")

    parser = argparse.ArgumentParser(
        description="Load Dropsilo flat files into Snowflake RAW_TIER1."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Directory containing pipe-delimited CSVs (default: {DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate target tables before loading (clean test run).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate CSVs and print summary without connecting to Snowflake.",
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    if not data_dir.exists():
        print(f"Error: data directory not found: {data_dir}")
        sys.exit(1)

    # Discover CSV files
    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {data_dir}")
        sys.exit(1)

    print(f"\nDropsilo Flat File Ingestion")
    print(f"{'=' * 50}")
    print(f"Data dir : {data_dir}")
    print(f"Dry run  : {args.dry_run}")
    print(f"Truncate : {args.truncate}")
    print()

    # ── Validate all CSVs first ───────────────────────────────────────────────
    load_plan: list[tuple[Path, str, pd.DataFrame]] = []

    for filepath in csv_files:
        table = resolve_table(filepath)
        if table is None:
            print(f"  [SKIP] {filepath.name} — unrecognized filename pattern")
            continue

        print(f"  [READ] {filepath.name} → {table}")
        try:
            df, warnings = validate_csv(filepath, table)
            for w in warnings:
                print(f"         Warning: {w}")
            df = add_metadata(df, filepath.name)
            df = replace_empty_with_none(df)
            print(f"         {len(df):,} rows, {len(df.columns)} columns (incl. metadata)")
            load_plan.append((filepath, table, df))
        except (ValueError, Exception) as e:
            print(f"         ERROR: {e}")
            sys.exit(1)

    if not load_plan:
        print("\nNo files to load.")
        sys.exit(0)

    if args.dry_run:
        print("\nDry run complete. No data written to Snowflake.")
        return

    # ── Connect and load ──────────────────────────────────────────────────────
    print(f"\nConnecting to Snowflake...")
    try:
        conn = get_connection()
    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("  Connected.")
    print("\nSetting up schema...")
    ensure_schema(conn)

    results = []

    for filepath, table, df in load_plan:
        print(f"\nLoading {filepath.name} → {table}")

        if args.truncate:
            truncate_table(conn, table)

        rows_before = count_rows(conn, table)

        from snowflake.connector.pandas_tools import write_pandas
        success, _, _, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table,
            database="DROPSILO_DB",
            schema="RAW_TIER1",
            auto_create_table=False,
            overwrite=False,
            quote_identifiers=False,
        )

        rows_after = count_rows(conn, table)
        added = rows_after - rows_before

        status = "OK" if success else "FAILED"
        print(f"  [{status}] {added:,} rows added → {rows_after:,} total in {table}")
        results.append((table, filepath.name, added, status))

    conn.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 50}")
    print("Ingestion Summary")
    print(f"{'=' * 50}")
    print(f"{'Table':<20} {'File':<40} {'Rows':<8} {'Status'}")
    print(f"{'-' * 20} {'-' * 40} {'-' * 8} {'-' * 6}")
    for table, filename, rows, status in results:
        print(f"{table:<20} {filename:<40} {rows:<8,} {status}")

    failed = [r for r in results if r[3] != "OK"]
    if failed:
        print(f"\n{len(failed)} table(s) failed to load.")
        sys.exit(1)
    else:
        print(f"\nAll {len(results)} table(s) loaded successfully.")
        print("Next step: cd c. execution/dbt && dbt run --select staging")


if __name__ == "__main__":
    main()
