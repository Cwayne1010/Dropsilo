# Jack Henry Core Banking Platforms

> **ID**: 001
> **Date added**: 2026-02-12
> **Source type**: text
> **Source**: User-provided platform summary
> **Added by**: research-relay

## Key Takeaways
- Jack Henry offers 3 distinct core banking platforms targeting different bank sizes and operational styles
- SilverLake targets mid-to-large banks: IBM i (AS/400) based, highly customizable, commercial lending focus
- CIF 20/20 targets community banks: parameter-driven configuration, streamlined for smaller retail operations
- Core Director targets small/growth banks: Windows-based, point-and-click interface, ease-of-use priority
- Platform choice determines the jXchange API surface area and integration complexity for Dropsilo
- SilverLake is the most likely initial target given Dropsilo's commercial lending focus

## Full Content

### Platform Comparison

| Platform | Target Market | Architecture | Key Characteristics |
|----------|--------------|--------------|---------------------|
| **SilverLake** | Mid-to-Large Banks | IBM i (AS/400) | Highly customizable, commercial focus |
| **CIF 20/20** | Community Banks | Parameter-driven | Streamlined for smaller retail operations |
| **Core Director** | Small/Growth Banks | Windows-based | Point-and-click interface, ease of use |

**SilverLake** — The flagship platform for larger institutions. Built on IBM's AS/400 (now IBM i), it offers deep customization for complex commercial banking operations. The AS/400 architecture means data access patterns and API behaviors will differ from the Windows-based systems.

**CIF 20/20** — Designed for community banks that need reliable core processing without the complexity of SilverLake. Parameter-driven means configuration over customization — less flexible but faster to deploy and maintain.

**Core Director** — The entry-level platform for small and growing banks. Windows-based with a modern point-and-click interface. Likely the simplest jXchange integration path but may have a smaller feature surface.

## Context & Analysis
Understanding the Jack Henry platform landscape is essential for Dropsilo's go-to-market strategy. Each platform exposes different data objects and APIs through jXchange, meaning the integration layer may need platform-specific adapters. SilverLake's AS/400 heritage means data structures may follow older conventions (EBCDIC encoding, fixed-width fields) that require careful handling in the ingestion pipeline. The platform a target bank runs determines not just the technical integration but also the bank's sophistication level and pain points — SilverLake banks likely have more complex data needs, while Core Director banks may value simplicity and speed of deployment. Dropsilo should decide which platform to target first and build the integration path accordingly.

## Cross-References
- Relates to: `3_product/centralized_database_interfaces/001_dropsilo_technical_framework.md` — Jack Henry is the "Vault" that feeds the entire Dropsilo architecture via jXchange

## SOP Connections
> **Potential SOP**: Jack Henry Platform Discovery Checklist
> **Confidence**: High
> **Rationale**: When engaging a new bank prospect, Dropsilo needs a repeatable process to identify which JH platform they run, what jXchange version/endpoints are available, and what data objects can be accessed. This is a sales engineering prerequisite.
> **Status**: Flagged — awaiting user go-ahead

## Execution Connections
> **Potential script**: JH platform detection / jXchange endpoint inventory
> **Inputs/Outputs**: Bank's jXchange connection details → platform type, available API endpoints, data object catalog
> **Status**: Flagged — awaiting SOP and user approval

## Skill Arc Connections
- **New arc suggested**: "Jack Henry Ecosystem" — understanding the three platforms, jXchange API patterns, and platform-specific data structures

## Recommended Tasks
1. [HIGH] Determine which Jack Henry platform to target first for the MVP integration — this gates all downstream technical decisions
2. [MED] Research jXchange API documentation for platform-specific differences in available endpoints and data objects
3. [LOW] Build a prospect qualification matrix mapping bank size/type to likely JH platform for sales targeting

## Revision History
- 2026-02-12: Initial entry via research-relay
