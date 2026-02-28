# ClickUp MCP Server

Model Context Protocol (MCP) server that exposes ClickUp API operations as AI-accessible tools.

## Overview

This MCP server provides native ClickUp integration for AI agents, allowing conversational control over your Rhizome workspace CRM. It implements the full task lifecycle and integrates with your existing workflow automation architecture.

## Features

### Core Operations
- **Workspace Management**: List workspaces, spaces, folders, and lists
- **Task CRUD**: Create, read, update tasks with full field support
- **Search**: Find tasks by name, status, assignee, custom fields
- **Comments**: Add comments and mentions to tasks
- **Custom Fields**: Read and set custom field values

### Available Tools

1. `clickup_get_workspaces` - List all workspaces/teams
2. `clickup_get_spaces` - Get spaces in a workspace
3. `clickup_get_lists` - Get lists from space or folder
4. `clickup_get_tasks` - Get tasks from a list
5. `clickup_search_tasks` - Search tasks across workspace
6. `clickup_create_task` - Create new task with all fields
7. `clickup_update_task` - Update existing task
8. `clickup_get_task` - Get detailed task info
9. `clickup_add_task_comment` - Add comment to task
10. `clickup_get_custom_fields` - Get available custom fields
11. `clickup_set_custom_field` - Set custom field value

## Installation

### 1. Install dependencies

```bash
cd execution/clickup_mcp
pip install -e .
```

### 2. Get ClickUp API Key

1. Go to your ClickUp workspace
2. Click your profile icon → Settings
3. Click "Apps" in the sidebar
4. Generate an API token
5. Copy the token

### 3. Configure environment

Add to your `.env` file:

```bash
CLICKUP_API_KEY=pk_your_api_key_here
CLICKUP_WORKSPACE_NAME=Rhizome
```

### 4. Configure Claude Desktop

Add to your Claude Desktop MCP settings file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "clickup": {
      "command": "python",
      "args": [
        "/Users/wayner/Downloads/DOE Workspace/execution/clickup_mcp/server.py"
      ],
      "env": {
        "CLICKUP_API_KEY": "pk_your_api_key_here",
        "CLICKUP_WORKSPACE_NAME": "Rhizome"
      }
    }
  }
}
```

**Important**: Update the path in `args` to match your actual workspace location.

### 5. Restart Claude Desktop

Restart Claude Desktop to load the MCP server.

## Usage Examples

Once configured, you can ask Claude to interact with ClickUp naturally:

```
"Show me all spaces in my Rhizome workspace"
"Create a task called 'Follow up with client' in the Sales list"
"Find all tasks assigned to John that are in progress"
"Update task #abc123 to mark it as complete"
"Add a comment to task #xyz789 saying 'Client approved the proposal'"
"What custom fields are available in the Leads list?"
```

## Architecture Integration

This MCP server integrates with your 3-layer architecture:

- **Layer 1 (Directives)**: See `directives/clickup_operations.md` for common workflows
- **Layer 2 (Orchestration)**: This MCP server + Claude routing decisions
- **Layer 3 (Execution)**: ClickUp API via deterministic HTTP requests

## Workflow Patterns

### Pattern 1: Ad-hoc CRM Operations
User asks → Claude calls MCP tools → immediate result

### Pattern 2: Automated Webhooks
External event → Modal webhook → Claude + MCP tools → ClickUp update
Example: New lead form → creates ClickUp task + updates status

### Pattern 3: Multi-system Workflows
User request → Claude orchestrates multiple tools:
- Read Google Sheet (via existing tools)
- Create ClickUp tasks (via MCP)
- Send notifications (via send_email)

## Troubleshooting

### Server not appearing in Claude Desktop
1. Check JSON syntax in config file
2. Verify file paths are absolute
3. Check Claude Desktop logs: Help → View Logs

### API authentication errors
1. Verify API key is correct in `.env`
2. Check API key has workspace access
3. Ensure workspace name matches exactly

### Tool call failures
- Check ClickUp API status: https://status.clickup.com/
- Verify IDs (workspace, space, list, task) are correct
- Use get/list tools first to discover IDs

## API Reference

ClickUp API docs: https://clickup.com/api

## Development

To modify the server:

1. Edit `server.py`
2. Test with: `python server.py`
3. Restart Claude Desktop to reload

## Self-Annealing

When ClickUp operations fail:
1. Check error message and API response
2. Fix the server.py code
3. Test the operation again
4. Update `directives/clickup_operations.md` with learnings
5. System is now stronger

This follows the self-annealing principle from your architecture.
