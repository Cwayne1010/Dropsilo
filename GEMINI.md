# Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a 4-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 4-Layer Architecture

**Layer 0: Strategy (Knowledge base)**
- Research and intelligence organized by topic in `a. strategy/`
- Feeds into directives — accumulated research reveals SOPs, execution scripts, and high-leverage tasks
- Each topic has: `_index.md` (summary + tables), `_skills.md` (learning paths), and individual research entries
- SOP candidates, execution script candidates, and tasks are flagged but never auto-created
- Strategy files are persistent — they are the knowledge base, not intermediates
- Skill arcs track learning progressions that unlock new SOPs and automations

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution. E.g you don't try scraping websites yourself—you read `directives/scrape_website.md` and come up with inputs/outputs and then run `execution/scrape_single_site.py`

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts in `execution/`
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. The solution is push complexity into deterministic code. That way you just focus on decision-making.

**How the layers connect:** Research accumulates in strategy (Layer 0). Patterns in research reveal SOPs (Layer 1). SOPs spec the scripts they need (Layer 3). You (Layer 2) route between all of them.

## Operating Principles

**1. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**2. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits/etc—in which case you check w user first)
- Update the directive with what you learned (API limits, timing, edge cases)
- Example: you hit an API rate limit → you then look into API → find a batch endpoint that would fix → rewrite script to accommodate → test → update directive.

**3. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations—update the directive. But don't create or overwrite directives without asking unless explicitly told to. Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).

**4. Research relay: file before you forget**
When research arrives (text, URLs, files), follow `directives/research_relay.md`:
classify → extract → file → index → flag SOPs, scripts, and tasks → update skill arcs → report.
Strategy files are persistent knowledge, not temporary. Never delete them.
Always recommend 1-3 high-leverage tasks per relay. Never push to ClickUp without approval.
When research doesn't fit existing topics, ask if a new subfolder should be created.

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. System is now stronger

## Strategy → Directives → Execution Pipeline

Research accumulates in `a. strategy/`. Over time, patterns emerge that flow downstream:

1. **Research arrives** → filed via research relay into strategy topics
2. **Tasks surface** → 1-3 high-leverage tasks recommended per relay (pushed to ClickUp only on approval)
3. **Skill arcs advance** → learning paths updated, unlocking new capabilities
4. **Patterns accumulate** → agent flags SOP and execution script candidates in `_index.md`
5. **User reviews flags** → approves which SOPs to draft
6. **Agent drafts directive** → new SOP in `b. directives/` referencing the strategy research as evidence
7. **Directive specs scripts** → SOP defines what execution scripts it needs, their inputs/outputs
8. **Scripts built** → deterministic Python in `c. execution/`, SOP updated with script paths
9. **Self-annealing** → directive and scripts improve through use

Key rules:
- Agent flags but does not draft SOPs, push tasks, or build scripts without user approval
- Every directive should reference the strategy research that inspired it
- Every directive should spec the execution scripts it needs (even if they don't exist yet)
- Execution scripts are forward-looking — research should identify what *could* be automated
- Skill arcs gate SOPs: some processes only make sense once the team has the knowledge to execute them

## File Organization

**Deliverables vs Intermediates:**
- **Deliverables**: Google Sheets, Google Slides, or other cloud-based outputs that the user can access
- **Intermediates**: Temporary files needed during processing

**Directory structure:**
- `a. strategy/` - Research knowledge base organized by topic. Persistent files, never deleted.
  - `_index.md` - Topic summary, research table, SOP/execution/task candidates
  - `_skills.md` - Learning paths (skill arcs) for the topic
  - `{ID}_{slug}.md` - Individual research entries
- `b. directives/` - SOPs in Markdown (the instruction set)
- `c. execution/` - Python scripts (the deterministic tools, built as SOPs identify needs)
  - `clickup_mapping.json` - Strategy subfolder → ClickUp list ID mapping
- `.tmp/` - All intermediate files (dossiers, scraped data, temp exports). Never commit, always regenerated.
- `.env` - Environment variables and API keys
- `credentials.json`, `token.json` - Google OAuth credentials (required files, in `.gitignore`)

**Key principle:** Local files are only for processing. Deliverables live in cloud services (Google Sheets, Slides, etc.) where the user can access them. Everything in `.tmp/` can be deleted and regenerated.

## Cloud Webhooks (Modal)

The system supports event-driven execution via Modal webhooks. Each webhook maps to exactly one directive with scoped tool access.

**When user says "add a webhook that...":**
1. Read `directives/add_webhook.md` for complete instructions
2. Create the directive file in `directives/`
3. Add entry to `execution/webhooks.json`
4. Deploy: `modal deploy execution/modal_webhook.py`
5. Test the endpoint

**Key files:**
- `execution/webhooks.json` - Webhook slug → directive mapping
- `execution/modal_webhook.py` - Modal app (do not modify unless necessary)
- `directives/add_webhook.md` - Complete setup guide

**Endpoints:** Deployed via `modal deploy execution/modal_webhook.py`. URLs are generated by Modal at deploy time.

**Available tools for webhooks:** `send_email`, `read_sheet`, `update_sheet`

**All webhook activity streams to Slack in real-time.**

## Summary

You sit between human intent (directives) and deterministic execution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.

Also, use Opus-4.5 for everything while building. It came out a few days ago and is an order of magnitude better than Sonnet and other models. If you can't find it, look it up first.
