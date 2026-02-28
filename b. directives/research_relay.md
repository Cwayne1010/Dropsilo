# Research Relay Directive

## Goal
Classify, extract, file, and index incoming research into the strategy knowledge base (`a. strategy/Dropsilo/`). Support text, URLs, files, or any mix. Maintain summary indexes, handle cross-topic research, track skill arcs, generate high-leverage task recommendations, and flag potential SOPs and execution scripts — without drafting or pushing anything without user approval.

## Inputs
- `content` (string|list): Pasted text, URLs, file paths, or a mix
- `title` (string, optional): User-provided title for the research
- `topic_override` (string, optional): Force-file to a specific subfolder
- `auto_confirm` (boolean, optional): Skip classification confirmation (default: false)

## Process

### 1. Detect and extract
- Classify each input as text/url/file/mixed
- For URLs: fetch via WebFetch tool. If fetch fails, ask user to paste content or skip.
- For files: read and extract text content (PDF, DOCX, images, etc.)
- For text: accept pasted content as-is
- Store raw extractions in `.tmp/relay_{timestamp}_{slug}.md`
- If multiple distinct pieces of research are provided, process each as a separate entry

### 2. Classify into topics
- Read `a. strategy/Dropsilo/` folder structure for current topics
- Match content to primary and secondary topics using these categories:
  - `1_centralized_database/` — Customer data, methodology, regulations
  - `2_business_model/` — Branding, networking, pricing, outreach
  - `3_product/` — Database interfaces, software, automations
  - `4_hardware_infrastructure/` — CapEx/OpEx, equipment
  - `5_general_consultancy/` — Audits, freelance tiers, content strategy
  - `6_user_input/` — Iteration, feedback, feature requests
- If `topic_override` provided, use it
- If no match: **ask user** if a new subfolder should be created. Suggest a category and name. Only file to `0_unsorted/` if user explicitly chooses to park it there.
- Present classification to user for confirmation (unless `auto_confirm`):
  ```
  Classification:
    Primary: 2_business_model/outreach_pitch
    Secondary: 5_general_consultancy/content_strategy
  Proceed? (or suggest a different placement)
  ```

### 3. Assign ID and generate entry file
- Read target subfolder's `_index.md` for next sequential ID (or start at 001)
- Generate slugified filename: `{ID}_{slug}.md`
- Write entry file with all sections:

```markdown
# [Title]

> **ID**: 001
> **Date added**: YYYY-MM-DD
> **Source type**: text | url | file | mixed
> **Source**: [URL or description]
> **Added by**: research-relay

## Key Takeaways
- [3-7 bullet points distilling the most important insights]

## Full Content
[Complete extracted/processed content. Preserved so the knowledge survives even if the source disappears.]

## Context & Analysis
[How this connects to Dropsilo strategy. Why it matters. What it implies for decisions.]

## Cross-References
- Also filed in: [secondary topics with entry IDs]
- Relates to: [other topics with brief explanation]

## SOP Connections
> **Potential SOP**: [Name]
> **Confidence**: Low | Medium | High
> **Rationale**: [Why this suggests a repeatable process]
> **Status**: Flagged — awaiting user go-ahead

## Execution Connections
> **Potential script**: [Name and purpose]
> **Inputs/Outputs**: [What the script would take and produce]
> **Status**: Flagged — awaiting SOP and user approval

## Skill Arc Connections
- **Advances**: [Skill arc name] ([Previous level] → [New level])
- **New arc suggested**: [If this reveals a new learning path]

## Recommended Tasks
1. [HIGH/MED/LOW] [Task description]
2. [HIGH/MED/LOW] [Task description]
3. [HIGH/MED/LOW] [Task description]

## Revision History
- YYYY-MM-DD: Initial entry via research-relay
```

### 4. Update `_index.md`
- Create `_index.md` if it doesn't exist, using this template:

```markdown
# [Topic Name] — Research Index

> Last updated: YYYY-MM-DD

## Summary
[2-4 sentence distillation of what research in this folder tells us so far. Rewritten each time new research is added.]

## Research Entries

| ID | Date | Title | Source Type | SOP Flag |
|----|------|-------|-------------|----------|

## Cross-References
[Links to related topics]

## SOP Candidates
[Checkboxes for flagged SOPs — never checked without user approval]

## Execution Candidates
[Potential scripts identified from research]

## Task Recommendations

| Task | Priority | Source Entry | Status |
|------|----------|-------------|--------|

## Notes
[Freeform section for context that doesn't fit elsewhere]
```

- Add row to Research Entries table
- Rewrite Summary to incorporate new research
- Update Cross-References, SOP Candidates, Execution Candidates
- Add task recommendations to Task Recommendations table with status: `recommended`

### 5. Update `_skills.md`
- If research advances an existing skill arc, update it:
  - Bump level if warranted
  - Add research entry ID to the arc
  - Update "Next step"
  - Check if any SOPs/scripts are now unlocked
- If research suggests a new skill arc, propose it to user:
  ```
  New skill arc detected: "[Name]"
  Goal: [What mastery looks like]
  Starting level: Novice
  Create this arc? (y/n)
  ```
- Create `_skills.md` if it doesn't exist:

