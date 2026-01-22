## Context

FastMCP 3.0 introduces a new architecture based on providers, transforms, and components. Our finance-mcp server uses custom middleware for authentication, rate limiting, request size limiting, and audit logging. We need to verify compatibility and migrate any deprecated patterns.

## Goals / Non-Goals

**Goals:**
- Upgrade to FastMCP 3.0 stable release
- Maintain all existing functionality (auth, rate limiting, audit logging, health check)
- Update any deprecated API usage
- Ensure tests pass with new version

**Non-Goals:**
- Adopt new v3 features like component versioning (can be done later)
- Migrate to Transform system (only if required)
- Add new functionality during migration

## Current Implementation Analysis

### Imports (app.py:13-16)
```python
from fastmcp import FastMCP                                    # ✅ Already v3 style
from fastmcp.server.dependencies import get_http_headers       # ⚠️ Verify path
from fastmcp.server.middleware import Middleware, MiddlewareContext  # ⚠️ Verify path
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware  # ⚠️ Verify path
```

### Custom Middleware Classes
1. **HTTPAuthMiddleware** - Bearer token validation → **REPLACE with v3 `AuthMiddleware`**
2. **RequestSizeLimitMiddleware** - Content-Length checking → Keep, verify compatibility
3. **AuditLoggingMiddleware** - Tool invocation logging → Keep, verify compatibility

All extend `Middleware` base class and implement `__call__` with `MiddlewareContext`.

### FastMCP v3 Authorization Analysis

**Finding:** v3's `AuthMiddleware` + `require_auth` is designed for OAuth/JWT tokens:
- Expects tokens with claims and scopes (JWT format)
- `require_auth` only checks if token exists, doesn't validate values
- `get_access_token()` looks for `AuthenticatedUser` in ASGI scope
- Designed for OAuth flows, not simple bearer token validation

**Decision:** Keep our custom `HTTPAuthMiddleware` because:
- It validates bearer tokens against `MCP_HTTP_AUTH_TOKEN` environment variable
- v3's auth system doesn't support simple token comparison out of the box
- Our middleware is compatible with v3's `Middleware` base class
- Existing tests pass with this approach

**Future Migration Path:**
When/if we adopt OAuth, we can migrate to v3's `AuthMiddleware`:
```python
from fastmcp.server.auth import require_auth, require_scopes
from fastmcp.server.middleware import AuthMiddleware

mcp = FastMCP(
    "Finance MCP",
    middleware=[AuthMiddleware(auth=require_scopes("finance:read"))]
)
```

### MCP Tools
- `search_transactions` - Transaction search with filters
- `describe_fields` - CSV configuration info
- `reload_transactions` - Reload CSV files
- `health_check` - Server status

## Migration Strategy

### Phase 1: Compatibility Check
1. Install FastMCP 3.0 in dev environment
2. Run existing tests to identify failures
3. Document specific breaking changes affecting our code

### Phase 2: Authentication Migration (Primary Change)
1. Remove custom `HTTPAuthMiddleware` class (~60 lines)
2. Import `AuthMiddleware` from `fastmcp.server.middleware`
3. Import `require_auth` from `fastmcp.server.auth`
4. Update middleware list: `AuthMiddleware(auth=require_auth)`
5. Update audit logging to use `ctx.user` if available
6. Verify bearer token validation works as before

### Phase 3: Import Updates
1. Update any changed import paths
2. Remove `get_http_headers` import if no longer needed
3. Verify remaining middleware base classes exist

### Phase 4: API Migration
1. If using `get_tools()` result as dict, update to list iteration
2. Check for any state management usage (we don't currently use ctx state)
3. Update component enable/disable if used

### Phase 5: Testing
1. Run full test suite
2. Manual verification of all tools
3. Verify rate limiting, auth, and audit logging work

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| v3 is new (beta), may have bugs | Pin to specific version, have rollback plan |
| Middleware API may change | Check v3 middleware docs, be prepared to rewrite |
| Test fixtures may break | Update fixtures as needed |

## Rollback Plan

If migration fails:
1. Revert `pyproject.toml` to `fastmcp<3`
2. Run `uv sync` to restore v2
3. Verify tests pass

## Open Questions

1. Has `fastmcp.server.middleware` path changed in v3?
2. Does `RateLimitingMiddleware` work the same way?
3. Is `get_http_headers` still available or replaced?
4. Does `require_auth` expect a specific token format/validation?

These will be answered during Phase 1 compatibility check.

## Future Improvements (Out of Scope)

These can be added later once v3 migration is stable:
- **Scopes-based authorization**: Use `require_scopes("read:transactions")` for fine-grained permissions
- **User identity tracking**: Extract user info from tokens via custom `AuthContext`
- **Role-based access**: Different permissions for read-only vs admin users
