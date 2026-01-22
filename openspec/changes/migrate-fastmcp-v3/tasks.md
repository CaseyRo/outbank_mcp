## 1. Compatibility Assessment

- [x] 1.1 Create a branch for migration testing
- [x] 1.2 Update `pyproject.toml` to `fastmcp>=3.0.0b1,<4.0.0`
- [x] 1.3 Run `uv sync` to install v3
- [x] 1.4 Attempt to start server and document errors (none found)
- [x] 1.5 Run test suite and document failures (Python 3.14 mcp.types issue only)

## 2. Import Path Updates

- [x] 2.1 Verify `from fastmcp import FastMCP` still works
- [x] 2.2 Check `fastmcp.server.dependencies.get_http_headers` path (unchanged)
- [x] 2.3 Check `fastmcp.server.middleware` module path (unchanged)
- [x] 2.4 Check `fastmcp.server.middleware.rate_limiting` path (unchanged)
- [x] 2.5 Update any broken imports (none needed)

## 3. Authentication Analysis (Completed)

- [x] 3.1 Analyzed v3's `AuthMiddleware` and `require_auth`
- [x] 3.2 Finding: v3 auth is designed for OAuth/JWT, not simple bearer tokens
- [x] 3.3 Decision: Keep custom `HTTPAuthMiddleware` for bearer token validation
- [x] 3.4 Verified our middleware is compatible with v3's `Middleware` base class
- [x] 3.5 Documented OAuth migration as future improvement

## 4. Remaining Middleware Compatibility

- [x] 4.1 Verify `Middleware` base class interface unchanged
- [x] 4.2 Verify `MiddlewareContext` attributes available
- [x] 4.3 Test `RequestSizeLimitMiddleware` with v3 (works)
- [x] 4.4 Test `RateLimitingMiddleware` with v3 (works)
- [x] 4.5 Test `AuditLoggingMiddleware` with v3 (works)
- [x] 4.6 Migrate to Transform system if middleware deprecated (not needed)

## 5. API Updates

- [x] 5.1 Check if we use `get_tools()` return value as dict (we don't)
- [x] 5.2 Check for any `ctx.set_state()`/`ctx.get_state()` usage (we don't)
- [x] 5.3 Check for `enable()`/`disable()` usage (we don't)
- [x] 5.4 Remove any `include_fastmcp_meta` parameters (none found)

## 6. Configuration Updates

- [x] 6.1 Update `FASTMCP_SHOW_CLI_BANNER` references if any (none found)
- [x] 6.2 Review `.env.example` for any FastMCP-specific vars (none needed)

## 7. Testing

- [x] 7.1 Run stdio transport tests (pass)
- [x] 7.2 Run HTTP transport tests with auth (pass, some skipped - require server)
- [x] 7.3 Verify rate limiting works (middleware verified)
- [x] 7.4 Verify audit logging works (middleware verified)
- [x] 7.5 Verify health_check tool works (pass)
- [x] 7.6 Run full BDD test suite (13 passed, 3 skipped)

## 8. Documentation

- [x] 8.1 Update CHANGELOG.md with v3 migration
- [x] 8.2 Update pyproject.toml version to 1.0.0
- [x] 8.3 Note any behavior changes in docs/mcp.md (none needed)
- [x] 8.4 Add scopes/advanced auth to docs/security.md future improvements

## 9. Finalization

- [ ] 9.1 Merge migration branch
- [ ] 9.2 Tag release if appropriate
