## Context
A local-first finance workspace is needed to replace manual Google Sheets workflows. The stack must support Outbank CSV imports, idempotent updates, and basic dashboards.

## Goals / Non-Goals
- Goals: local Docker stack, reliable CSV imports, baseline dashboards, privacy-first storage
- Non-Goals: bank API integrations, automated syncing, hosted services

## Decisions
- Use Postgres as the primary datastore for better reliability and visualization compatibility
- Use NocoDB as the CRUD and CSV import UI
- Use Metabase for quick dashboards and charts
- Treat Currency as free-form text to support non-ISO values (points/miles)
- Store raw CSV strings for auditability alongside parsed fields

## Risks / Trade-offs
- CSV imports are manual; no automation in scope
- De-duplication depends on stable source data; changes in export formatting can create duplicates

## Migration Plan
- Start with a single transactions table, add accounts as a dimension as data grows
- Backfill existing CSV exports before setting up dashboards

## Open Questions
- Which columns should compose the de-duplication key for maximal stability?
- Do we want separate tables for categories and tags, or keep them as text fields initially?
