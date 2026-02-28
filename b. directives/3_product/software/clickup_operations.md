# ClickUp Operations Directive

## Goal
Provide intelligent routing and orchestration for ClickUp CRM operations in the Rhizome workspace via MCP server.

## Overview
The ClickUp MCP server (`execution/clickup_mcp/server.py`) exposes ClickUp API as native tools. Your job is to interpret user requests, call the right tools in the right order, and handle errors gracefully.

## Tools Available

### Discovery Tools
- `clickup_get_workspaces` - Find workspace/team IDs
- `clickup_get_spaces` - List spaces in workspace
- `clickup_get_lists` - Get lists from space or folder
- `clickup_get_custom_fields` - See available custom fields for a list

### Task Operations
- `clickup_get_tasks` - Get tasks from a list
- `clickup_search_tasks` - Search across workspace
- `clickup_get_task` - Get detailed task info
- `clickup_create_task` - Create new task
- `clickup_update_task` - Update existing task
- `clickup_add_task_comment` - Add comment to task
- `clickup_set_custom_field` - Set custom field value

## Common Workflows

### 1. First-Time Setup: Discover Workspace Structure

**User says**: "Show me my ClickUp workspace structure"

**Steps**:
1. Call `clickup_get_workspaces` to find Rhizome workspace ID
2. Call `clickup_get_spaces` with team_id to see all spaces
3. For key spaces, call `clickup_get_lists` to see lists
4. Present structure in readable format

**Cache**: Store workspace_id, space_ids, list_ids for future operations

**Expected result**: User sees their workspace hierarchy and you have IDs for future operations

---

### 2. Create Task: Simple

**User says**: "Create a task called 'Follow up with John' in Sales"

**Steps**:
1. If you don't have list IDs cached, search for "Sales" list first
2. Call `clickup_create_task` with:
   - `list_id`: Sales list ID
   - `name`: "Follow up with John"
3. Return task URL and confirmation

**Edge cases**:
- Multiple lists named "Sales" → ask user which one
- List doesn't exist → suggest creating it or ask for alternative

---

### 3. Create Task: Complex

**User says**: "Create a high priority task for Sarah to reach out to Acme Corp by Friday, tagged with 'hot-lead'"

