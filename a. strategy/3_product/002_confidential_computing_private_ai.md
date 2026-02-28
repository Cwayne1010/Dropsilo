# Confidential Computing & Private AI for Banking

> **ID**: 002
> **Date added**: 2026-02-17
> **Source type**: text
> **Source**: Exploratory research conversation — Arcium, MPC, FHE, TEEs, private model inference for financial queries
> **Added by**: research-relay

## Key Takeaways
- Confidential computing enables AI inference on encrypted data — the model processes inputs without ever seeing them in plaintext
- Arcium is an MPC network on Solana; TEEs (AWS Nitro, Azure Confidential, on-prem SGX) are the proven near-term path for banks
- BFSI = 46% of the confidential computing market, but adoption is dominated by large banks / crypto custody — community banks at essentially zero
- Dropsilo's on-prem direction and confidential computing are complementary, not competing
- 5 concrete attachment points exist in the current stack that can be upgraded without re-architecting
- Strategic framing: Bet 1 (build compliance-ready architecture now) + Bet 2 (slot in FHE/MPC as regulation matures)
- Dark pools / private DeFi validate the market need: public data creates exploitable vulnerabilities — same principle applies to banking AI

## Full Content

### What Confidential Computing Is
Confidential computing enables computation on encrypted data — inputs, model weights, and outputs remain encrypted throughout processing. No single party (including the cloud provider or AI vendor) sees the raw data. Implemented via:
- **TEEs (Trusted Execution Environments)**: Hardware-based enclaves (AWS Nitro, Azure Confidential Computing, Intel SGX) that isolate computation at the chip level
- **MPC (Multi-Party Computation)**: Multiple nodes jointly compute a result — no single node sees the full dataset (Arcium's approach)
- **FHE (Fully Homomorphic Encryption)**: Computation directly on ciphertext — mathematically the strongest guarantee, but highest latency today
- **Differential Privacy**: Adds calibrated statistical noise to aggregate outputs, preventing reverse-engineering of individual records

### Arcium Specifically
- MPC network built on Solana
- Execution happens in MXEs (MPC eXecution Environments) — isolated enclaves
- Programs written in Arcis (Rust-based DSL)
- Mainnet Alpha launched late 2025
- Primary early use cases: private DeFi (dark pools, confidential AMMs), private AI inference
- For Dropsilo: Arcium is a medium-term strategic option, not a day-one requirement. On-prem Dify + TEE is the near-term path.

### Dark Pools & Private DeFi (Conceptual Validation)
- Dark pools: trading venues where orders are hidden until after execution — prevent front-running and price manipulation
- DeFi equivalent: public blockchains expose all order data in real time, creating MEV (Maximal Extractable Value) exploitation and liquidation hunting
- Solution: encrypted computation (MPC/FHE/TEE) maintains trustlessness while hiding sensitive inputs
- Banking parallel: public data in fragmented systems creates its own exploitability — consistent governed data with privacy controls is the analog

### Private Model Inference for Financial Queries
- NLQ interface queries against live loan portfolios, customer financials, KYC/AML records
- With standard cloud AI: provider technically processes queries, logs exist, admin access possible
- With TEE-wrapped inference: computation isolated in hardware enclave — provider cannot inspect runtime state
- With FHE: model never sees data in plaintext at any point (highest guarantee, not yet practical at scale)
- Community bank benefit: "your data is never decrypted outside your environment, not by us, not by our cloud providers"

### Current Market Adoption
- Confidential computing market: $9.3B in 2025, forecast $173B by 2031 (62% CAGR)
- BFSI = 46% of market — largest vertical
- Gartner: 50% of large organizations will adopt privacy-enhancing computation by 2026
- Named adopters: BNY Mellon, Standard Chartered, BBVA, JPMorgan, Revolut
- **Critical distinction**: almost all adoption is for digital asset custody / key management (MPC wallets) — NOT AI inference on loan data
- Community banks: essentially zero adoption. The technology reaches their world primarily through what Jack Henry bundles.

### 5 Attachment Points in the Dropsilo Stack

**Attachment 1 — Dify Inference Layer → TEE Wrapper**
- Today: Dify runs on-prem in a standard container
- Prep: keep Dify containerized, stateless, secrets pulled at runtime
- Near-term: wrap in AWS Nitro Enclave or on-prem SGX — no code changes, different runtime
- Future: swap standard model for FHE-compatible inference runtime inside the enclave

**Attachment 2 — dbt/NLQ Aggregate Outputs → Differential Privacy**
- Today: NLQ returns raw aggregate answers
- Attachment: post-process results through DP mechanism (Google DP library, OpenDP) before returning
- Design now: NLQ output as a pass-through pipeline — DP function is one slot in that pipeline
- Available today, regulatorily understood, no FHE/MPC required

**Attachment 3 — Cross-Bank Module → MPC Slot**
- Today: each bank's Dropsilo instance is isolated
- Interim: AWS Clean Rooms (TEE-based, regulatorily viable now) for peer benchmarking
- Future: replace with MPC module (Arcium-style) at the same API contract
- Design the benchmarking API contract now — banks' integration doesn't change when the privacy layer upgrades

**Attachment 4 — Customer-Managed Keys (CMK)**
- Today: Snowflake manages encryption keys
- Attachment: Snowflake Tri-Secret Secure — bank holds its own key in an HSM
- Result: "Dropsilo cannot access your data" — provably true, powerful trust argument
- Available today, regulatorily understood, should be designed in from the start

**Attachment 5 — Confidential Audit Logs**
- Today: audit logs accessible to Dropsilo admins
- Attachment: route logs through a TEE — cryptographically sealed, Dropsilo can prove integrity but cannot read contents
- Trust message: "Even we don't know what your CEO is asking about"

## Context & Analysis
This research establishes the strategic roadmap for Dropsilo's privacy architecture. The core insight is that confidential computing isn't a single decision — it's a spectrum of techniques deployable incrementally. The attachment point model means Dropsilo can ship a compliance-ready product today using standard and TEE-based techniques, while preserving architectural optionality for FHE/MPC as regulatory frameworks catch up.

The large bank adoption cycle (JPMorgan, BNY Mellon) validates the technology without Dropsilo having to pioneer regulatory acceptance. By the time Dropsilo is at scale with community banks, the compliance conversation around confidential computing will be substantially clearer.

The near-term competitive differentiation is not "we use MPC" — it's "your data never leaves your network during AI processing." That message works today with community bank boards and satisfies vendor risk requirements better than any cloud AI alternative.

## Cross-References
- Also relevant to: `1_centralized_database/003_banking_ai_compliance_stack.md` — compliance requirements that confidential computing addresses
- Also relevant to: `4_hardware_infrastructure/` — on-prem AI ops direction aligns with TEE attachment point
- Relates to: `3_product/001_dropsilo_technical_framework.md` — attachment points map to specific layers of the Dropsilo stack

## SOP Connections
> **Potential SOP**: Privacy Architecture Review for New Bank Onboarding
> **Confidence**: Low
> **Rationale**: As Dropsilo onboards banks, there will be a repeatable process for assessing which attachment points to activate (CMK, TEE inference, DP outputs) based on the bank's risk profile and examiner expectations
> **Status**: Flagged — awaiting user go-ahead

## Execution Connections
> **Potential script**: Differential Privacy post-processor for NLQ outputs
> **Inputs/Outputs**: Raw Snowflake aggregate query result + sensitivity parameter → DP-noised result with privacy budget tracking
> **Status**: Flagged — awaiting SOP and user approval

> **Potential script**: AWS Nitro Enclave deployment wrapper for Dify
> **Inputs/Outputs**: Dify container config → enclave deployment manifest + attestation verification
> **Status**: Flagged — awaiting SOP and user approval

## Skill Arc Connections
- **New arc suggested**: "Confidential Computing & Privacy Tech" — understanding TEE deployment, differential privacy, MPC fundamentals, and regulatory trajectory
- Starting level: Novice
- Unlocks: At Familiar — evaluate which attachment points to activate for a given bank. At Competent — deploy TEE-wrapped Dify and CMK on Snowflake. At Proficient — design cross-bank MPC benchmarking module.

## Recommended Tasks
1. [MED] Evaluate AWS Nitro Enclave feasibility for containerized Dify deployment — lowest-cost TEE attachment point available now, no regulatory uncertainty
2. [LOW] Monitor OCC and FFIEC publications for guidance on FHE/MPC — quarterly review to track when regulatory acceptance approaches
3. [LOW] Prototype differential privacy post-processor for one NLQ aggregate query — validates the pattern before architecture commitment

## Revision History
- 2026-02-17: Initial entry via research-relay
