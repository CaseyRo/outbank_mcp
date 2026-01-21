# Change: Align MCP tooling with OpenAI standards and dual transport

## Why
The MCP service needs to match OpenAI tooling standards for clear tool presentation and approval readiness, while supporting both stdio and authenticated HTTP transports in a non-Docker workflow.

## What Changes
- Document OpenAI MCP tool presentation expectations and approval readiness checklist.
- Add dual transport support (stdio + HTTP) with HTTP token auth.
- Update security and run docs for non-Docker usage and auth guidance.

## Impact
- Affected specs: finance-mcp, documentation
- Affected code: services/finance-mcp/app.py
- Affected docs: README.md, docs/mcp.md, docs/security.md
