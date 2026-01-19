# Outbank MCP Finance Stack

Local-first finance workspace with a read-only MCP query service on top of
Postgres and NocoDB. The stack is designed for importing Outbank CSV exports,
normalizing transactions, and querying them safely from LLM tools.

## What is here
- Docker Compose stack for Postgres, NocoDB, Metabase, and the MCP service
- MCP tools for fuzzy transaction search with filters
- Import notes and SQL for Outbank CSV normalization

## Quick start
1. Copy the environment template and set a data directory:
   ```bash
   cp .env.example .env
   ```
2. Set `DATA_DIR` in `.env`.
3. Start services:
   ```bash
   docker compose up -d
   ```
4. Initialize schema:
   ```bash
   psql postgresql://finance:finance@localhost:5432/finance -f db/schema.sql
   ```

## Docs
- Stack overview: `docs/stack.md`
- MCP service details: `docs/mcp.md`
- Outbank CSV import steps: `docs/outbank-import.md`
- Metabase starter queries: `docs/metabase.md`

## Open source projects used here
- Postgres: https://www.postgresql.org/
- NocoDB: https://github.com/nocodb/nocodb
- Metabase: https://github.com/metabase/metabase
- Docker / Docker Compose: https://www.docker.com/
- FastMCP: https://github.com/jlowin/fastmcp
- Requests: https://github.com/psf/requests
- Python: https://www.python.org/

## Outbank
- Product: https://outbankapp.com/
- Outbank team: https://outbankapp.com/ueber-outbank/

## Get the app

<a href="https://apps.apple.com/de/app/outbank-banking-finanzen/id1094254051">
  <img alt="Download on the App Store" src="https://tools.applemediaservices.com/api/badges/download-on-the-app-store/black/en-us?size=250x83" height="64">
</a>
<a href="https://play.google.com/store/apps/details?id=com.stoegerit.outbank.android">
  <img alt="Get it on Google Play" src="https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png" height="64">
</a>
