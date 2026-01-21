## Context
The current MCP service queries NocoDB over HTTP, which requires Docker and a running database. The goal is to simplify the workflow by reading Outbank CSV exports directly from a local folder while keeping the same query capabilities.

## Goals / Non-Goals
- Goals:
  - Load all CSV files in a configured folder and normalize them into memory.
  - Preserve local-first privacy without Docker or NocoDB dependencies.
  - Keep the query interface stable for search and filters.
- Non-Goals:
  - No persistence layer beyond the CSV files.
  - No database migrations or UI changes in this change.

## Decisions
- Decision: Use an in-memory JSON list as the primary query store.
  - Rationale: Simplicity and avoids extra dependencies. Fast enough for ~17k rows (~4 MB).
- Decision: Parse Outbank CSV with semicolon delimiter, German date format, and decimal comma.
  - Rationale: Matches existing export format and current ingestion expectations.
- Decision: Provide an MCP tool to reload CSV files on demand.
  - Rationale: Supports refresh without restarting the service when CSVs change.

## Alternatives considered
- SQLite cache or embedded DB
  - Pros: Faster queries for very large datasets, persistence across restarts
  - Cons: Adds schema management and storage complexity, conflicts with the request to avoid extra DBs
  - Outcome: Defer until a concrete scale issue is observed

## Risks / Trade-offs
- Large CSV sets may increase memory usage and startup time.
- CSV parsing inconsistencies could require header mapping or fallbacks if export formats vary.

## Migration Plan
1. Introduce CSV folder configuration and ingestion pipeline.
2. Remove NocoDB client usage in the MCP service.
3. Update docs and sample configuration to reflect the simpler setup.

## Open Questions
- None.
