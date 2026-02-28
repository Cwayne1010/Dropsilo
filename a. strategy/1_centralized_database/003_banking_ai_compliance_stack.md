# Banking AI Compliance Stack

> **ID**: 003
> **Date added**: 2026-02-17
> **Source type**: text
> **Source**: Exploratory research conversation — SR 11-7, GLBA, FFIEC, BSA/AML, compliance architecture for AI in community banking
> **Added by**: research-relay

## Key Takeaways
- SR 11-7 (Federal Reserve model risk management guidance) requires every AI model used in banking decisions to have a documented inventory, independent validation, and ongoing monitoring
- GLBA Safeguards Rule mandates encryption at rest/transit, access controls, and risk assessments — Snowflake handles most of this natively
- Encryption alone does not satisfy banking regulators — auditability, plaintext access for BSA/AML, vendor risk documentation, and key management governance are also required
- The dbt semantic layer is structurally well-suited to satisfy SR 11-7's model inventory requirement — documentation is a byproduct of building it correctly
- BSA/AML (SARs, OFAC screening) requires plaintext outputs at a defined compliance boundary — this cannot be fully encrypted end-to-end
- Most compliance work for Dropsilo is configuration, documentation, and logging — not re-architecture
- Solving the compliance stack is table stakes for community bank sales, not a differentiator by itself; but doing it visibly and credibly is a sales asset

## Full Content

### SR 11-7 — Model Risk Management
Federal Reserve supervisory letter (2011), jointly issued with OCC. The primary regulatory framework governing AI and quantitative models in banking. Not a law — supervisory guidance used by examiners as a benchmark.

**Three pillars:**
1. **Model Development, Implementation & Use** — every model documented with: purpose, inputs, assumptions, known limitations, appropriate use scope, named owner
2. **Model Validation** — independent validation (separate from the building team), testing conceptual soundness, data quality, benchmark performance, sensitivity analysis, documented and repeated periodically
3. **Governance, Policies & Controls** — model inventory (registry of all models in production), board/senior management accountability, ongoing monitoring for drift or degradation

**What counts as a "model" under SR 11-7:**
Broadly defined — any quantitative method that processes inputs into estimates used for decisions. For Dropsilo this captures:
- Dify AI workflows that score credit risk or extract document data
- IDP model extracting fields from tax returns and appraisals
- RAG system retrieving documents to inform credit recommendations
- NLQ outputs used to make business decisions
- dbt metric definitions used in executive risk dashboards

### GLBA — Gramm-Leach-Bliley Act (Safeguards Rule)
FTC Safeguards Rule (updated 2023) explicitly requires:
- Encryption for customer information in transit and at rest
- Multi-factor authentication for anyone accessing customer information systems
- Designated qualified individual overseeing the information security program
- Annual risk assessment
- Incident response plan

