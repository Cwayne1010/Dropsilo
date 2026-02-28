"""
Appraisal Order Workflow - Execution Scripts

This package contains deterministic Python scripts for the appraisal
order management workflow.

Scripts:
- setup_sheets.py: Create Google Sheets for tracking
- receive_order.py: Step 1 - Validate and log incoming orders
- find_appraisers.py: Step 2 - Query panel and rank candidates
- send_rfp.py: Step 3 - Send RFP emails to appraisers
- collect_quotes.py: Step 4 - Record and rank quotes
- send_engagement.py: Step 5 - Engage winner, decline others
"""
