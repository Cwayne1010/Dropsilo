# DOE Workspace - 4-Layer AI Orchestration System

A reliability-focused architecture that separates LLM orchestration from deterministic execution, with an upstream research knowledge base that drives everything.

## Architecture Overview

**Layer 0: Strategy** (`a. strategy/`)
- Research knowledge base organized by topic
- Accumulated research reveals SOPs, execution scripts, and high-leverage tasks
- Tracks skill arcs (learning paths) that unlock new capabilities
- Feeds downstream into directives and execution

**Layer 1: Directives** (`b. directives/`)
- Natural language SOPs that define what to do
- Living documents that improve through self-annealing
- Contains goals, inputs, tools, outputs, and edge cases

**Layer 2: Orchestration** (AI Agent)
- Intelligent routing and decision-making
- Reads directives, calls tools, handles errors
- Updates directives with learnings

**Layer 3: Execution** (`c. execution/`)
- Deterministic Python scripts
- Handles API calls, data processing, file operations
- Reliable, testable, fast

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.template .env

# Edit .env with your API keys
nano .env
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install anthropic python-dotenv requests modal

# For Google Sheets integration
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Google OAuth Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Sheets API
3. Create OAuth 2.0 credentials
4. Download as `credentials.json` in root directory
5. Run your first script - it will generate `token.json`

### 4. Modal Setup (For Webhooks)

```bash
# Install Modal
pip install modal

# Authenticate
modal token new

# Create secrets
modal secret create workspace-secrets \
  ANTHROPIC_API_KEY=your_key_here \
  OPENAI_API_KEY=your_key_here

# Deploy webhooks
modal deploy execution/modal_webhook.py
```

## Directory Structure

```
.
├── CLAUDE.md                # Agent instructions (mirrored)
├── AGENTS.md                # Same instructions for other AI tools
├── GEMINI.md                # Same instructions for Gemini
├── README.md                # This file
├── .env                     # Environment variables (not committed)
├── .env.template            # Environment template
├── .gitignore               # Git ignore rules
├── a. strategy/             # Layer 0: Research knowledge base
│   └── Dropsilo/
│       ├── 0_unsorted/      # Research that doesn't fit existing topics
│       ├── 1_centralized_database/
│       ├── 2_business_model/
│       ├── 3_product/
│       ├── 4_hardware_infrastructure/
│       ├── 5_general_consultancy/
│       └── 6_user_input/
│       # Each subfolder contains:
│       #   _index.md  - Summary, research table, SOP/task candidates
│       #   _skills.md - Learning paths (skill arcs)
│       #   {ID}_{slug}.md - Individual research entries
├── b. directives/           # Layer 1: What to do (SOPs)
│   ├── research_relay.md    # SOP for filing research
│   ├── example_directive.md
│   └── Subcontractors/
├── c. execution/            # Layer 3: Doing the work
│   ├── clickup_mapping.json # Strategy → ClickUp list ID mapping
│   ├── clickup_mcp/         # ClickUp MCP server
│   ├── appraisal/           # Appraisal workflow scripts
│   ├── n8n/                 # n8n automation workflows
│   └── webhooks.json
└── .tmp/                    # Temporary files (not committed)
```

## Usage

### Creating a New Directive

1. Create `directives/my_task.md` with structure:
   - Goal
   - Inputs
   - Process (step-by-step)
   - Tools (scripts to use)
   - Outputs
   - Edge Cases

2. Create execution script if needed: `execution/my_task.py`

3. Tell the AI: "Follow the directive in directives/my_task.md"

### Relaying Research

Paste text, provide URLs, or upload files. The agent will:
1. Extract and classify the content into the right strategy topic
2. File it with key takeaways, analysis, and cross-references
3. Flag potential SOPs and execution scripts
4. Update skill arcs (learning paths)
5. Recommend 1-3 high-leverage tasks (pushed to ClickUp only on your approval)

```
"File this research on cold email benchmarks"
"Relay this article: [URL]"
"Add this to the outreach_pitch knowledge base"
```

The research relay follows `b. directives/research_relay.md`.

### Adding a Webhook

```bash
# Tell the AI
"Add a webhook that sends daily reports"

# The AI will:
# 1. Read directives/add_webhook.md
# 2. Create the directive
# 3. Update execution/webhooks.json
# 4. Guide you through deployment
```

### Self-Annealing

When errors occur:
1. AI reads error and stack trace
2. Fixes the script
3. Tests the fix
4. Updates the directive with learnings
5. System is now stronger

## Key Principles

- **Deliverables live in the cloud** (Google Sheets, Slides, etc.)
- **Local files are temporary** (everything in `.tmp/` is regenerated)
- **Directives are living documents** (improve through use)
- **Check for tools first** (don't recreate what exists)
- **Deterministic beats probabilistic** (push complexity to Python)
- **Research relay: file before you forget** (all research goes into strategy)
- **Flag, don't draft** (recommend SOPs and tasks, wait for approval)

## File Organization

- **Deliverables**: Google Sheets, Slides, Docs (user-accessible)
- **Intermediates**: Local files in `.tmp/` (regenerated as needed)
- **Never commit**: `.env`, `credentials.json`, `token.json`, `.tmp/`

## Webhook Endpoints

After deploying to Modal:

URLs are generated by Modal at deploy time. Run `modal deploy execution/modal_webhook.py` to get your endpoints.

## Common Commands

```bash
# Deploy webhooks
modal deploy execution/modal_webhook.py

# List active Modal apps
modal app list

# View Modal logs
modal app logs claude-orchestrator

# Run a Python script
python execution/my_script.py --param value
```

## Best Practices

1. **Read before modifying** - Always check existing code/directives first
2. **Update directives** - Document learnings as you discover them
3. **Batch API calls** - Respect rate limits, use batch endpoints
4. **Error handling** - Retry once, then fail gracefully with context
5. **Test locally first** - Verify scripts work before deploying webhooks

## Troubleshooting

### "No module named 'anthropic'"
```bash
pip install anthropic
```

### "credentials.json not found"
Set up Google OAuth (see Quick Start #3)

### "Modal authentication failed"
```bash
modal token new
```

### Webhook not found
Check `execution/webhooks.json` for correct slug mapping

## Contributing

This is a self-annealing system. As you use it:
- Update directives with learnings
- Fix bugs in execution scripts
- Document edge cases
- Improve error handling

The system gets smarter with each iteration.

## Notes

- Use Claude Opus 4.5 for best results
- All webhook activity streams to Slack (if configured)
- Rate limits and API constraints are learned and documented
- Focus on reliability over speed