**Snowflake handles most encryption natively.** Compliance work is primarily documentation and configuration (data map of what's masked/encrypted, encryption key governance).

### FFIEC — Federal Financial Institutions Examination Council
Examination framework covering:
- Security controls (governance, policies, independent testing)
- Vendor risk management — **encryption does not eliminate this.** Even if data is encrypted, banks must: conduct due diligence on vendors, maintain contracts with right-to-audit clauses, document in third-party risk management program, ensure vendor has certifications.
- Business continuity
- On-site reviews of independent security testing

### BSA/AML — Bank Secrecy Act / Anti-Money Laundering
Critical boundary: **certain outputs cannot be fully encrypted.**
- Suspicious Activity Reports (SARs) must contain readable customer data
- OFAC sanctions screening requires matching against readable names/addresses
- FinCEN can subpoena records — encrypted outputs don't satisfy a subpoena

**Design implication**: AI processes privately inside the stack, but final compliance decision records must be written in readable plaintext to a compliance-specific store. This is the "compliance output boundary" — a defined point where encrypted processing produces a readable, auditable record.

### Key Management Compliance
Advanced encryption creates its own audit surface:
- Who holds the keys? Key custodian documentation required
- How are keys rotated? Documented procedures required
- Recovery plan if keys are lost
- Law enforcement / regulatory escrow considerations
- Snowflake Tri-Secret Secure (customer-managed keys) addresses this — bank holds its own HSM key

### Legal Holds and E-Discovery
Courts and regulators can subpoena data. Discovery may require producing data the AI processed in readable form. A defined decryption process must exist, be documented, and be auditable.

### Layer-by-Layer Compliance Map for Dropsilo

**jXchange (Translator)**
- Every API call gets structured audit log: timestamp, data object, requesting process
- Chain of custody origin — regulators will trace data provenance back to here
- TLS in transit: enforce explicitly in ingestion config

**Ingestion Pipeline (Armored Truck)**
- Document which fields are masked, pseudonymized, or tokenized — this is the GLBA data map
- Masking logic versioned and auditable (what masking applied when)
- Field-level lineage: every Snowflake column traces to its jXchange source

**Snowflake (Digital Library)**
- AES-256 at rest: native, already on
- Query history / access logs: route to compliance store (every query, who, when)
- Dynamic Data Masking: additional PII protection at query time by role
- Time Travel (90 days): legal hold / e-discovery point-in-time recovery
- Data residency (region lock): US regions for state-level compliance
- Column-level security: belt-and-suspenders below dbt layer

**dbt (Head Librarian)**
- dbt docs = model inventory. Every metric (Total Exposure, Customer Health, Past Due History) documented with: business definition, source fields, calculation logic, owner
- dbt tests = data quality control records (audit-ready)
- Git version control on dbt models = change log (who changed what, when, why)
- This is where SR 11-7 compliance gets built in — documentation is a byproduct of building it correctly

**Dify + IDP/RAG (Intelligence Officer)**
- Highest-risk compliance layer — AI making recommendations on loan files
- Model cards for each Dify workflow: inputs, outputs, limitations, validation procedure
- IDP extraction logged: document ID → extracted fields → confidence scores → timestamp
- RAG retrieval logged: query → documents retrieved → documents used in response
- AI recommendation logged: inputs considered, output produced, human reviewer
- BSA/AML boundary: AML/KYC outputs produce readable plaintext records for SAR filing
- Vendor risk: on-prem Dify = vendor provides software, not data processing — cleaner risk profile

**NLQ Interface (Briefing Room)**
- Every query logged: user, query text, timestamp, data objects accessed, output returned
- RBAC from dbt propagates here — NLQ cannot return data the user's role can't see in Snowflake
- High-sensitivity output flagging for secondary logging

### What's Already There vs. What Needs Adding

| Component | Already Designed | Needs to Be Added |
|---|---|---|
| PII masking at ingestion | Yes | Documentation of what's masked and why |
| RBAC in dbt | Yes | Full model inventory docs (SR 11-7) |
| Snowflake encryption | Yes (native) | Query logging routed to compliance store |
| IDP document processing | Yes | Extraction audit logs, model cards |
| On-prem inference | In direction | Formalized vendor risk posture |
| NLQ interface | Yes | Query logging, RBAC propagation |
| Readable compliance outputs | Not yet | Explicit BSA/AML output boundary |

## Context & Analysis
Solving the banking AI compliance stack is not optional — it's the cost of entry for selling to community banks. The good news: Dropsilo's architecture is already well-positioned. The compliance work is primarily documentation, logging, and configuration layered on top of existing design, not re-architecture.

The strategic opportunity: being the vendor that walks into a bank with a pre-documented SR 11-7 model inventory, a GLBA data map, and a clear BSA/AML output boundary — before the examiner asks. That turns a compliance burden into a credibility signal. No community bank AI vendor has yet packaged this as a feature.

Encryption alone is not compliance. The correct framing: encrypted computation + auditable logs + regulatory-compliant key management + selective disclosure for examiners + model risk documentation + BSA/AML plaintext boundary = a defensible compliance posture.

## Cross-References
- Also relevant to: `3_product/002_confidential_computing_private_ai.md` — encryption and TEE techniques that address parts of this compliance stack
- Also relevant to: `3_product/001_dropsilo_technical_framework.md` — the architecture this compliance stack maps to

## SOP Connections
> **Potential SOP**: Bank Onboarding Compliance Checklist
> **Confidence**: High
> **Rationale**: Every community bank Dropsilo onboards will need the same compliance artifacts produced: GLBA data map, SR 11-7 model inventory, vendor risk assessment, BSA/AML output boundary documentation. This is highly repeatable.
> **Status**: Flagged — awaiting user go-ahead

> **Potential SOP**: SR 11-7 Model Validation Procedure
> **Confidence**: Medium
> **Rationale**: Independent validation of Dify workflows and dbt metrics will be required by bank examiners. Needs a repeatable testing and documentation process.
> **Status**: Flagged — awaiting user go-ahead

## Execution Connections
> **Potential script**: Compliance audit log exporter
> **Inputs/Outputs**: Snowflake query history + Dify execution logs → structured compliance report (readable plaintext, formatted for examiner review)
> **Status**: Flagged — awaiting SOP and user approval

## Skill Arc Connections
- **New arc suggested**: "Banking AI Regulatory Compliance" — understanding SR 11-7, GLBA, FFIEC, BSA/AML, and how they map to Dropsilo's architecture
- Starting level: Novice (this conversation is the first research on this arc)
- Unlocks: At Familiar — draft SR 11-7 model inventory for Dropsilo. At Competent — produce full compliance documentation package for bank onboarding. At Proficient — advise banks on their own model risk posture using Dropsilo data.

## Recommended Tasks
1. [HIGH] Map SR 11-7 model inventory requirements to every Dify workflow and dbt metric in the current Dropsilo architecture — determines the compliance gap before first bank pilot
2. [MED] Draft the BSA/AML output boundary design — define exactly where encrypted AI processing produces readable plaintext compliance records in the Dropsilo pipeline
3. [MED] Identify which Snowflake features need to be activated for FFIEC compliance (query history routing, Dynamic Data Masking, Time Travel configuration)

## Revision History
- 2026-02-17: Initial entry via research-relay
