# Change: Add Production Hardening Features

## Why

The MCP server handles financial data and needs additional safeguards for production use. While primarily local-first, the HTTP transport mode should be hardened against abuse, provide operational visibility through audit logging, and include standard project hygiene (CHANGELOG).

## What Changes

- **Rate Limiting**: Add FastMCP built-in rate limiting to protect against request flooding (HTTP mode only)
- **Request Size Limits**: Constrain maximum request payload size
- **Timeout Handling**: Configure request timeouts to prevent hung connections
- **Audit Logging**: Log all tool invocations with timestamps, tool name, and parameters for financial data traceability
- **Health Endpoint**: Add a `health_check` tool for monitoring server status (common pattern even if not MCP spec)
- **CHANGELOG.md**: Add version history tracking
- **Security Documentation**: Note token rotation as a future improvement

## Impact

- Affected specs: `finance-mcp`
- Affected code: `app.py`, `docs/security.md`
- New files: `CHANGELOG.md`
- No breaking changes - all additions are backward compatible
