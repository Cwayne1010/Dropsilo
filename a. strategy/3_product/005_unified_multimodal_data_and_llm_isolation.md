# Unified Multi-Modal Data Architecture & Enterprise LLM Isolation

> **ID**: 005
> **Date added**: 2026-02-27
> **Source type**: text
> **Source**: Architecture design conversation — unifying structured, semi-structured, and unstructured data; enterprise LLM deployment patterns; multi-tenant bank isolation
> **Added by**: research-relay

## Key Takeaways
- Snowflake Cortex Search extends Snowflake into the RAG layer — structured, semi-structured, and unstructured data all live in one platform with unified governance
- Dify orchestrates two parallel tool calls per query: SQL agent (dbt Logic Views) + Cortex Search agent (document RAG) — LLM synthesizes both into a response
- The LLM is stateless between API calls — it cannot "combine" Bank A and Bank B data; contamination risk is entirely at the application and retrieval layer
- AWS Bedrock (Claude) or Azure OpenAI (GPT-4) deploy enterprise models inside Dropsilo's own cloud account — data never reaches the model provider's network
- Per-bank isolation requires four enforcement points: separate Dify workspaces, Snowflake credentials scoped to bank-specific DBs, namespaced Cortex Search with mandatory `bank_id` filter, and separate conversation history stores
- Fine-tuning on customer data must never happen — all customization via system prompts and RAG, which are isolated at the application layer
- Snowflake Tri-Secret Secure (customer-managed keys) means Dropsilo itself cannot decrypt a bank's data — architectural trust guarantee, not just a policy claim

## Full Content

### Three Classes of Data in Dropsilo

| Class | Examples | Storage |
|---|---|---|
| Structured | Core banking: accounts, loans, transactions, balances | Snowflake tables → dbt Logic Views |
| Semi-structured | jXchange XML/JSON, form submissions, API snapshots | Snowflake VARIANT columns |
| Unstructured | PDFs, tax returns, appraisals, emails, correspondence | Snowflake STAGE + Cortex Search index |

### The Unified Architecture: Snowflake as Single Source of Truth for All Data Types

Rather than running a separate vector database (Pinecone, Weaviate, Chroma) alongside Snowflake, Snowflake Cortex Search extends the existing platform into the RAG layer. Unstructured documents are:
1. Ingested via Dify IDP (text extracted from PDFs and scanned docs)
2. Stored in a Snowflake `DOCUMENTS` table + STAGE
3. Automatically indexed by Cortex Search with vector embeddings

This keeps RBAC, audit logging, encryption, and governance unified. There is no second system to manage, no cross-system join logic, and no separate access controls.

### The Dify Orchestration Pattern: Two-Tool Parallel Query

For every user query, Dify runs two tool calls simultaneously:

```
User: "Compile a loan request summary for John Smith"

Tool 1 — SQL Agent:
  → Queries Snowflake via dbt Logic Views (BANK_A_ROLE)
  → Returns: structured financials, existing exposure, deposit balances, credit flags

Tool 2 — Cortex Search Agent:
  → RAG query: "John Smith loan documents tax returns financial statements"
  → Filter: bank_id = 'BANK_A' (enforced at index level)
  → Returns: chunks from PDFs — income statements, appraisals, correspondence

LLM (AWS Bedrock / Claude):
  → Receives both tool outputs in context window
  → Synthesizes: "Structured data shows $2.1M exposure. Tax returns show income declined 18% YoY. Recommend senior credit review."
  → Response returned to user chat
```

### Why the LLM Is Not the Contamination Risk

The LLM model is stateless between API calls. It processes a context window, returns a response, and retains nothing. Bank A and Bank B data cannot "combine in the LLM" any more than two separate phone calls can contaminate each other on the same phone network.

**What can cause contamination (all application-layer):**

| Attack Surface | How contamination happens | Prevention |
|---|---|---|
| Prompt construction | Bank A data included in Bank B's prompt | Separate Dify workspaces with separate credentials |
| RAG retrieval | Bank A documents returned for Bank B query | Mandatory `bank_id` filter at Cortex Search index level |
| Conversation history | Bank A's history loaded in Bank B session | Session IDs scoped to `(bank_id, user_id)` |
| Fine-tuning | Model weights trained on both banks' data | Never fine-tune on customer data — prohibited |

### Enterprise LLM Deployment: AWS Bedrock