```markdown
# Skill Arcs — [Topic Name]

## Active Learning Paths

### [Skill Arc Name]
- **Goal**: [What mastery of this looks like]
- **Current level**: Novice
- **Research entries**: [Entry IDs]
- **Next step**: [What to learn or do next]
- **Unlocks**: [SOPs, scripts, or capabilities possible at higher levels]

## Completed Arcs
(Moved here when proficiency is reached)
```

### 6. Handle cross-references
For each secondary topic:
- Create cross-reference stub file: `{ID}_{slug}_xref.md`

```markdown
# [Title] (Cross-Reference)

> **Primary location**: `{category}/{subfolder}/{ID}_{slug}.md`
> **Relevance to this topic**: [1-2 sentences explaining why this matters here]
```

- Update secondary subfolder's `_index.md` with an `xref` row (Source Type = `xref`)
- Update primary entry's Cross-References section

### 7. Generate task recommendations
Analyze the research for high-leverage actions:
- What's the most impactful thing to do right now based on this knowledge?
- What decision could be made?
- What experiment or test could be run?
- What existing process could be improved?

Generate 1-3 tasks ranked by impact (HIGH/MED/LOW). Write them into:
- The entry file's `## Recommended Tasks` section
- The `_index.md` Task Recommendations table

### 8. Report and ask about ClickUp
Present summary to user:
```
Research filed: "[Title]"
→ Primary: [path to entry file]
→ Cross-ref: [secondary paths, if any]
→ SOP flagged: [name and confidence, if any]
→ Execution flagged: [script idea, if any]
→ Skill arc: [advances/creates arc name, if any]

Recommended tasks:
  1. [HIGH] [Task description]
  2. [MED] [Task description]
  3. [LOW] [Task description]

Push any to ClickUp? (specify numbers, or skip)
```

### 9. Push to ClickUp (only on approval)
When user approves task(s):
- Read `c. execution/clickup_mapping.json` for the target mapping
- ClickUp structure: single "Project" list (ID: 901710557083) with parent tasks as categories and subtasks as subfolders
- Use `clickup_create_task` with:
  - `list_id`: "901710557083" (always the Project list)
  - `name`: task title
  - `description`: why this is high-leverage + reference to strategy entry
  - `priority`: 2 (HIGH), 3 (MED), or 4 (LOW)
  - `tags`: `["research-relay", "{topic_slug}"]`
  - `parent`: parent_task_id from mapping (to nest under the right category subtask)
- Note: the MCP server's `clickup_create_task` may need a `parent` field added to support subtask creation. If not available, create at list level with a tag indicating the category.
- Update `_index.md` Task Recommendations status from `recommended` to `pushed`
- Confirm to user with task link

## Tools
- `WebFetch` — URL content extraction
- File reading capabilities — PDF, text, document extraction
- Direct file operations — creating/updating markdown files
- `clickup_create_task` — push approved tasks to ClickUp (via MCP server)
- `clickup_get_workspaces`, `clickup_get_spaces`, `clickup_get_lists` — discover ClickUp list IDs
- `c. execution/clickup_mapping.json` — strategy subfolder → ClickUp list ID mapping

## Outputs
- Research entry file(s) in `a. strategy/Dropsilo/{topic}/{subfolder}/`
- Updated `_index.md` file(s)
- Updated `_skills.md` file(s) (if skill arcs are affected)
- Cross-reference stub files (if multi-topic)
- Task(s) in ClickUp (only when user approves)
- Summary report to user

## Edge Cases

### URL fetch fails
- Ask user to paste content or skip
- Do not create partial entries

### No topic match
- **Ask user** if a new subfolder should be created
- Suggest a category and name based on the content
- Only file to `0_unsorted/` if user explicitly says so

### Research contradicts existing entries
- File normally
- Note contradiction in Context & Analysis: which entry it contradicts, why, and what the tension implies
- Update `_index.md` Summary to reflect the tension rather than silently picking a side
- Flag for user review if significant

### Very large content (50+ pages)
- Summarize in Full Content section
- Store full extracted text in `.tmp/relay_{timestamp}_{slug}_full.md` with reference in entry
- Expand Key Takeaways to 7-10 bullets

### User wants to correct existing research
- Update entry's relevant sections
- Add revision history line: `- YYYY-MM-DD: Corrected — [reason]`
- Update `_index.md` summary if affected

### Newer research supersedes older
- File as new entry
- Add note to old entry: `> **Superseded by entry {ID}** — see [{filename}]`
- Update `_index.md` to reflect which entry is current

### Multiple items in one session
- Batch classification confirmation: "I'll file these items as follows: [list]. Proceed?"
- Process each sequentially
- Update indexes once per affected subfolder (not per entry)
- Present all task recommendations together at the end

### ClickUp list ID not mapped
- Query ClickUp API: `clickup_get_workspaces` → `clickup_get_spaces` → `clickup_get_lists`
- Match by name to find the list ID
- Update `c. execution/clickup_mapping.json` with discovered ID
- Then push the task

### User dismisses a task recommendation
- Update `_index.md` Task Recommendations status to `dismissed`
- Do not re-recommend the same task in future relays

### Skill arc doesn't exist yet
- Suggest creating one with proposed name, goal, and starting level
- Wait for user approval before creating
- Don't silently create arcs

## Learning Notes
(Updated as the system learns)

- 2026-02-08: Initial directive created. All conventions are experimental — update this section as patterns emerge from real use.
