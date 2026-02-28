# Equipment — Research Index

> Last updated: 2026-02-08

## Summary
Research in this folder covers the infrastructure and team requirements for running AI/LLM platforms on-premises vs. cloud. The primary finding so far is that a two-person startup should start cloud-first and phase into on-prem only when regulatory requirements demand it, with managed services filling the gap for GPU ops, security, and compliance.

## Research Entries

| ID | Date | Title | Source Type | SOP Flag |
|----|------|-------|-------------|----------|
| 001 | 2026-02-08 | Building a Dedicated Ops Team for an On-Prem AI/LLM Platform | text | Infrastructure Decision Matrix (Medium) |

## Cross-References
- `4_hardware_infrastructure/capex_vs_opex/` — Cost comparison data (cloud vs on-prem vs hybrid)
- `2_business_model/` — Lean ops team structure and startup feasibility

## SOP Candidates
- [ ] Infrastructure Decision Matrix — repeatable evaluation framework for cloud-vs-on-prem per client (Medium confidence)

## Execution Candidates
- [ ] GPU Cost Calculator — break-even analysis tool comparing cloud GPU pricing vs on-prem hardware costs

## Task Recommendations

| Task | Priority | Source Entry | Status |
|------|----------|-------------|--------|
| Run GPU cost comparison for target use cases (fraud, KYC, credit scoring) across cloud providers vs leased rack | HIGH | 001 | recommended |
| Identify 2-3 managed GPU services vendors and get quotes | MED | 001 | recommended |
| Draft compliance requirements checklist for target banking jurisdictions | LOW | 001 | recommended |

## Notes
- Both hardware subfolders (equipment, capex_vs_opex) were empty before this entry — this is the foundational research piece for infrastructure planning.