Instead of calling `api.anthropic.com` or `api.openai.com` directly, deploy via cloud marketplace:

```
Standard API route:
  Dify → HTTPS → api.anthropic.com (their servers, their logs, their network)

AWS Bedrock route (recommended):
  Dify → VPC → AWS Bedrock endpoint (model runs in Dropsilo's own AWS account)
                     ↑ Data never leaves the account boundary
                     ↑ AWS SOC 2, ISO 27001, HIPAA-eligible
                     ↑ CloudTrail logs every inference call
```

AWS Bedrock provides access to Claude (Anthropic) models running inside your own AWS infrastructure. Azure OpenAI provides the same for GPT-4/o1 in an Azure tenant. Same model weights, isolated compute.

**What enterprise deployment buys:**
- Zero data retention post-inference
- No model training on customer prompts
- Data stays in your cloud account boundary
- Full audit log of every API call (AWS CloudTrail)
- Regional data residency

### Multi-Tenant Isolation Architecture

```
                    AWS Bedrock (Claude)
                    ┌─────────────────┐
                    │  Shared model   │
                    │  Stateless API  │
                    │  Zero retention │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼──────────┐      ┌──────────▼──────────┐
    │  Dify: Bank A WS   │      │  Dify: Bank B WS    │
    │  System prompt A   │      │  System prompt B    │
    │  BANK_A credentials│      │  BANK_B credentials │
    └─────────┬──────────┘      └──────────┬──────────┘
              │                             │
    ┌─────────▼──────────┐      ┌──────────▼──────────┐
    │  SQL tool          │      │  SQL tool           │
    │  Role: BANK_A_ROLE │      │  Role: BANK_B_ROLE  │
    │  Schema: BANK_A.*  │      │  Schema: BANK_B.*   │
    └─────────┬──────────┘      └──────────┬──────────┘
              │                             │
    ┌─────────▼──────────┐      ┌──────────▼──────────┐
    │  RAG tool          │      │  RAG tool           │
    │  filter: BANK_A    │      │  filter: BANK_B     │
    └────────────────────┘      └─────────────────────┘
              │                             │
    ┌─────────▼────────────────────────────▼──────────┐
    │                  SNOWFLAKE                       │
    │  DB: BANK_A (BANK_A_ROLE — no access to BANK_B) │
    │  DB: BANK_B (BANK_B_ROLE — no access to BANK_A) │
    │  Cortex Search: namespaced by bank_id            │
    └─────────────────────────────────────────────────┘
```

Isolation is enforced at the **credential level**, not at the policy level. BANK_A_ROLE has no permissions on BANK_B.* — this is a Snowflake GRANT configuration, not a runtime check that can be bypassed.

### RBAC Threading Through the Agent Layer

User bank role (Credit Officer, Risk Manager, CEO) must propagate end-to-end:

```
User auth token (carries role claim)
  → Dify receives role in request context
  → SQL tool uses Snowflake service account scoped to that role's dbt Logic View
  → RAG tool applies role-level document filter (some docs restricted by role)
  → LLM system prompt includes role context
  → Response contains only what that role is permitted to see
```

**Critical rule**: RBAC is enforced at Snowflake, not at the prompt. The database returns only what the role is permitted to see — the agent never fetches restricted data and then decides to hide it.

### Snowflake Tri-Secret Secure: The Trust Guarantee

With Tri-Secret Secure activated per bank:
- The bank holds its own encryption key in a Hardware Security Module (HSM)
- Dropsilo's Snowflake account cannot decrypt the data without the bank's key
- If the bank revokes the key, Dropsilo's access is immediately severed
- This is a provable, hardware-enforced guarantee: "We cannot access your data"

This turns a compliance checkbox into a sales differentiator and a trust architecture.

## Context & Analysis

This research resolves the major open architectural question for Dropsilo's multi-modal expansion: how to extend from structured data into documents and unstructured content without fragmenting the security and governance model. The answer — Snowflake Cortex Search as the RAG layer — keeps everything in one governed platform.

The LLM isolation question reveals a common misconception in the market: most bank IT staff assume "data combining in the AI" is an LLM-layer problem. It is not. Clarifying this in bank conversations (the LLM is stateless, isolation is enforced in the layers below) is a credibility signal and a way to advance the technical sale.

