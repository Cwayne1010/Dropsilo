# Building a Dedicated Ops Team for an On-Prem AI/LLM Platform

> **ID**: 001
> **Date added**: 2026-02-08
> **Source type**: text
> **Source**: User-provided research document
> **Added by**: research-relay

## Key Takeaways
- Running on-prem AI requires 7 distinct roles: Systems/Infra Engineer, GPU/HPC Engineer, DevOps, Security/Compliance, Data/Model Engineer, Business Liaison, and Support/Incident Response
- A two-person team can cover business, light DevOps, and ML — but GPU ops, security/compliance, and data-center infra typically need a third party or contractor
- Four lean ops approaches ranked by feasibility: managed GPU rack vendor ($1-3k/mo), cloud/hybrid ($0.10-0.20/GPU-hr), outsourced ops team ($10-25k/mo), or full DIY (not scalable)
- Cloud-only or hybrid is the most pragmatic starting path when no existing data center exists — start in days vs months
- Compliance (PCI-DSS, GDPR, data residency) is the primary driver for on-prem; latency and cost predictability are secondary factors
- GPU/HPC engineering is the hardest role to cover with a small team — requires deep CUDA, NCCL, TensorRT experience
- Phased approach (cloud first → partial on-prem migration later) is what most banks end up doing

## Full Content

### Roles Required for On-Prem AI Ops

| Role | Primary Responsibilities | Time Commitment | Two-Person Feasible? |
|------|-------------------------|-----------------|---------------------|
| Systems / Infrastructure Engineer | Servers, GPU racks, storage, networking, power & cooling, OS patching | 30-40 h/wk setup → 10-15 h/mo maintenance | Yes, if you own a data center |
| GPU / HPC Engineer | GPU utilization tuning, CUDA/cuDNN/NCCL/TensorRT management, GPU lifecycle | 20-30 h/wk peaks; 5-10 h/wk inference-only | Hard without deep GPU experience |
| DevOps / CI-CD Engineer | Docker/Singularity images, inference pipelines, Helm/Terraform, auto-scaling | 20-30 h/wk rollout; 5-10 h/wk routine | Yes, if one person handles small K8s cluster |
| Security & Compliance Officer | Encryption, key management (HSM/Vault), audit trails, SIEM, regulatory alignment | 10-15 h/wk monitoring; 5-10 h/mo audits | Hard — outsource compliance consultant |
| Data & Model Engineer | Train/fine-tune LLMs, model drift monitoring, A/B testing, data pipelines | 20-25 h/wk during model lifecycle | Yes, if comfortable with ML workflows |
| Business / Product Liaison | Translate bank requirements to AI tasks, dashboards, alerts for risk officers | 10-15 h/wk | Yes |
| Support & Incident Response | Ops tickets, incident playbooks, root-cause analysis, post-mortems | 5-10 h/wk, spikes during outages | Hard without clear vendor escalation path |

### Lean Ops Approaches

| Approach | What You Do | Cost/Time |
|----------|------------|-----------|
| Buy 2-4 GPU rack + managed services vendor | Own rack, basic OS + containers, vendor handles power/cooling/security/GPU lifecycle | 3-6 mo prep + $1-3k/mo vendor |
| Cloud-only or hybrid with on-prem edge | Cloud for training/large inference, small edge GPU for ultra-low-latency | $0.10-0.20/GPU-hr cloud; $1.5-3k upfront on-prem |
| Outsource ops team (part-time) | Retain 3-4 people on monthly retainer for full ops coverage | $10-25k/mo |
| Full DIY | Single high-end workstation (RTX 4090), run everything yourself | <$3k initial; 5-10 h/wk; not scalable |

### Cloud vs On-Prem Decision Factors

| Factor | On-Prem | Cloud |
|--------|---------|-------|
| Regulatory (data residency) | Full control with audit evidence | Region-specific compliance possible |
| Latency | Sub-ms | Sub-10ms with edge/private-link |
| Scalability | Hardware-limited | Elastic, spin up GPU nodes in minutes |
| Hardware currency | Annual/biennial refresh needed | Newest GPUs (H100, L4) available |
| Cost predictability | CAPEX amortized 5-7 yrs | OPEX spikes with usage |
| Team expertise needed | Deep infra/ops knowledge | Focus on ML & product |

### Quick Checklist for Two-Person Startup
1. Define scope — use cases, concurrent inference requests
2. Do the math — GPU hours/mo vs $/GPU-hr, CAPEX vs OPEX
3. Assess compliance — PCI-DSS, GDPR, local banking law, mandatory in-house requirement?
4. Choose ops model — full on-prem, cloud-only, or hybrid
5. Plan for growth — run-books for adding GPU nodes, scaling K8s
6. Build or buy — existing data center? Lease vs buy GPU rack? Managed services for first 6-12 months?
7. Iterate — start small, add monitoring/logging/security gradually

## Context & Analysis
This research is directly relevant to Dropsilo's infrastructure planning for serving AI/LLM to banking clients. The key insight is that a two-person team should NOT attempt full on-prem from day one. The phased approach (cloud → hybrid → selective on-prem) reduces upfront cost and team burden while maintaining a path to full regulatory compliance when required. The $10-25k/mo outsourced ops team option is worth evaluating against cloud costs at scale — there's likely a crossover point where bringing ops in-house becomes economical.

## Cross-References
- Also filed in: `4_hardware_infrastructure/capex_vs_opex/` (xref)
- Also filed in: `2_business_model/` (xref)
- Relates to: Equipment decisions depend on ops model choice; CapEx/OpEx analysis is central to the cloud-vs-on-prem decision

## SOP Connections
> **Potential SOP**: Infrastructure Decision Matrix
> **Confidence**: Medium
> **Rationale**: The cloud-vs-on-prem decision framework could become a repeatable evaluation process applied to each new banking client's requirements
> **Status**: Flagged — awaiting user go-ahead

## Execution Connections
> **Potential script**: GPU Cost Calculator
> **Inputs/Outputs**: Takes GPU hours/month, cloud provider rates, on-prem hardware costs → outputs break-even analysis and recommendation
> **Status**: Flagged — awaiting SOP and user approval

## Skill Arc Connections
- **New arc suggested**: "On-Prem AI Infrastructure" — understanding the full stack from GPU hardware to deployment pipelines
- **New arc suggested**: "Cloud/Hybrid AI Deployment" — mastering cloud GPU provisioning, cost optimization, and hybrid architectures

## Recommended Tasks
1. [HIGH] Run a cost comparison: estimate GPU hours needed for target use cases (fraud, KYC, credit scoring) and compare cloud pricing (AWS/GCP/Azure) vs leased GPU rack + managed services vendor
2. [MED] Identify 2-3 managed GPU services vendors and get quotes for a small (2-4 GPU) rack with full ops support
3. [LOW] Draft a compliance requirements checklist specific to target banking clients' jurisdictions to determine if on-prem is actually mandatory

## Revision History
- 2026-02-08: Initial entry via research-relay
