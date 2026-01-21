# Change: Require HTTP Authentication

## Why
HTTP transport exposes the MCP service over a network interface, making it accessible to any process that can reach the endpoint. Currently, authentication is optional, which creates a security risk if users accidentally expose the service without enabling auth. Making HTTP auth mandatory ensures that financial data is always protected when using HTTP transport.

## What Changes
- **BREAKING**: HTTP transport now requires authentication - `MCP_HTTP_AUTH_TOKEN` must be set when using HTTP transport
- Remove `MCP_HTTP_AUTH_ENABLED` configuration option (auth is always enabled for HTTP)
- HTTP transport will fail to start if `MCP_HTTP_AUTH_TOKEN` is not configured
- Stdio transport remains unchanged (no auth required, as it's local process spawning)
- Update documentation to reflect mandatory HTTP auth
- Update `.env.example` to show `MCP_HTTP_AUTH_TOKEN` as required for HTTP transport

## Impact
- Affected specs: `finance-mcp` (HTTP authentication requirement)
- Affected code: `app.py` (auth check logic, startup validation), `.env.example`, `docs/security.md`, `docs/mcp.md`
- Breaking change: Existing HTTP deployments without auth will need to configure `MCP_HTTP_AUTH_TOKEN` to continue working
