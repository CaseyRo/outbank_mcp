# Finance MCP Query Service

## Overview
The finance MCP service exposes a small set of tools for querying NocoDB
transactions via an LLM. The service is read-only and uses fuzzy matching
with optional filters (account, IBAN, amount, date range).

## Environment
The service reads its configuration from `.env` or Docker Compose variables.
Start by copying `.env.example` to `.env` so defaults are in place.

- `MCP_PORT` (default `6668`)
- `NOCODB_BASE_URL` (default `http://nocodb:8080`)
- `NOCODB_TOKEN` (optional API token, sent as `xc-token`)
- `NOCODB_TABLE` (required table id or name, default `transactions`)
- `NOCODB_VIEW_ID` (optional view id)
- `NOCODB_PAGE_SIZE` (default `200`)
- `NOCODB_MAX_PAGES` (default `5`)
- `MCP_MIN_SCORE` (default `0.55`)

Field mapping (override when your NocoDB column names differ):
- `NOCODB_FIELD_ID` (default `id`)
- `NOCODB_FIELD_DATE` (default `booking_date`)
- `NOCODB_FIELD_AMOUNT` (default `amount`)
- `NOCODB_FIELD_CURRENCY` (default `currency`)
- `NOCODB_FIELD_ACCOUNT` (default `account`)
- `NOCODB_FIELD_IBAN` (default `counterparty_account`)
- `NOCODB_FIELD_DESCRIPTION` (default `reason`)
- `NOCODB_FIELD_COUNTERPARTY` (default `counterparty_name`)

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

### `describe_fields`
Returns the current field mapping configuration for validation.

## Response Shape
The tool returns a normalized result set with:
- `id`
- `date`
- `amount`
- `currency`
- `account`
- `iban`
- `counterparty`
- `description`
- `source_table`
- `score` (fuzzy match score)

## Test scripts
Basic to advanced MCP test calls are available under `scripts/mcp-tests/`.
Set `MCP_URL` and run the shell scripts to validate tool discovery and queries.
