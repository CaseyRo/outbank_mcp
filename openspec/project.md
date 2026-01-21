# Project Context

## Purpose
Provide a trustworthy, local-first MCP query service that reads Outbank CSV exports from a folder, normalizes transactions in memory, and exposes read-only search tools. The goal is a lightweight, no-Docker workflow for local querying.

## Tech Stack
- Python 3.10+ with FastMCP
- `uv` for dependency management
- Optional Docker support for containerized execution
- In-memory CSV processing (no database required)

## Project Conventions

### Code Style
- Keep code simple and single-file focused until proven insufficient
- Use kebab-case for file and directory names
- Keep README-like docs short and task-oriented
- Prefer environment variables over hardcoded configuration

### Architecture Patterns
- Local-first: all data stays on the user's machine
- CSV ingestion: read Outbank CSVs from a configured folder
- In-memory processing: normalize CSV rows into JSON for query operations
- Idempotent updates: re-reading the same CSV should not create duplicates
- Read-only queries: MCP tools provide search and inspection, no write operations

### Testing Strategy
- Manual verification: load CSV, validate row counts, and check search results
- Spot-check metrics: account totals and date range queries
- MCP transport tests available in `scripts/mcp-tests/`

### Git Workflow
- Small, focused commits per feature or doc update
- Keep implementation changes separate from documentation updates

## Domain Context
- Outbank CSVs include account, booking date, value date, amount, currency, and purpose fields
- Primary entity is a transaction; accounts act as a dimension for grouping
- Regular updates will append new transactions when CSV files are reloaded
- CSV format uses semicolon delimiters and German date format (DD.MM.YYYY)

## Important Constraints
- Privacy-first: no external uploads or hosted services unless explicitly approved
- Must work without Docker (Docker is optional)
- Avoid vendor lock-in; keep data exportable as CSV
- No database dependencies for core functionality

## External Dependencies
- FastMCP: MCP server framework
- Python standard library: csv, pathlib, difflib
- Optional: Docker and Docker Compose for containerized execution
