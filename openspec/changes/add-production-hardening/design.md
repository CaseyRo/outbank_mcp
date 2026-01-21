## Context

The finance MCP server needs production hardening for HTTP transport mode. FastMCP provides built-in middleware for rate limiting and timeout handling, making implementation straightforward.

## Goals / Non-Goals

**Goals:**
- Protect HTTP transport from abuse (rate limiting, request limits, timeouts)
- Provide audit trail for financial tool calls
- Add health check capability for monitoring
- Document version history

**Non-Goals:**
- TLS/HTTPS (user responsibility via reverse proxy)
- Token rotation/expiration (local-only use case)
- Per-user rate limiting (single-token model)
- External monitoring integration

## Decisions

### Rate Limiting
- **Decision**: Use FastMCP's built-in `rate_limit` parameter
- **Configuration**: `100/minute` default, configurable via `MCP_RATE_LIMIT` env var
- **Rationale**: FastMCP uses token bucket algorithm, handles burst traffic gracefully
- **Alternatives considered**: Custom middleware (more complex, reinventing the wheel)

### Request Timeout
- **Decision**: Use FastMCP's `request_timeout` parameter
- **Configuration**: 60 seconds default, configurable via `MCP_REQUEST_TIMEOUT` env var
- **Rationale**: Prevents hung connections, standard timeout for API services
- **Alternatives considered**: Per-tool timeouts (overkill for current use case)

### Request Size Limits
- **Decision**: Implement via custom middleware checking Content-Length header
- **Configuration**: 1MB default, configurable via `MCP_MAX_REQUEST_SIZE` env var
- **Rationale**: FastMCP doesn't have built-in request size limiting; middleware approach is clean

### Audit Logging
- **Decision**: Use Python's `logging` module with structured JSON output to file
- **Log Location**: `./logs/audit.log` (configurable via `MCP_AUDIT_LOG`)
- **Log Format**: JSON lines with timestamp, tool_name, parameters, client_ip (if HTTP)
- **Rationale**: JSON format enables parsing/analysis; file-based avoids external dependencies
- **Alternatives considered**:
  - Rich console output (doesn't persist, interferes with stdio)
  - SQLite (adds database dependency)

### Health Endpoint
- **Decision**: Add `health_check` MCP tool
- **Rationale**: MCP spec doesn't define health endpoints, but `tools/list` response confirms basic connectivity. A dedicated tool provides richer status info (data loaded, record count, uptime).
- **Alternatives considered**:
  - HTTP `/health` endpoint (would require modifying FastMCP routing)
  - Rely on `tools/list` only (insufficient for monitoring)

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Rate limiting may block legitimate heavy usage | Make limit configurable via env var |
| Audit log files grow unbounded | Document log rotation (user responsibility) |
| Request size limit may break large queries | 1MB is generous; make configurable |

## Migration Plan

1. All features are additive with sensible defaults
2. No configuration required - works out of the box
3. Users can tune via environment variables

## Open Questions

None - implementation is straightforward using FastMCP built-ins where available.
