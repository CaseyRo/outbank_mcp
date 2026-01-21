## 1. Rate Limiting & Timeouts

- [x] 1.1 Add `MCP_RATE_LIMIT` environment variable parsing (default: "100/minute")
- [x] 1.2 Add `MCP_REQUEST_TIMEOUT` environment variable parsing (default: 60 seconds)
- [x] 1.3 Configure FastMCP with rate_limit and request_timeout parameters
- [x] 1.4 Update `.env.example` with new variables and documentation

## 2. Request Size Limiting

- [x] 2.1 Add `MCP_MAX_REQUEST_SIZE` environment variable (default: 1MB)
- [x] 2.2 Create `RequestSizeLimitMiddleware` class
- [x] 2.3 Add middleware to FastMCP initialization for HTTP transport
- [x] 2.4 Update `.env.example` with new variable

## 3. Audit Logging

- [x] 3.1 Add `MCP_AUDIT_LOG` environment variable (default: "./logs/audit.log")
- [x] 3.2 Add `MCP_AUDIT_ENABLED` environment variable (default: true for HTTP, false for stdio)
- [x] 3.3 Create audit logger setup with JSON formatter
- [x] 3.4 Create `AuditLoggingMiddleware` class to log tool invocations
- [x] 3.5 Add middleware to FastMCP initialization
- [x] 3.6 Update `.env.example` with new variables

## 4. Health Check Tool

- [x] 4.1 Create `health_check` MCP tool function
- [x] 4.2 Return: status, uptime, data_loaded, record_count, files_scanned, transport_mode
- [x] 4.3 Add startup timestamp tracking

## 5. Documentation Updates

- [x] 5.1 Update `docs/security.md` with token rotation note as future improvement
- [x] 5.2 Update `docs/mcp.md` with new health_check tool documentation
- [x] 5.3 Create `CHANGELOG.md` with initial version history

## 6. Pre-commit Configuration

- [x] 6.1 Create `.pre-commit-config.yaml` with ruff and standard hooks
- [x] 6.2 Add pre-commit and ruff to dev dependencies in `pyproject.toml`
- [x] 6.3 Document pre-commit setup in README.md

## 7. Testing

- [x] 7.1 Add test for health_check tool
- [x] 7.2 Add test for rate limiting
- [x] 7.3 Add test for request size limits
- [x] 7.4 Add test for audit log file creation and format
