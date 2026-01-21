# Local Finance Workspace

## Prereqs
- Python 3.10+
- `uv` installed
- A folder containing Outbank CSV exports

## Configure CSV folder
The MCP service reads configuration from `.env`.

```bash
cp .env.example .env
```

Set `OUTBANK_CSV_DIR` to the folder containing your CSV exports. Optional:
- `OUTBANK_CSV_GLOB` to customize the file pattern (default `*.csv`)
- `MCP_PORT` to change the HTTP port

## Install dependencies
```bash
uv venv
uv pip install -r services/finance-mcp/requirements.txt
```

## Run the MCP service
```bash
uv run python services/finance-mcp/app.py
```

## MCP query service
The MCP query service provides read-only, fuzzy transaction search for LLM
tools. See `docs/mcp.md` for environment variables and examples.
