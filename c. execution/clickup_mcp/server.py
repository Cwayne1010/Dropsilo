#!/usr/bin/env python3
"""
ClickUp MCP Server
Exposes ClickUp API operations as MCP tools for AI agents.
Focused on the Rhizome workspace.
"""

import os
import json
import asyncio
from typing import Any, Optional
import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio

# Load environment variables
load_dotenv()

# ClickUp API Configuration
CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")
CLICKUP_WORKSPACE_NAME = os.getenv("CLICKUP_WORKSPACE_NAME", "Rhizome")
CLICKUP_API_BASE = "https://api.clickup.com/api/v2"

# Initialize MCP server
app = Server("clickup-mcp")

# Global HTTP client
http_client: Optional[httpx.AsyncClient] = None


def get_headers() -> dict:
    """Get ClickUp API headers"""
    if not CLICKUP_API_KEY:
        raise ValueError("CLICKUP_API_KEY not found in environment variables")
    return {
        "Authorization": CLICKUP_API_KEY,
        "Content-Type": "application/json"
    }


async def clickup_request(method: str, endpoint: str, **kwargs) -> dict:
    """Make authenticated request to ClickUp API"""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=30.0)

    url = f"{CLICKUP_API_BASE}/{endpoint.lstrip('/')}"
    headers = get_headers()

    response = await http_client.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response.json()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available ClickUp tools"""
    return [
        Tool(
            name="clickup_get_workspaces",
            description="Get all ClickUp workspaces/teams. Use this to find workspace IDs.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="clickup_get_spaces",
            description="Get all spaces in a workspace. Spaces are top-level containers in ClickUp.",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Workspace/team ID. Get this from clickup_get_workspaces first."
                    }
                },
                "required": ["team_id"]
            }
        ),
        Tool(
            name="clickup_get_lists",
            description="Get all lists in a space or folder. Lists contain tasks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "Space ID to get lists from"
                    },
                    "folder_id": {
                        "type": "string",
                        "description": "Optional folder ID to get lists from (instead of space_id)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="clickup_get_tasks",
            description="Get tasks from a list. Returns task details including status, assignees, due dates, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "string",
                        "description": "List ID to get tasks from"
                    },
                    "include_closed": {
                        "type": "boolean",
                        "description": "Include closed/completed tasks",
                        "default": False
                    }
                },
                "required": ["list_id"]
            }
        ),
        Tool(
            name="clickup_search_tasks",
            description="Search for tasks across the workspace by name, status, assignee, or custom fields.",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Workspace/team ID to search in"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (task name)"
                    },
                    "space_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: Filter by space IDs"
                    },
                    "list_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: Filter by list IDs"
                    },
                    "assignees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: Filter by assignee user IDs"
                    },
                    "statuses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: Filter by status names"
                    }
                },
                "required": ["team_id"]
            }
        ),
        Tool(
            name="clickup_create_task",
            description="Create a new task in ClickUp. Can set name, description, status, assignees, due date, priority, and custom fields.",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "string",
                        "description": "List ID where task will be created"
                    },
                    "name": {
                        "type": "string",
                        "description": "Task name/title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (supports markdown)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Task status (e.g., 'to do', 'in progress', 'done')"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Priority: 1=Urgent, 2=High, 3=Normal, 4=Low"
                    },
                    "due_date": {
                        "type": "integer",
                        "description": "Due date as Unix timestamp in milliseconds"
                    },
                    "assignees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of user IDs to assign"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of tag names"
                    }
                },
                "required": ["list_id", "name"]
            }
        ),
        Tool(
            name="clickup_update_task",
            description="Update an existing task. Can modify name, description, status, assignees, due date, priority, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New task name"
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description"
                    },
                    "status": {
                        "type": "string",
                        "description": "New task status"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Priority: 1=Urgent, 2=High, 3=Normal, 4=Low"
                    },
                    "due_date": {
                        "type": "integer",
                        "description": "Due date as Unix timestamp in milliseconds"
                    },
                    "assignees_add": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "User IDs to add as assignees"
                    },
                    "assignees_remove": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "User IDs to remove from assignees"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="clickup_get_task",
            description="Get detailed information about a specific task by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to retrieve"
                    },
                    "include_subtasks": {
                        "type": "boolean",
                        "description": "Include subtasks in response",
                        "default": False
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="clickup_add_task_comment",
            description="Add a comment to a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to comment on"
                    },
                    "comment_text": {
                        "type": "string",
                        "description": "Comment text (supports markdown)"
                    },
                    "assignee": {
                        "type": "string",
                        "description": "Optional user ID to assign the comment to"
                    }
                },
                "required": ["task_id", "comment_text"]
            }
        ),
        Tool(
            name="clickup_get_custom_fields",
            description="Get custom fields for a list. Useful for understanding what fields are available.",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "string",
                        "description": "List ID to get custom fields from"
                    }
                },
                "required": ["list_id"]
            }
        ),
        Tool(
            name="clickup_set_custom_field",
            description="Set a custom field value on a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID"
                    },
                    "field_id": {
                        "type": "string",
                        "description": "Custom field ID (get from clickup_get_custom_fields)"
                    },
                    "value": {
                        "description": "Field value (type depends on field type)"
                    }
                },
                "required": ["task_id", "field_id", "value"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute ClickUp tool operations"""

    try:
        if name == "clickup_get_workspaces":
            data = await clickup_request("GET", "/team")
            workspaces = data.get("teams", [])
            return [TextContent(
                type="text",
                text=json.dumps({
                    "workspaces": workspaces,
                    "count": len(workspaces)
                }, indent=2)
            )]

        elif name == "clickup_get_spaces":
            team_id = arguments["team_id"]
            data = await clickup_request("GET", f"/team/{team_id}/space")
            spaces = data.get("spaces", [])
            return [TextContent(
                type="text",
                text=json.dumps({
                    "spaces": spaces,
                    "count": len(spaces)
                }, indent=2)
            )]

        elif name == "clickup_get_lists":
            if "space_id" in arguments:
                space_id = arguments["space_id"]
                data = await clickup_request("GET", f"/space/{space_id}/list")
            elif "folder_id" in arguments:
                folder_id = arguments["folder_id"]
                data = await clickup_request("GET", f"/folder/{folder_id}/list")
            else:
                raise ValueError("Either space_id or folder_id is required")

            lists = data.get("lists", [])
            return [TextContent(
                type="text",
                text=json.dumps({
                    "lists": lists,
                    "count": len(lists)
                }, indent=2)
            )]

        elif name == "clickup_get_tasks":
            list_id = arguments["list_id"]
            include_closed = arguments.get("include_closed", False)

            params = {"archived": "false"}
            if not include_closed:
                params["include_closed"] = "false"

            data = await clickup_request("GET", f"/list/{list_id}/task", params=params)
            tasks = data.get("tasks", [])
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tasks": tasks,
                    "count": len(tasks)
                }, indent=2)
            )]

        elif name == "clickup_search_tasks":
            team_id = arguments["team_id"]
            params = {}

            if "query" in arguments:
                params["query"] = arguments["query"]
            if "space_ids" in arguments:
                params["space_ids[]"] = arguments["space_ids"]
            if "list_ids" in arguments:
                params["list_ids[]"] = arguments["list_ids"]
            if "assignees" in arguments:
                params["assignees[]"] = arguments["assignees"]
            if "statuses" in arguments:
                params["statuses[]"] = arguments["statuses"]

            data = await clickup_request("GET", f"/team/{team_id}/task", params=params)
            tasks = data.get("tasks", [])
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tasks": tasks,
                    "count": len(tasks)
                }, indent=2)
            )]

        elif name == "clickup_create_task":
            list_id = arguments["list_id"]
            task_data = {"name": arguments["name"]}

            # Add optional fields
            if "description" in arguments:
                task_data["description"] = arguments["description"]
            if "status" in arguments:
                task_data["status"] = arguments["status"]
            if "priority" in arguments:
                task_data["priority"] = arguments["priority"]
            if "due_date" in arguments:
                task_data["due_date"] = arguments["due_date"]
            if "assignees" in arguments:
                task_data["assignees"] = arguments["assignees"]
            if "tags" in arguments:
                task_data["tags"] = arguments["tags"]

            data = await clickup_request("POST", f"/list/{list_id}/task", json=task_data)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "task": data
                }, indent=2)
            )]

        elif name == "clickup_update_task":
            task_id = arguments["task_id"]
            update_data = {}

            # Add fields to update
            if "name" in arguments:
                update_data["name"] = arguments["name"]
            if "description" in arguments:
                update_data["description"] = arguments["description"]
            if "status" in arguments:
                update_data["status"] = arguments["status"]
            if "priority" in arguments:
                update_data["priority"] = arguments["priority"]
            if "due_date" in arguments:
                update_data["due_date"] = arguments["due_date"]

            # Handle assignees separately
            if "assignees_add" in arguments:
                for assignee_id in arguments["assignees_add"]:
                    await clickup_request("POST", f"/task/{task_id}/assignee/{assignee_id}")
            if "assignees_remove" in arguments:
                for assignee_id in arguments["assignees_remove"]:
                    await clickup_request("DELETE", f"/task/{task_id}/assignee/{assignee_id}")

            if update_data:
                data = await clickup_request("PUT", f"/task/{task_id}", json=update_data)
            else:
                data = await clickup_request("GET", f"/task/{task_id}")

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "task": data
                }, indent=2)
            )]

        elif name == "clickup_get_task":
            task_id = arguments["task_id"]
            include_subtasks = arguments.get("include_subtasks", False)

            params = {}
            if include_subtasks:
                params["include_subtasks"] = "true"

            data = await clickup_request("GET", f"/task/{task_id}", params=params)
            return [TextContent(
                type="text",
                text=json.dumps(data, indent=2)
            )]

        elif name == "clickup_add_task_comment":
            task_id = arguments["task_id"]
            comment_data = {"comment_text": arguments["comment_text"]}

            if "assignee" in arguments:
                comment_data["assignee"] = arguments["assignee"]

            data = await clickup_request("POST", f"/task/{task_id}/comment", json=comment_data)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "comment": data
                }, indent=2)
            )]

        elif name == "clickup_get_custom_fields":
            list_id = arguments["list_id"]
            data = await clickup_request("GET", f"/list/{list_id}/field")
            fields = data.get("fields", [])
            return [TextContent(
                type="text",
                text=json.dumps({
                    "custom_fields": fields,
                    "count": len(fields)
                }, indent=2)
            )]

        elif name == "clickup_set_custom_field":
            task_id = arguments["task_id"]
            field_id = arguments["field_id"]
            value = arguments["value"]

            data = await clickup_request(
                "POST",
                f"/task/{task_id}/field/{field_id}",
                json={"value": value}
            )
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "field_update": data
                }, indent=2)
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": f"ClickUp API error: {e.response.status_code}",
                "detail": error_detail
            }, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "type": type(e).__name__
            }, indent=2)
        )]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