**Steps**:
1. Get list_id (from context or ask user)
2. Calculate Friday's timestamp (Unix ms)
3. Get Sarah's user_id (search workspace users or use cached)
4. Call `clickup_create_task` with:
   - `list_id`: appropriate list
   - `name`: "Reach out to Acme Corp"
   - `assignees`: [Sarah's user_id]
   - `priority`: 2 (high)
   - `due_date`: Friday timestamp
   - `tags`: ["hot-lead"]
5. Return confirmation with task link

**Edge cases**:
- Sarah not found → ask for clarification or user_id
- Ambiguous date → confirm with user
- Invalid priority → default to Normal (3)

---

### 4. Search Tasks

**User says**: "Show me all tasks assigned to me that are in progress"

**Steps**:
1. Get workspace_id (cached or fetch)
2. Get current user's user_id (from auth or ask)
3. Call `clickup_search_tasks` with:
   - `team_id`: workspace_id
   - `assignees`: [user_id]
   - `statuses`: ["in progress"]
4. Format results with task names, due dates, list names

**Variations**:
- "Overdue tasks" → filter by due_date < now
- "Tasks with tag X" → use custom field filtering
- "Tasks in space Y" → add space_ids filter

---

### 5. Update Task Status

**User says**: "Mark task #abc123 as complete"

**Steps**:
1. Call `clickup_update_task` with:
   - `task_id`: "abc123"
   - `status`: "complete" (or workspace's closed status)
2. Confirm update

**Edge cases**:
- Task doesn't exist → error message with suggestion
- Invalid status → list available statuses for that task
- Task already closed → inform user

---

### 6. Bulk Operations

**User says**: "Create tasks for each lead in the Google Sheet"

**Steps**:
1. Read Google Sheet (use existing sheet tools)
2. Get target list_id in ClickUp
3. For each row:
   - Call `clickup_create_task` with lead data
   - Map sheet columns to task fields
   - Add custom fields if needed
4. Track successes/failures
5. Report summary

**Error handling**:
- If any task fails, log it but continue
- Report all failures at end
- Suggest fixes for common errors

---

### 7. Custom Fields

**User says**: "Set the 'Deal Value' field to $50,000 for task #xyz789"

**Steps**:
1. Get task details: `clickup_get_task` with task_id
2. Get list custom fields: `clickup_get_custom_fields` with list_id
3. Find "Deal Value" field_id
4. Call `clickup_set_custom_field` with:
   - `task_id`: "xyz789"
   - `field_id`: found field_id
   - `value`: 50000 (or appropriate format)
5. Confirm update

**Edge cases**:
- Field doesn't exist → list available fields
- Wrong value type → convert or error with guidance
- Multiple matching fields → ask user which one

---

## Multi-System Workflows

### Pattern: New Lead Capture

**Trigger**: Webhook receives new lead data

**Flow**:
1. Parse lead data from webhook
2. Create ClickUp task in "New Leads" list
3. Set custom fields (company, contact, source)
4. Update Google Sheet tracking log
5. Send Slack notification to sales team
6. Return success confirmation

**Tools used**: MCP ClickUp + sheet tools + send_email + Slack webhook

---

### Pattern: Deal Stage Progression

**User says**: "Move the Acme Corp deal to 'Proposal Sent' and schedule a follow-up in 3 days"

**Flow**:
1. Search for Acme Corp task
2. Update task status to "Proposal Sent"
3. Create follow-up task with due_date = now + 3 days
4. Link tasks (parent/subtask or dependency)
5. Add comment noting the progression
6. Confirm all updates

---

## Error Handling

### API Rate Limits
- ClickUp: 100 requests/minute, 10,000/hour
- If hit: wait 60s, retry once, then inform user
- For bulk ops: add small delays between requests

### Authentication Errors
- Check CLICKUP_API_KEY is set
- Verify key has workspace access
- Guide user to regenerate if needed

### Not Found Errors (404)
- Verify IDs are correct
- Suggest using search/list tools to find correct ID
- Update cached IDs if stale

### Validation Errors (400)
- Read error message carefully
- Common issues: invalid status name, wrong field type
- Suggest corrections based on error

---

## Self-Annealing Notes

### API Timing
- Search can be slow with large workspaces (2-5s)
- Batch operations: add 100ms delay between requests
- Custom fields: cache field_id mappings per list

### Status Names
- Status names vary by list
- "complete", "closed", "done" all map differently
- Always check list statuses first for updates

### Custom Field Types
- Text: string value
- Number: integer/float
- Dropdown: option_id (not option name!)
- Date: Unix timestamp in milliseconds
- Users: array of user_ids

### Common User Patterns
- Users often reference tasks by name, not ID
- Search before update/comment operations
- Cache workspace structure for session

---

## Integration Points

### Google Sheets
- Import leads → ClickUp tasks
- Export ClickUp tasks → Sheet reporting
- Sync status updates bidirectionally

### Email (send_email.py)
- Task created → notify assignee
- Status changed → update stakeholders
- Overdue tasks → automated reminders

### Modal Webhooks
- External form → ClickUp task
- Zapier/Make → ClickUp automation
- Calendar events → ClickUp tasks

---

## Quick Reference

### Priority Levels
1. Urgent (red)
2. High (yellow)
3. Normal (white)
4. Low (gray)

### Common Status Mappings
- Open: "to do", "open", "new"
- Active: "in progress", "working", "active"
- Blocked: "blocked", "waiting"
- Done: "complete", "closed", "done"

### Date Format
Always use Unix timestamp in milliseconds:
```python
import time
timestamp_ms = int(time.time() * 1000)
```

---

## Testing Checklist

Before deploying changes:
- [ ] Test workspace discovery
- [ ] Create task with all field types
- [ ] Search by different filters
- [ ] Update task status
- [ ] Add comments and tags
- [ ] Set custom field values
- [ ] Error handling (invalid IDs, rate limits)
- [ ] Multi-task bulk operation

---

## Future Enhancements

Ideas to implement as needs arise:
- Time tracking integration
- Recurring tasks automation
- Smart task prioritization based on due dates
- ClickUp → Slack real-time notifications
- Natural language due date parsing ("next Friday")
- Task dependencies and blocking
- Attachments and file uploads
- Checklists and subtasks
- Workspace templates
- Advanced custom field automation

Add to this section as you discover patterns.
