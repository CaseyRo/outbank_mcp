# Change: Migrate to FastMCP 3.0

## Why

FastMCP 3.0 has been released with significant architectural improvements including:
- Provider architecture for dynamic component sourcing
- Transform system (middleware for components)
- Session-scoped state management
- Component versioning
- Improved developer experience with hot-reload

Our current implementation uses FastMCP 2.14.x. Upgrading ensures we:
- Stay on a supported version
- Benefit from performance improvements
- Access new features like component versioning and transforms
- Maintain compatibility with the evolving MCP ecosystem

## What Changes

### Import Updates (if any needed)
- Verify all imports use `from fastmcp import FastMCP` (already correct)
- Update middleware imports if paths changed
- Update any deprecated API usage

### Authentication Migration (Key Change)
- **Replace custom `HTTPAuthMiddleware` with FastMCP v3's built-in `AuthMiddleware`**
- Use `require_auth` from `fastmcp.server.auth` for bearer token validation
- Leverage `ctx.user` for authenticated user context in tools
- Keep custom `RequestSizeLimitMiddleware`, `AuditLoggingMiddleware` (verify compatibility)
- Keep `RateLimitingMiddleware` (verify compatibility)

### API Changes
- `get_tools()` returns list instead of dict
- State methods are now async: `await ctx.set_state()`, `await ctx.get_state()`
- Component enable/disable moved to server level

### Configuration
- `FASTMCP_SHOW_CLI_BANNER` → `FASTMCP_SHOW_SERVER_BANNER`
- Remove any `include_fastmcp_meta` parameters

### Dependencies
- Update `pyproject.toml` to require `fastmcp>=3.0.0`
- Update `uv.lock` with new dependencies

### Future Improvements (Out of Scope)
- Scopes-based authorization (`require_scopes`)
- User identity extraction from tokens (`AuthContext`)
- Role-based access control for tools

## Impact

- Affected specs: `finance-mcp`
- Affected code: `app.py`, `pyproject.toml`, tests
- **BREAKING**: Custom `HTTPAuthMiddleware` replaced by built-in `AuthMiddleware`
- Risk: Medium - v3 is new, may have undiscovered issues

## References

- [FastMCP 3.0 Release Notes](https://github.com/jlowin/fastmcp/releases)
- [Upgrade Guide](https://github.com/jlowin/fastmcp/blob/main/docs/development/upgrade-guide.mdx)
- [FastMCP Documentation](https://gofastmcp.com)
