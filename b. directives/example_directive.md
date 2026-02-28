# Example Directive

## Goal
Demonstrate the structure of a directive and how to write clear instructions for the orchestration layer.

## Inputs
- `user_name` (string): The name of the user
- `email` (string, optional): User's email address

## Process

1. **Validate inputs**
   - Check that `user_name` is provided
   - If `email` provided, validate format

2. **Execute main task**
   - Use `execution/example_script.py` if it exists
   - Pass parameters: `--name "{user_name}" --email "{email}"`
   - Otherwise, perform task manually

3. **Handle results**
   - Log success/failure
   - If email provided, send confirmation via `send_email` tool

4. **Update tracking**
   - Record execution in Google Sheet (if configured)
   - Use `update_sheet` tool with sheet_id and data

## Tools
- `execution/example_script.py` - Main processing script
- `send_email` - Send confirmation emails
- `update_sheet` - Update tracking spreadsheet

## Outputs
- Success confirmation message
- Email sent to user (if email provided)
- Updated tracking sheet with execution details

## Edge Cases

### Missing user_name
- Return error: "user_name is required"
- Do not proceed

### Invalid email format
- Log warning but continue
- Skip email sending step

### Script execution fails
- Retry once
- If still fails, log error and notify via Slack
- Do not update tracking sheet on failure

### API Rate Limits
- Google Sheets: Max 100 requests per 100 seconds
- If hit, wait 60 seconds and retry
- Update this directive if better batch approach discovered

## Learning Notes
(This section gets updated as the system learns)

- 2024-01-15: Discovered that email validation regex was too strict, updated to allow + signs
- 2024-01-16: Sheet updates work better in batches, updated script to batch writes
