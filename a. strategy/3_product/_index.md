# Centralized Database Interfaces — Research Index

> Last updated: 2026-02-17

## Summary
This folder covers the technical architecture and strategic positioning of Dropsilo's core product. The foundational blueprint (entry 001) defines a four-layer pipeline: Jack Henry → jXchange → Snowflake → dbt → Dify → NLQ. Entry 002 maps the confidential computing and privacy tech landscape onto this architecture — identifying 5 attachment points (TEE inference, differential privacy, cross-bank MPC, CMK, confidential audit logs) that can be activated incrementally as regulatory frameworks mature. Entry 003 maps banking AI compliance requirements (SR 11-7, GLBA, FFIEC, BSA/AML) layer-by-layer to the Dropsilo stack. Entry 004 (xref) captures the competitive landscape finding: Dropsilo occupies genuine whitespace as the only purpose-built Jack Henry-native + data fabric + AI + NLQ product for community banks. Entry 005 resolves the multi-modal data architecture question (Snowflake Cortex Search as the RAG layer, unifying structured + unstructured in one governed platform) and establishes the enterprise LLM isolation model — AWS Bedrock, per-bank Dify workspace + Snowflake role scoping, namespaced Cortex Search, and Tri-Secret Secure as the four-layer isolation stack.

## Research Entries

| ID | Date | Title | Source Type | SOP Flag |
|----|------|-------|-------------|----------|
| 001 | 2026-02-12 | Dropsilo Technical Framework | text | Data Pipeline Integration Testing (Medium) |
| 002 | 2026-02-17 | Confidential Computing & Private AI for Banking | text | Privacy Architecture Review (Low) |
| 003 | 2026-02-17 | Banking AI Compliance Stack | xref | — |
| 004 | 2026-02-17 | Competitive Landscape — Community Bank AI | xref | — |
| 005 | 2026-02-27 | Unified Multi-Modal Data Architecture & Enterprise LLM Isolation | text | Multi-Tenant Bank Provisioning (High), Document Ingestion Pipeline (Medium), Bank Onboarding Compliance Checklist upgraded to High |

## Cross-References
- `1_centralized_database/methodology/` — data fabric methodology underpinning the architecture
- `1_centralized_database/jack_henry/` — the core banking system feeding the pipeline
- `1_centralized_database/003_banking_ai_compliance_stack.md` — full compliance entry (003 here is xref)
- `2_business_model/002_competitive_landscape_community_bank_ai.md` — full competitive entry (004 here is xref)
- `4_hardware_infrastructure/` — on-prem AI ops direction aligns with TEE attachment point

## SOP Candidates
- [ ] Data Pipeline Integration Testing — validate jXchange → Snowflake → dbt → Logic Views flow (Medium confidence)
- [ ] Privacy Architecture Review for New Bank Onboarding — assess which attachment points to activate per bank risk profile (Low confidence)
- [ ] Multi-Tenant Bank Provisioning Procedure — repeatable setup for each new bank client: Snowflake DB + role, Dify workspace, Cortex Search namespace, Tri-Secret Secure, CloudTrail logging (High confidence)
- [ ] Document Ingestion Pipeline Setup — ingest PDFs and unstructured docs into Snowflake via Dify IDP, index in Cortex Search (Medium confidence)
- [x] Bank Onboarding Compliance Checklist — **DRAFTED** → `b. directives/Dropsilo/bank_onboarding_compliance_checklist.md` (2026-02-27)

## Execution Candidates
- jXchange API connectivity validator — test connection, enumerate data objects, measure latency
- Differential Privacy post-processor for NLQ outputs — add DP noise to aggregate query results
- AWS Nitro Enclave deployment wrapper for Dify — containerized TEE deployment manifest
- Bank provisioning automation — inputs: bank_id, name → outputs: Snowflake DB + role created, Dify workspace provisioned, Cortex Search namespace initialized
- Multi-tenant isolation validator — test suite confirming cross-bank credential and RAG isolation for a given bank_id

## Task Recommendations

| Task | Priority | Source Entry | Status |
|------|----------|-------------|--------|
| Map jXchange API endpoints for initial data objects (customer, loan, deposit) | HIGH | 001 | recommended |
| Define first 3-5 Logic Views (dbt models) for stakeholder demos | MED | 001 | recommended |
| Research Dify IDP capabilities for bank document types | MED | 001 | recommended |
| Evaluate AWS Nitro Enclave feasibility for containerized Dify deployment | MED | 002 | recommended |
| Monitor OCC/FFIEC publications for FHE/MPC regulatory guidance (quarterly) | LOW | 002 | recommended |
| Make AWS Bedrock deployment decision — model tier, AWS account structure, lock in LLM deployment pattern | HIGH | 005 | recommended |
| Design per-bank provisioning checklist — enumerate every setup step for new bank client onboarding | HIGH | 005 | recommended |
| Prototype two-tool Dify workflow (SQL + Cortex Search in parallel) against mock bank data | MED | 005 | recommended |

## Notes
- The Intelligence Agency analogy (in entry 001) is a powerful sales/communication tool — consider using it in pitch materials
- "Speed vs. Truth" is the core positioning vs. Covecta — they automate on fragmented data, Dropsilo unifies the foundation first
- Bet 1 (compliance-ready architecture now) + Bet 2 (FHE/MPC slots in when regulation matures) is the strategic framing for privacy tech

## Architecture Decision — 2026-02-20: Tier 1 / Tier 2 Parallel Track

Two ingestion tiers now in parallel development:

**Tier 1 — Flat File / Canonical Schema (MVP path)**
- Dropsilo defines a standard flat file schema (Dropsilo Data Spec v0)
- Any core banking system maps to the spec and delivers via SFTP
- Works with Jack Henry, Fiserv, FIS, or any core — platform-agnostic
- Nightly batch delivery — sufficient for analytics, NLQ, executive reporting
- Directive: `b. directives/Dropsilo/dropsilo_data_spec_v0.md`
- Setup Guides:
  - `b. directives/Dropsilo/fiserv_premier_ba_setup_guide.md`
  - `b. directives/Dropsilo/jack_henry_setup_guide.md`
  - `b. directives/Dropsilo/fis_setup_guide.md`
- **Active pilot**: Fiserv Premier bank — exports via BA (Business Analytics) module
- Target: onboard pilot bank and validate full dbt → Dify → NLQ stack on real data

**Tier 2 — API Integration / jXchange (real-time, post-MVP)**
- Jack Henry jXchange integration as originally designed
- Real-time data freshness, fully automated, no manual export step
- Positioned as the premium/upgrade tier from Tier 1
- Development continues in parallel — does not block MVP

**Strategic implication**: Tier 1 widens TAM from Jack Henry-only to all community banks immediately. The ingestion layer becomes a specification problem (publish the schema, bank IT maps to it) rather than a platform-specific engineering problem for the MVP. Tier 2 becomes the automation upgrade sold after initial value is proven.
