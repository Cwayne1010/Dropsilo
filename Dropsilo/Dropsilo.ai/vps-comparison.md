# VPS Provider Comparison for Bandwidth Phase 1

## Quick Comparison

| Provider | Relevant Tier | Monthly Cost | What You Get | Best For |
|---|---|---|---|---|
| **Hostinger VPS** | KVM 4-8 | $16-30 | 16-32GB RAM, decent CPU, budget pricing | Website hosting + light automation |
| **Hetzner** | CPX31-41 | $15-30 | Same specs, better network, EU data centers, respected infrastructure | Best value for serious workloads |
| **DigitalOcean** | Droplet + App Platform | $24-48 | Solid performance, great docs, managed databases available | Developer-friendly, good ecosystem |
| **Contabo** | VPS M-L | $12-26 | Most RAM per dollar (30-60GB), but inconsistent performance | Budget maximizer if you need raw specs |
| **Linode (Akamai)** | Dedicated 8-16GB | $30-60 | Dedicated CPU cores (no noisy neighbors), predictable performance | Production n8n workflows that need reliability |

## The Key Tradeoff

Hostinger is optimized for **web hosting customers** — great cPanel experience, easy WordPress migrations, solid support for that use case. But running n8n workflows, PostgreSQL, and eventually LLM inference is an **infrastructure workload**, which is a different game.

Hetzner and DigitalOcean are built for developers running production services. Better network performance, more transparent resource allocation, and communities full of people doing exactly what you're doing.

## Recommendation

**Hetzner** gives the best cost-to-capability ratio for a split workload. More predictable performance than Hostinger at comparable pricing, EU data centers add a minor data sovereignty talking point, and they're widely used in the n8n and self-hosting community — meaning more guides and troubleshooting resources.

If you value **managed simplicity** and don't mind paying a bit more, **DigitalOcean** is the safest choice. Their managed PostgreSQL add-on alone could save headaches.

Either way, Hostinger can still be used for pure website hosting if the migration path is easier there, with automation infrastructure running separately. Keeping client-facing sites isolated from the workflow engine is better architecture anyway.
