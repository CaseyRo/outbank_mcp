# Finance MCP Query Service

## Overview
The finance MCP service exposes a small set of tools for querying Outbank CSV
transactions via an LLM. The service is read-only and uses fuzzy matching with
optional filters (account, IBAN, amount, date range).

## Environment
The service reads its configuration from `.env` or environment variables.
Start by copying `.env.example` to `.env` so defaults are in place.

- `MCP_PORT` (default `6668`)
- `MCP_HTTP_AUTH_ENABLED` (default `false`)
- `MCP_HTTP_AUTH_TOKEN` (optional shared token for HTTP auth)
- `MCP_MIN_SCORE` (default `0.55`)
- `OUTBANK_CSV_DIR` (folder containing Outbank CSV exports)
- `OUTBANK_CSV_GLOB` (default `*.csv`)

## Tools

### `search_transactions`
Fuzzy transaction search with optional filters.

Inputs:
- `query` (string, optional)
- `account` (string, optional)
- `iban` (string, optional)
- `amount` (number, optional)
- `amount_min` / `amount_max` (number, optional)
- `date` (YYYY-MM-DD, optional)
- `date_start` / `date_end` (YYYY-MM-DD, optional)
- `max_results` (default `25`)
- `sort` (`-date`, `date`, `-amount`, `amount`)

Example questions:
- "Find transactions for my ING account between 2024-01-01 and 2024-01-31."
- "Show payments around 79.99 with IBAN NL00TEST123."
- "List grocery expenses for the last week."

### `reload_transactions`
Reloads CSV data from the configured folder and returns counts.
The response includes `total_records`, `new_records`, `removed_records`, and `files_scanned`.

### `describe_fields`
Returns the current CSV configuration and expected headers.

## Response Shape
The search tool returns a normalized result set with:
- `id`
- `date`
- `value_date`
- `amount`
- `currency`
- `account`
- `iban`
- `counterparty`
- `description`
- `category`
- `subcategory`
- `category_path`
- `tags`
- `note`
- `posting_text`
- `source_file`
- `score` (fuzzy match score)

## Security
This service is intended for local-only use. If you need to add basic access
control on HTTP, see `docs/security.md` for the shared token setup.

## Test scripts
Basic to advanced MCP test calls are available under `scripts/mcp-tests/`.
Set `MCP_URL` and run the shell scripts to validate tool discovery and queries.
