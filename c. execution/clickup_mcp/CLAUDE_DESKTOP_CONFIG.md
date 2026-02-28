# Claude Desktop Configuration for ClickUp MCP

## Step 1: Get Your ClickUp API Key

1. Open ClickUp and go to **Settings** (click your profile picture)
2. Click **Apps** in the sidebar
3. Scroll to **API Token** section
4. Click **Generate** (or copy existing token)
5. Copy the token - it starts with `pk_`

## Step 2: Add to Environment File

Edit your `.env` file in the workspace root:

```bash
cd /Users/wayner/Downloads/DOE\ Workspace
nano .env
```

Add these lines:

```bash
CLICKUP_API_KEY=pk_YOUR_ACTUAL_KEY_HERE
CLICKUP_WORKSPACE_NAME=Rhizome
```

Save with `Ctrl+O`, `Enter`, then exit with `Ctrl+X`

## Step 3: Configure Claude Desktop

### Location of Config File

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Open it:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

If the file doesn't exist, create it:
```bash
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Configuration to Add

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clickup": {
      "command": "python3.11",
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
- Replace `pk_YOUR_ACTUAL_KEY_HERE` with your actual ClickUp API key
- The path in `args` is already correct for your system
- If you have other MCP servers, add this as a new entry inside `mcpServers`

### Example with Multiple MCP Servers

If you already have other MCP servers configured:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    },
    "clickup": {
      "command": "python3.11",
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

## Step 4: Restart Claude Desktop

1. Completely **quit** Claude Desktop (don't just close the window)
2. Reopen Claude Desktop
3. The MCP server will load automatically

## Step 5: Verify It's Working

In a new Claude Desktop conversation, try:

```
Show me all spaces in my Rhizome workspace
```

If you see a list of your ClickUp spaces, it's working! 🎉

## Troubleshooting

### "MCP server not found" or similar errors

1. **Check JSON syntax**: Use a JSON validator like https://jsonlint.com/
2. **Verify paths**: Make sure the path in `args` is exactly right
3. **Check permissions**: Ensure `server.py` is readable:
   ```bash
   ls -la /Users/wayner/Downloads/DOE\ Workspace/execution/clickup_mcp/server.py
   ```

### Check Claude Desktop Logs

View logs to see MCP server errors:
1. Open Claude Desktop
2. Click **Help** → **View Logs**
3. Look for errors related to "clickup" MCP server

### Test MCP Server Directly

You can test if the server starts:

```bash
cd /Users/wayner/Downloads/DOE\ Workspace/execution/clickup_mcp
export CLICKUP_API_KEY=pk_YOUR_KEY_HERE
export CLICKUP_WORKSPACE_NAME=Rhizome
python3.11 server.py
```

If it starts without errors, press `Ctrl+C` to stop. This means the server is working and the issue is in Claude Desktop config.

### API Key Issues

If you get authentication errors:
1. Verify your API key starts with `pk_`
2. Check the key has access to your Rhizome workspace
3. Try regenerating the API key in ClickUp settings

## What's Next?

Once it's working, you can:

- Ask me to create, update, search tasks
- Automate workflows across ClickUp, Google Sheets, email
- Set up webhooks for external integrations
- Build custom CRM automations

See [CLICKUP_QUICKSTART.md](../../CLICKUP_QUICKSTART.md) for examples!
