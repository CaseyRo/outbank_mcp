## 1. Implementation
- [x] 1.1 Update `_http_auth_enabled()` to always return `True` when HTTP transport is used
- [x] 1.2 Add startup validation to require `MCP_HTTP_AUTH_TOKEN` when `MCP_TRANSPORT=http`
- [x] 1.3 Remove `MCP_HTTP_AUTH_ENABLED` configuration logic and references
- [x] 1.4 Update `_require_http_auth()` to always enforce auth for HTTP transport (remove conditional check)

## 2. Configuration Updates
- [x] 2.1 Update `.env.example` to show `MCP_HTTP_AUTH_TOKEN` as required for HTTP transport
- [x] 2.2 Remove `MCP_HTTP_AUTH_ENABLED` from `.env.example`
- [x] 2.3 Update `docker-compose.yml` to remove `MCP_HTTP_AUTH_ENABLED` reference

## 3. Documentation Updates
- [x] 3.1 Update `docs/security.md` to reflect mandatory HTTP auth
- [x] 3.2 Update `docs/mcp.md` to show token as required for HTTP transport
- [x] 3.3 Update `README.md` to mention mandatory HTTP auth requirement

## 4. Test Updates
- [x] 4.1 Update HTTP transport tests to always use auth tokens
- [x] 4.2 Add test for startup failure when HTTP transport is used without token
- [x] 4.3 Update test fixtures to require auth tokens for HTTP transport
- [x] 4.4 Update test documentation to reflect mandatory auth

## 5. Validation
- [x] 5.1 Verify HTTP transport fails to start without token
- [x] 5.2 Verify HTTP transport works with valid token
- [x] 5.3 Verify stdio transport works without auth (unchanged)
- [x] 5.4 Run existing test suite to ensure no regressions