AWS Bedrock is the right near-term deployment decision. It gives enterprise model capability (Claude 3.5/3.7 Sonnet) with data sovereignty (your AWS account), auditability (CloudTrail), and compliance coverage (SOC 2, HIPAA-eligible). It also creates a natural upgrade path — as the bank relationship deepens, they can move to their own Bedrock deployment for maximum isolation.

The per-bank Dify workspace + Snowflake role provisioning process is highly repeatable and should become a standardized onboarding procedure. Every new bank client requires the same setup steps.

## Cross-References
- Also relevant to: `1_centralized_database/003_banking_ai_compliance_stack.md` — compliance requirements this architecture satisfies (GLBA, FFIEC vendor risk, SR 11-7 model inventory)
- Also relevant to: `3_product/002_confidential_computing_private_ai.md` — Tri-Secret Secure (Attachment 4) and TEE wrapper (Attachment 1) connect directly to this architecture
- Relates to: `3_product/001_dropsilo_technical_framework.md` — this entry extends the base architecture with multi-modal data and LLM deployment specifics

## SOP Connections
> **Potential SOP**: Multi-Tenant Bank Provisioning Procedure
> **Confidence**: High
> **Rationale**: Every new bank onboarded requires the same repeatable setup: create Snowflake DB + role, provision Dify workspace with scoped credentials, configure Cortex Search namespace, activate Tri-Secret Secure, set up CloudTrail logging. This is the core operational SOP for scaling Dropsilo.
> **Status**: Flagged — awaiting user go-ahead

> **Potential SOP**: Document Ingestion Pipeline Setup
> **Confidence**: Medium
> **Rationale**: Ingesting unstructured documents (PDFs, tax returns, appraisals) into Snowflake via Dify IDP and indexing in Cortex Search will be repeated for every bank client and document type onboarded.
> **Status**: Flagged — awaiting user go-ahead

> **Potential SOP**: Bank Onboarding Compliance Checklist (existing flag — confidence upgraded to High)
> **Confidence**: High (upgraded from previous research)
> **Rationale**: This research adds the LLM deployment documentation, Bedrock configuration, and multi-tenant isolation verification to the compliance checklist. The full checklist now covers: GLBA data map, SR 11-7 model inventory, FFIEC vendor risk docs, BSA/AML output boundary, Bedrock deployment config, per-bank Dify workspace verification, Tri-Secret Secure activation.
> **Status**: Flagged — awaiting user go-ahead

## Execution Connections
> **Potential script**: Bank provisioning automation
> **Inputs/Outputs**: bank_id, bank_name, contact info → Snowflake DB + role created, Dify workspace provisioned, Cortex Search namespace initialized, configuration report
> **Status**: Flagged — awaiting SOP and user approval

> **Potential script**: Multi-tenant isolation validator
> **Inputs/Outputs**: bank_id → test suite confirming: (1) BANK_X_ROLE cannot query other bank schemas, (2) Cortex Search returns only bank_id-filtered results, (3) Dify workspace credentials cannot reach cross-bank Snowflake objects
> **Status**: Flagged — awaiting SOP and user approval

## Skill Arc Connections
- **Advances**: Banking AI Regulatory Compliance (Novice → Familiar) — multi-tenant isolation and enterprise LLM deployment directly address GLBA, FFIEC vendor risk, and SR 11-7 model boundary requirements
- **Advances**: Data Warehouse Architecture (Novice → Familiar) — Cortex Search, VARIANT columns, and Tri-Secret Secure extend the Snowflake knowledge base significantly
- **New arc suggested**: Multi-Tenant SaaS Architecture — understanding workspace isolation, credential scoping, per-tenant provisioning, and isolation testing as a repeatable engineering discipline
  - Goal: ability to provision a new bank client end-to-end (Snowflake + Dify + RAG + Bedrock) reliably and verify isolation programmatically
  - Starting level: Novice

## Recommended Tasks
1. [HIGH] Make the AWS Bedrock deployment decision — select Claude model tier on Bedrock, confirm AWS account structure, and lock in the LLM deployment pattern before any bank pilot begins
2. [HIGH] Design the per-bank provisioning checklist — enumerate every setup step for a new bank client (Snowflake role, Dify workspace, Cortex Search namespace, Tri-Secret Secure, CloudTrail) to form the foundation of the Bank Provisioning SOP
3. [MED] Prototype the two-tool Dify workflow — SQL agent + Cortex Search agent running in parallel against mock bank data, with LLM synthesis — validates the core query pattern before production data

## Revision History
- 2026-02-27: Initial entry via research-relay
