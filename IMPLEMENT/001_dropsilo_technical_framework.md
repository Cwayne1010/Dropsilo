# Dropsilo Technical Framework

> **ID**: 001
> **Date added**: 2026-02-12
> **Source type**: text
> **Source**: User-provided technical brief
> **Added by**: research-relay

## Key Takeaways
- Unified Data Fabric built on a Cloud Data Warehouse (e.g., Snowflake) as the single source of truth
- Real-time ingestion from Jack Henry core via jXchange middleware APIs
- Semantic layering via dbt maps raw core data into department-specific Logic Views with RBAC
- Consistent metric definitions (e.g., "Total Exposure", "Customer Health") rendered through different perceptions per role (Credit, Risk, Retail)
- Agentic orchestration via Dify manages Document Lifecycle using IDP and RAG
- Natural Language Query (NLQ) interface enables executives to run ad-hoc risk assessment and portfolio analysis in plain English
- End result: automated data pipeline that appends audit trails, KYC/AML verification, and credit spreading metadata as loan files progress

## Full Content
**Unified Data Fabric:** A centralized Cloud Data Warehouse (e.g., Snowflake) that serves as the single source of truth, ingesting real-time data from the Jack Henry core via middleware APIs (jXchange).

**Semantic Layering:** Utilizing a tool like dbt (data build tool) to map raw core data into department-specific Logic Views. This ensures that "Total Exposure" or "Customer Health" is calculated consistently but presented through different perceptions (Credit, Risk, or Retail) based on Role-Based Access Control (RBAC).

**Agentic Orchestration:** An AI orchestration platform (Dify) that manages the Document Lifecycle. It utilizes Intelligent Document Processing (IDP) and RAG (Retrieval-Augmented Generation) to extract data from unstructured sources and append it to the master record.

**Natural Language Query (NLQ):** A Conversational Analytics interface allowing executives to perform ad-hoc risk assessment and portfolio analysis using plain-English prompts directly against the governed database.

**The Business Outcome:** This architecture transforms the bank from a siloed manual operation to an automated data pipeline. As a loan file progresses, the system automatically appends audit trails, KYC/AML verification, and credit spreading metadata. This results in reduced time-to-decision, improved regulatory explainability, and a lower efficiency ratio.

### The Intelligence Agency Analogy

To visualize how Dropsilo functions, imagine the business as a high-end Global Intelligence Agency. Here is how data moves from the "Old Vault" to the "Executive's Desk":

1. **The Vault (Jack Henry / SilverLake)** — A massive, underground, 100-year-old Steel Vault containing millions of handwritten ledger books. It is the absolute "Source of Truth," but incredibly difficult to access. Strictly guarded, and the books are written in a specific, archaic code that only a few veteran clerks understand.

2. **The Master Translator (jXchange)** — The Head Courier & Translator. The only person allowed to talk to the vault clerks. When you want to know a customer's balance, you send this courier a formal request (an XML "Message"). The courier goes into the vault, finds the right ledger, translates the old code into a standardized report, and brings it back to the surface.

3. **The Secure Transport (Ingestion Pipeline)** — An Armored Truck. The reports are moved via a secure, one-way tunnel. The truck strips off sensitive labels (Masking/PII) and ensures no one can intercept the intel while it's moving from the bank's property to your headquarters.

4. **The Digital Library (Snowflake)** — A State-of-the-Art Digital Archive. The armored truck drops the reports here. Unlike the old vault, this library is infinitely searchable and lightning-fast. However, the reports are still raw printouts of what was in the vault.

5. **The Head Librarian (dbt)** — The Intelligence Editor. The librarian takes those raw reports in Snowflake and cleans them up, highlighting the most important parts and creating "Department Folders" (Logic Views). For the Credit Dept, they highlight "Total Exposure." For the Risk Dept, they highlight "Past Due History." The data hasn't changed, but the perception is now tailored for the person reading it.

6. **The Analyst & File Clerk (IDP & RAG)** — The Research Team. While the vault (JH) has the numbers, the "Research Team" handles the external mail — PDFs, tax returns, and property appraisals. They scan these documents, pull out the "meat," and file them in the Digital Library (Snowflake) right next to the vault data.

7. **The Intelligence Officer (Dify / Agentic AI)** — The Senior Agent. The "Brain" that sits in the library, reading the vault reports (Snowflake), the clean summaries (dbt), and the scanned external files (RAG). When it's time to make a decision, the Agent connects the dots: "The vault says he has $50k, but the tax return I just read says his income dropped. My recommendation is: Caution."

8. **The Briefing Room (NLQ Interface)** — The Executive's Tablet. The Bank CEO doesn't need to know about the vault, the courier, or the librarian. They just ask the Agent a question in plain English: "Show me all loans at risk if interest rates rise." The Agent runs into the library, grabs the intel, and presents a clear answer.

## Context & Analysis
This is the foundational technical blueprint for the Dropsilo product. It defines the four pillars of the architecture: data ingestion (Snowflake + jXchange), semantic governance (dbt + RBAC), intelligent processing (Dify + IDP/RAG), and user access (NLQ). Each layer addresses a specific pain point in community banking: fragmented data, inconsistent metrics, manual document handling, and inaccessible analytics. The Jack Henry dependency is critical — jXchange is the middleware that bridges the core banking system to the data warehouse. The choice of specific tools (Snowflake, dbt, Dify) represents current best-of-breed selections that could evolve but the architectural pattern is stable.

## Cross-References
- Also relevant to: `1_centralized_database/methodology/` — data fabric methodology and semantic layering approach
- Relates to: `1_centralized_database/jack_henry/` — Jack Henry is the core system feeding this architecture via jXchange

## SOP Connections
> **Potential SOP**: Data Pipeline Integration Testing
> **Confidence**: Medium
> **Rationale**: As the architecture matures, there will be a repeatable process for validating that jXchange data flows correctly through Snowflake → dbt → Logic Views. This needs a standard testing procedure.
> **Status**: Flagged — awaiting user go-ahead

## Execution Connections
> **Potential script**: jXchange API connectivity validator
> **Inputs/Outputs**: Jack Henry credentials + endpoint config → connection status, available data objects, latency metrics
> **Status**: Flagged — awaiting SOP and user approval

## Skill Arc Connections
- **New arc suggested**: "Data Warehouse Architecture" — understanding Snowflake, dbt semantic layering, and Logic View design
- **New arc suggested**: "jXchange Integration" — mastering Jack Henry's middleware API for real-time data ingestion

## Recommended Tasks
1. [HIGH] Map the specific jXchange API endpoints needed for the initial data objects (customer, loan, deposit) — this determines what data is available on day one
2. [MED] Define the first 3-5 Logic Views (dbt models) that demonstrate the semantic layering value proposition to bank stakeholders
3. [MED] Research Dify's IDP capabilities for common bank document types (loan applications, financial statements, appraisals) to validate the orchestration layer

## Revision History
- 2026-02-12: Initial entry via research-relay
- 2026-02-12: Added Intelligence Agency analogy mapping each component to a narrative role
