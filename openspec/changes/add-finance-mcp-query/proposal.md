# Change: Add MCP query service for NocoDB finance data

## Why
Querying finance data through NocoDB's UI is manual and slow. An MCP service enables LLM-driven lookups tailored to finance questions while keeping data local. This also reduces ad hoc exports and gives a repeatable, tool-based interface that an LLM can call safely without exposing the full dataset each time.

## What Changes
- Add a FastMCP-based Python service that queries NocoDB via its REST API
- Provide MCP tools for fuzzy transaction search across common finance fields (account, counterparty, description, IBAN, amount, date)
- Support optional filters for account, IBAN, exact amount, amount range, date, and date range; allow combinations in a single query
- Return results in a normalized response shape that is LLM-friendly (id, date, amount, currency, account, IBAN, description, source table), with a small summary of applied filters
- Include basic query controls such as max results and sort order (default: most recent first)
- Configure NocoDB connectivity via `.env` (base URL, auth token, table name/view, field mapping) to avoid hardcoded schema coupling
- Add a Docker Compose service for the MCP container with configurable port (default `6668`)
- Add minimal docs/examples for tool usage and common finance questions
- Define clear non-goals: no write-back to NocoDB, no forecasting, no external data egress

## Impact
- Affected specs: finance-mcp
- Affected code: Docker Compose, MCP service, env/docs for configuration
- Operational impact: one additional container, new port binding, local-only access expected
