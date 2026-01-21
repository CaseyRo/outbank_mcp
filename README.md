# Outbank MCP CSV Workspace

Local-first MCP query service that reads Outbank CSV exports from a folder,
normalizes transactions in memory, and exposes read-only search tools. The
goal is a lightweight, no-Docker workflow for local querying.

## Purpose and responsibility
This project exists solely to supply LLMs with your finance data using exports
from the popular Outbank tool. You are responsible for how your data is
handled, exported, stored, and shared. Prefer local models over big-tech hosted
LLMs whenever possible. If you do use an external model, using an MCP to query
your local data is safer than uploading raw CSV exports repeatedly.

> ⚠️ 🔒 🚫 **Local-only warning**  
> This project is intended for local-only use.  
> Exposing the MCP service publicly is out of scope and entirely at your own risk.  
> See `docs/security.md` for recommended local-only and optional HTTP auth setup.

## What is here
- Python MCP service for CSV-folder ingestion and query tools
- Notes on Outbank CSV export format and normalization
- Example Outbank CSV export (`outbank_export_example.csv`)

## Quick start
1. Install `uv`: https://github.com/astral-sh/uv
2. Copy the environment template and set your CSV folder:
   ```bash
   cp .env.example .env
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   uv pip install -r services/finance-mcp/requirements.txt
   ```
4. Run the MCP service:
   ```bash
   uv run python services/finance-mcp/app.py
   ```

## CSV format
Outbank exports use semicolon-delimited CSV with German date format and
decimal commas. Expected header example:
```csv
#;Account;Date;Value Date;Amount;Currency;Name;Number;Bank;Reason;Category;Subcategory;Category-Path;Tags;Note;Posting Text
```

## Docs
- MCP service details: `docs/mcp.md`
- Security guide: `docs/security.md`
- Outbank CSV import steps: `docs/outbank-import.md`

## Open source projects used here
- FastMCP: https://github.com/jlowin/fastmcp
- Python: https://www.python.org/
- uv: https://github.com/astral-sh/uv

## Outbank
- Product: https://outbankapp.com/
- Outbank team: https://outbankapp.com/ueber-outbank/
- Affiliate link (free month): https://outbankapp.com/affiliate-gratismonat/?id=outbank_mcp
  - Disclosure: this is an affiliate link.
