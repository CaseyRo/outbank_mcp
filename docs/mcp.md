# Finance MCP Query Service

## Overview
The finance MCP service exposes a small set of tools for querying Outbank CSV
transactions via an LLM. The service is read-only and uses fuzzy matching with
optional filters (account, IBAN, amount, date range).

## Environment
The service reads its configuration from `.env` or environment variables.
Start by copying `.env.example` to `.env` so defaults are in place.

- `MCP_TRANSPORT` (`http` or `stdio`, default `stdio`)
- `MCP_HOST` (default `127.0.0.1` for HTTP)
- `MCP_PORT` (default `6668`)
- `MCP_HTTP_AUTH_TOKEN` (required shared token for HTTP auth when using HTTP transport)
- `MCP_MIN_SCORE` (default `0.55`)
- `OUTBANK_CSV_DIR` (folder containing Outbank CSV exports)
- `OUTBANK_CSV_GLOB` (default `*.csv`)
- `EXCLUDED_CATEGORIES` (comma-separated list of categories to exclude from loading, optional)
- `EXCLUDED_TAGS` (comma-separated list of tags to exclude from loading, optional)
- `MCP_RATE_LIMIT` (rate limit, e.g., "100/minute", HTTP only, optional)
- `MCP_REQUEST_TIMEOUT` (request timeout in seconds, optional)
- `MCP_MAX_REQUEST_SIZE` (max request size in bytes, default 1MB)
- `MCP_AUDIT_ENABLED` (enable audit logging, default true for HTTP)
- `MCP_AUDIT_LOG` (audit log path, default `./logs/audit.log`)

### Transaction Exclusion Filters

The service supports filtering out transactions during CSV ingestion based on category or tag values. This is useful for excluding internal transfers, reconciliation transactions, or other noise from your analysis.

**Configuration:**
- Set `EXCLUDED_CATEGORIES` to exclude transactions by category (e.g., `Transfer,Internal`)
- Set `EXCLUDED_TAGS` to exclude transactions by tag (e.g., `transfer,internal`)
- Matching is case-insensitive and supports partial matches
- Exclusions are applied at load time - excluded transactions never enter the transaction store
- After changing exclusion filters, call `reload_transactions` to apply changes

See the README.md "Configuration" section for detailed documentation and examples.

## Transports
This service supports both stdio and HTTP MCP transports.

### Stdio
```bash
MCP_TRANSPORT=stdio uv run python app.py
```

### HTTP
```bash
MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=6668 \
  MCP_HTTP_AUTH_TOKEN=your-secret-token \
  uv run python app.py
```

The HTTP transport uses standard HTTP requests/responses with JSON-RPC format. **No SSE streaming** - all responses are returned as complete JSON objects. The service uses FastMCP's streamable-http mode internally, but responses are parsed transparently to provide pure JSON (no streaming behavior exposed to clients).

**Authentication is required**: When using HTTP transport, `MCP_HTTP_AUTH_TOKEN` must be set (minimum 16 characters, 32+ recommended). The service will fail to start if the token is missing or too short. Include a bearer token in all HTTP requests.

**Generate a secure token:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

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

### `health_check`
Returns server health status for monitoring and diagnostics.

Response:
- `status`: "healthy" if operational
- `uptime_seconds`: seconds since server start
- `data_loaded`: whether transaction data is loaded
- `record_count`: number of transactions in memory
- `files_scanned`: number of CSV files loaded
- `transport_mode`: current transport (stdio/http)

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
This service is intended for local-only use. HTTP transport requires authentication via `MCP_HTTP_AUTH_TOKEN`. See `docs/security.md` for security guidance and authentication setup.

## OpenAI MCP approval checklist
Based on the MCP specification (2025-11-25): https://modelcontextprotocol.io/specification/2025-11-25

- Tools have stable names, clear descriptions, and complete JSON schema inputs.
- Tool outputs are deterministic, read-only, and documented.
- Errors are surfaced via JSON-RPC responses with actionable messages.
- HTTP transport requires a bearer token (mandatory).
- Security notes explain local-only expectations and auth limits.

## Test scripts
Basic to advanced MCP test calls are available under `scripts/mcp-tests/`.
Set `MCP_URL` and run the shell scripts to validate tool discovery and queries.
