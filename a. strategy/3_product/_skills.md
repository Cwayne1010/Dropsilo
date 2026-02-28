# Skill Arcs — Centralized Database Interfaces

## Active Learning Paths

### Data Warehouse Architecture
- **Goal**: Deep understanding of Snowflake capabilities, dbt semantic layering patterns, and Logic View design for multi-department RBAC access
- **Current level**: Familiar
- **Research entries**: 001, 005
- **Next step**: Prototype Cortex Search indexing for a bank document type (loan application or tax return) alongside structured dbt models; validate the unified query pattern
- **Unlocks**: At Familiar (current) — SOP for Logic View design patterns. At Competent — execution scripts for automated dbt model generation from core data schemas, plus Cortex Search namespace provisioning per bank.

### jXchange Integration
- **Goal**: Mastery of Jack Henry's middleware API — authentication, available endpoints per platform, data object mapping, real-time vs batch patterns
- **Current level**: Novice
- **Research entries**: 001
- **Next step**: Obtain jXchange API documentation and map available endpoints for customer, loan, and deposit objects
- **Unlocks**: At Familiar level — SOP for bank integration onboarding. At Competent level — execution scripts for jXchange connectivity testing and data object inventory.

### Confidential Computing & Privacy Tech
- **Goal**: Understand TEE deployment, differential privacy, MPC fundamentals, FHE trajectory, and regulatory timeline — enough to activate the right attachment points for a given bank and advise on privacy architecture
- **Current level**: Novice
- **Research entries**: 002, 005
- **Next step**: Evaluate AWS Nitro Enclave feasibility for containerized Dify deployment; prototype a differential privacy post-processor for one NLQ aggregate query
- **Unlocks**: At Familiar — evaluate and recommend which attachment points to activate per bank. At Competent — deploy TEE-wrapped Dify and CMK on Snowflake. At Proficient — design cross-bank MPC benchmarking module.

### Banking AI Regulatory Compliance
- **Goal**: Deep working knowledge of SR 11-7, GLBA, FFIEC, and BSA/AML as they apply to AI systems in community banking — enough to produce a full compliance documentation package for bank onboarding without external legal counsel
- **Current level**: Familiar
- **Research entries**: 003 (xref → 1_centralized_database/003_banking_ai_compliance_stack.md), 005
- **Next step**: Map SR 11-7 model inventory to every Dify workflow and dbt metric; draft BSA/AML output boundary design; document AWS Bedrock deployment config as FFIEC vendor risk artifact
- **Unlocks**: At Familiar (current) — draft SR 11-7 model inventory for Dropsilo. At Competent — produce full compliance documentation package for bank onboarding. At Proficient — advise bank on their own model risk posture using Dropsilo data.

### Multi-Tenant SaaS Architecture
- **Goal**: Ability to provision a new bank client end-to-end (Snowflake DB + role, Dify workspace, Cortex Search namespace, Bedrock config) reliably, and verify isolation programmatically via automated test suite
- **Current level**: Novice
- **Research entries**: 005
- **Next step**: Design the per-bank provisioning checklist — enumerate every setup step, then build the isolation validator script
- **Unlocks**: At Familiar — execute manual provisioning for a new bank client. At Competent — fully automated provisioning script with isolation verification. At Proficient — self-service bank onboarding with automated compliance artifact generation.

## Completed Arcs
(Moved here when proficiency is reached)
