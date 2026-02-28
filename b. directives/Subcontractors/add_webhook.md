# Add Webhook Directive

## Goal
Create a new webhook endpoint that executes a specific directive with scoped tool access.

## When to Use
When you need to add event-driven automation that can be triggered via HTTP requests.

## Process

### 1. Create the Directive
Create a new markdown file in `directives/` that defines:
- **Goal**: What this webhook accomplishes
- **Inputs**: What parameters it expects
- **Process**: Step-by-step instructions
- **Tools**: Which execution scripts to use
- **Outputs**: What it returns/creates
- **Edge Cases**: Error handling and constraints

### 2. Register the Webhook
Add an entry to `execution/webhooks.json`:

```json
{
  "webhooks": {
    "your-slug": {
      "directive": "directives/your_directive.md",
      "description": "Brief description of what this does",
      "allowed_tools": ["send_email", "read_sheet", "update_sheet"]
    }
  }
}
```

**Available tools:**
- `send_email` - Send emails via configured SMTP
- `read_sheet` - Read data from Google Sheets
- `update_sheet` - Write data to Google Sheets

### 3. Deploy to Modal
```bash
modal deploy execution/modal_webhook.py
```

### 4. Test the Endpoint
```bash
curl -X POST "https://nick-90891--claude-orchestrator-directive.modal.run?slug=your-slug" \
  -H "Content-Type: application/json" \
  -d '{"param1": "value1"}'
```

## Important Notes

- Each webhook maps to exactly ONE directive
- Webhooks have scoped tool access (only the tools specified)
- All webhook activity streams to Slack in real-time
- Endpoints are serverless and scale automatically
- Use kebab-case for slug names (e.g., `send-daily-report`)

## Common Use Cases

1. **Scheduled Reports**: Daily/weekly data exports to Google Sheets
2. **Email Notifications**: Alert on specific events
3. **Data Ingestion**: Process incoming data and store in Sheets
4. **Integration Triggers**: Connect external services to your workflow

## Edge Cases

- **Invalid slug**: Returns 404 with available webhooks
- **Missing directive**: Returns error with path attempted
- **Tool not allowed**: Execution fails with permission error
- **Timeout**: Modal functions timeout after 10 minutes
