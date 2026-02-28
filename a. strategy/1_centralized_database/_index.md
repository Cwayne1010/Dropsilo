# Centralized Database — Research Index

> Last updated: 2026-02-17

## Summary
Research covers the core banking platform landscape (entry 001), cross-references to Dropsilo's technical framework (entry 002 xref), a cross-reference to confidential computing (entry 003 xref), and the full banking AI compliance stack (entry 004). Entry 005 (xref) extends the compliance picture with the operational implementation: enterprise LLM deployment via AWS Bedrock, per-bank Snowflake role scoping, namespaced Cortex Search isolation, and Tri-Secret Secure as the hardware-enforced data sovereignty guarantee. The compliance entry is the most actionable: SR 11-7 model risk management, GLBA encryption requirements, FFIEC vendor risk, and BSA/AML plaintext output boundaries all map directly to Dropsilo's architecture. Most compliance work is configuration and documentation, not re-architecture — the Bank Onboarding Compliance Checklist SOP is now high-confidence and ready for drafting.

## Research Entries

| ID | Date | Title | Source Type | SOP Flag |
|----|------|-------|-------------|----------|
| 001 | 2026-02-08 | Core Banking Platforms | text | — |
| 002 | 2026-02-12 | Dropsilo Technical Framework | xref | — |
| 003 | 2026-02-17 | Confidential Computing & Private AI for Banking | xref | — |
| 004 | 2026-02-17 | Banking AI Compliance Stack | text | Bank Onboarding Compliance Checklist (High), SR 11-7 Model Validation Procedure (Medium) |
| 005 | 2026-02-27 | Unified Multi-Modal Data Architecture & Enterprise LLM Isolation | xref | — |

## Cross-References
- `3_product/001_dropsilo_technical_framework.md` — the architecture that this compliance stack maps to
- `3_product/002_confidential_computing_private_ai.md` — encryption/TEE techniques that address parts of the compliance stack
- `1_centralized_database/jack_henry_index.md` — Jack Henry specifics
- `1_centralized_database/methodology_index.md` — data fabric methodology

## SOP Candidates
- [x] Bank Onboarding Compliance Checklist — **DRAFTED** → `b. directives/Dropsilo/bank_onboarding_compliance_checklist.md` (2026-02-27)
- [ ] SR 11-7 Model Validation Procedure — independent validation of Dify workflows and dbt metrics (Medium confidence)

## Execution Candidates
- Compliance audit log exporter — Snowflake query history + Dify execution logs → structured examiner-ready compliance report

## Task Recommendations

| Task | Priority | Source Entry | Status |
|------|----------|-------------|--------|
| Map SR 11-7 model inventory requirements to every Dify workflow and dbt metric in current Dropsilo architecture | HIGH | 004 | recommended |
| Draft the BSA/AML output boundary design — where encrypted AI processing produces readable plaintext compliance records | MED | 004 | recommended |
| Identify which Snowflake features to activate for FFIEC compliance (query history, Dynamic Data Masking, Time Travel) | MED | 004 | recommended |
| Make AWS Bedrock deployment decision — satisfies FFIEC vendor risk and GLBA data residency in one move | HIGH | 005 | recommended |
| Design per-bank Snowflake role + Dify workspace provisioning procedure — operational foundation of compliance onboarding | HIGH | 005 | recommended |

## Notes
- SR 11-7 is the most immediate compliance requirement — any AI used in credit decisions requires a model inventory and validation procedure
- The dbt semantic layer is structurally well-suited to satisfy SR 11-7 model inventory — documentation is a byproduct of building it correctly
- BSA/AML is the one layer where data cannot be fully encrypted — a plaintext compliance output boundary must be explicitly designed into the Dify layer
