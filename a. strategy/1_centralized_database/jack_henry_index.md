# Jack Henry — Research Index

> Last updated: 2026-02-12

## Summary
Jack Henry offers three distinct core banking platforms serving different bank segments. SilverLake (IBM i/AS400, mid-to-large banks, highly customizable commercial focus), CIF 20/20 (parameter-driven, community banks, retail focus), and Core Director (Windows-based, small/growth banks, ease of use). Understanding the platform landscape is critical for Dropsilo's integration strategy — each platform exposes different data objects and API behaviors through jXchange, and the target platform determines technical complexity, go-to-market positioning, and prospect qualification.

## Research Entries

| ID | Date | Title | Source Type | SOP Flag |
|----|------|-------|-------------|----------|
| 001 | 2026-02-12 | Jack Henry Core Banking Platforms | text | JH Platform Discovery Checklist (High) |

## Cross-References
- `3_product/centralized_database_interfaces/001_dropsilo_technical_framework.md` — Jack Henry is the source system feeding the entire Dropsilo architecture

## SOP Candidates
- [ ] Jack Henry Platform Discovery Checklist — repeatable process for identifying a bank's JH platform, jXchange version, and available data objects during prospect engagement (High confidence)

## Execution Candidates
- JH platform detection / jXchange endpoint inventory — given connection details, detect platform type and catalog available API endpoints

## Task Recommendations

| Task | Priority | Source Entry | Status |
|------|----------|-------------|--------|
| Determine which JH platform to target first for MVP integration | HIGH | 001 | recommended |
| Research jXchange API docs for platform-specific endpoint differences | MED | 001 | recommended |
| Build prospect qualification matrix: bank size → likely JH platform | LOW | 001 | recommended |

## Notes
- SilverLake's AS/400 heritage means potential EBCDIC encoding and fixed-width field issues in the ingestion pipeline
- Platform choice is both a technical and go-to-market decision — it determines which banks Dropsilo can serve first
