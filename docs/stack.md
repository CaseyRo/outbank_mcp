# Local Finance Stack

## Prereqs
- Docker Desktop or Docker Engine
- A writable data directory for persistent volumes

## Configure data directory
Docker Compose reads configuration from `.env`.

```bash
cp .env.example .env
```

Set `DATA_DIR` to the host path where data should live:
- Local workstation: `/Volumes/data`
- Container host: `/mnt/data`

If you want non-default credentials, also set:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `MCP_PORT` (optional)
- `NOCODB_TOKEN` (if your NocoDB instance requires auth)

## Start services
```bash
docker compose up -d
```

Services:
- Postgres: `localhost:5432`
- NocoDB: `http://localhost:8080`
- Metabase: `http://localhost:3000`
- Finance MCP: `http://localhost:${MCP_PORT:-6668}`

## MCP query service
The MCP query service provides read-only, fuzzy transaction search for LLM
tools. See `docs/mcp.md` for environment variables and examples.

## Initialize schema
```bash
psql postgresql://${POSTGRES_USER:-finance}:${POSTGRES_PASSWORD:-finance}@localhost:5432/${POSTGRES_DB:-finance} -f db/schema.sql
```
