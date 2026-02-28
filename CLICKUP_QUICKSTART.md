# ClickUp MCP Server - Quick Start Guide

This guide will get you up and running with the ClickUp MCP wrapper in under 5 minutes.

## What You're Building

An AI-powered wrapper around ClickUp that lets you:
- Ask me to do anything in ClickUp using natural language
- Automate CRM workflows across multiple systems
- Connect ClickUp to your other agency tools (Google Sheets, email, webhooks)

## Step 1: Get Your ClickUp API Key

1. Open ClickUp and log in to your **Rhizome** workspace
2. Click your profile picture → **Settings**
3. In the sidebar, click **Apps**
4. Scroll to **API Token** section
5. Click **Generate** (or **Regenerate** if you already have one)
6. Copy the token (starts with `pk_`)

## Step 2: Configure Environment

Add your API key to `.env`:

```bash
# Open .env in your editor
nano .env

# Add these lines:
CLICKUP_API_KEY=pk_YOUR_KEY_HERE
CLICKUP_WORKSPACE_NAME=Rhizome
```

Save and close the file.

## Step 3: Install MCP Server

```bash
cd execution/clickup_mcp
./setup.sh
```

This installs all dependencies and validates your setup.

## Step 4: Configure Claude Desktop

### macOS
```bash
# Open config file
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Add ClickUp MCP Server

Add this to the `mcpServers` section:

```json
{
  "mcpServers": {
    "clickup": {
      "command": "python",
      "args": [
        "/Users/wayner/Downloads/DOE Workspace/execution/clickup_mcp/server.py"
      ],
      "env": {
        "CLICKUP_API_KEY": "pk_YOUR_ACTUAL_KEY_HERE",
        "CLICKUP_WORKSPACE_NAME": "Rhizome"
      }
    }
  }
}
```

**Important**:
- Replace the path in `args` with your actual workspace path
- Replace `pk_YOUR_ACTUAL_KEY_HERE` with your real API key
- If you have other MCP servers, add this as a new entry (don't replace them)

## Step 5: Restart Claude Desktop

Completely quit and restart Claude Desktop to load the MCP server.

## Step 6: Test It!

Open a new conversation in Claude Desktop and try:

```
"Show me all the spaces in my Rhizome workspace"
```

If you see a list of your ClickUp spaces, **it's working!** 🎉

## Common First Commands

Try these to explore your ClickUp setup:

```
"List all spaces in Rhizome"
"Show me the lists in the [Space Name] space"
"What tasks are in the [List Name] list?"
"Create a task called 'Test task' in [List Name]"
"Search for all tasks assigned to me"
```

## Troubleshooting

### MCP server not showing up in Claude

1. Check your `claude_desktop_config.json` syntax (use a JSON validator)
2. Verify the path in `args` is absolute and correct
3. Check Claude Desktop logs: **Help → View Logs**

### "Authentication failed" errors

1. Verify your API key is correct in the config
2. Make sure the key starts with `pk_`
3. Check that the key has access to your Rhizome workspace
4. Try regenerating the API key in ClickUp settings

### "Workspace not found" errors

1. Confirm `CLICKUP_WORKSPACE_NAME` is exactly "Rhizome"
2. Check that your API key has access to that workspace
3. List all workspaces: "Show me all my ClickUp workspaces"

### Server crashes or errors

1. Check Python version: `python --version` (need 3.10+)
2. Reinstall dependencies: `cd execution/clickup_mcp && pip install -e .`
3. Check logs in Claude Desktop

## Next Steps

### Learn Common Workflows

Read [directives/clickup_operations.md](directives/clickup_operations.md) for:
- Creating and updating tasks
- Searching and filtering
- Setting custom fields
- Multi-system workflows (ClickUp + Sheets + Email)

### Build Automation

Combine ClickUp MCP with your existing tools:
- Import leads from Google Sheets → ClickUp tasks
- New task webhooks → Email notifications
- Deal progression → Automated follow-ups

### Explore Advanced Features

```
"Show me the custom fields in the [List Name] list"
"Set the Deal Value field to $50,000 for task #abc123"
"Add a comment to task #xyz789 with 'Client approved'"
"Create 10 tasks from the leads in my Google Sheet"
```

## Architecture

You're now running a 3-layer system:

1. **Directives** (`directives/clickup_operations.md`) - What to do
2. **Orchestration** (You + Claude) - Decision making
3. **Execution** (MCP Server) - ClickUp API calls

When something breaks, the system self-anneals:
- I'll fix the error
- Update the MCP server code
- Document the learning in directives
- System gets stronger

## Getting Help

- Full docs: [execution/clickup_mcp/README.md](execution/clickup_mcp/README.md)
- ClickUp API: https://clickup.com/api
- Report issues: Just tell me what went wrong!

## Examples of What's Now Possible

**Simple**:
- "Create a task for Sarah to call Acme Corp tomorrow"
- "Mark all my overdue tasks as high priority"
- "Show me deals in the 'Proposal Sent' stage"

**Complex**:
- "Import all leads from the Google Sheet and create ClickUp tasks with the company name, contact, and deal value as custom fields"
- "Find all tasks tagged 'hot-lead' that haven't been updated in 3 days and send me a summary"
- "When I receive an email at leads@company.com, create a ClickUp task and notify the sales team in Slack"

All of this is now just a conversation away!
