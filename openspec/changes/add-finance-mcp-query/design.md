## Context
We already run a local NocoDB finance stack. We need an MCP service that can answer LLM questions by querying NocoDB through its API with a small, focused tool surface.

## Goals / Non-Goals
- Goals: FastMCP-based Python service, fuzzy search over transactions, optional filters for account/IBAN/amount/date, local-only operation
- Non-Goals: Write-back operations, automation/sync, broad analytics or forecasting

## Decisions
- Use FastMCP in Python for the MCP server runtime
- Query NocoDB via its REST API rather than direct database access
- Expose a single primary tool for fuzzy transaction search with optional filters
- Make the MCP service port configurable via `.env`, defaulting to `6668`

## Risks / Trade-offs
- NocoDB API schema changes could require service updates
- Fuzzy matching may return unexpected results; keep scope read-only and transparent

## Migration Plan
- Add MCP service container to the Docker Compose stack
- Document environment variables and usage examples

## Open Questions
- Which NocoDB API auth mechanism should be preferred (token vs. public API access)?
- Should the MCP tool return raw rows, a summarized view, or both?
