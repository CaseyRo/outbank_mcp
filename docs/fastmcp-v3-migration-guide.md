# FastMCP v2 to v3 Migration Guide

A practical guide for migrating MCP servers from FastMCP 2.x to 3.x, based on real migration experience.

## Pre-Migration Checklist

1. **Check current FastMCP version**: `uv pip show fastmcp` or check `pyproject.toml`
2. **Check v3 availability**: v3.0.0 went stable on Feb 18, 2026. Latest stable is `3.0.2`
3. **Create a migration branch**: Don't migrate on main

## Step 1: Update Dependencies

```toml
# pyproject.toml
dependencies = [
  "fastmcp>=3.0.0,<4.0.0",
  # ... other deps
]
```

Then sync:
```bash
uv sync
```

## Step 2: Verify Imports

All these imports work unchanged in v3:

```python
from fastmcp import FastMCP                                    # ✅ Same
from fastmcp.server.dependencies import get_http_headers       # ✅ Same
from fastmcp.server.middleware import Middleware, MiddlewareContext  # ✅ Same
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware  # ✅ Same
```

**New v3 imports available:**
```python
from fastmcp.server.auth import require_auth, require_scopes, AuthContext
from fastmcp.server.middleware import AuthMiddleware
```

## Step 3: Authentication Considerations

### v3 Built-in Auth (OAuth/JWT)

v3 introduces `AuthMiddleware` with `require_auth` for OAuth/JWT-based authentication:

```python
from fastmcp.server.auth import require_auth
from fastmcp.server.middleware import AuthMiddleware

mcp = FastMCP("Server", middleware=[AuthMiddleware(auth=require_auth)])
```

**Important**: This is designed for OAuth/JWT tokens with claims and scopes. It:
- Checks if a token exists (`require_auth`)
- Can check for specific scopes (`require_scopes("scope:name")`)
- Expects tokens to be validated by an external auth provider
- Does NOT validate tokens against a configured secret

### Simple Bearer Token Auth

If you use simple bearer token validation (comparing against an env var like `MCP_HTTP_AUTH_TOKEN`), **keep your custom middleware**:

```python
class HTTPAuthMiddleware(Middleware):
    async def __call__(self, context: MiddlewareContext, call_next):
        # get_http_headers strips authorization by default (3.0.2+);
        # explicitly include it so we can validate the bearer token.
        headers = get_http_headers(include={"authorization"})
        if not headers:
            return await call_next(context)  # stdio transport

        auth_header = headers.get("authorization", "")
        scheme, _, token = auth_header.partition(" ")

        expected = os.getenv("MCP_HTTP_AUTH_TOKEN", "")
        if scheme.lower() != "bearer" or token.strip() != expected:
            raise PermissionError("Unauthorized")

        return await call_next(context)
```

**Important (3.0.2+):** `get_http_headers()` now strips sensitive headers (`authorization`, `content-length`, etc.) by default to prevent leakage to downstream services. Use the `include` parameter to explicitly request headers you need. Headers are also normalized to lowercase.

## Step 4: Middleware Compatibility

Custom middleware extending `Middleware` base class works unchanged:

```python
class CustomMiddleware(Middleware):
    async def __call__(self, context: MiddlewareContext[Any], call_next: Any) -> Any:
        # Your logic here
        return await call_next(context)
```

**Verified compatible:**
- `RateLimitingMiddleware` (built-in)
- Custom auth middleware
- Custom request size limiting middleware
- Custom audit logging middleware

## Step 5: API Changes to Check

| v2 Pattern | v3 Status | Action |
|------------|-----------|--------|
| `get_tools()` returns dict | Returns list in v3 | Update if iterating as dict |
| `ctx.set_state()` / `ctx.get_state()` | Now async | Add `await` if used |
| `enable()` / `disable()` on components | Moved to server level | Update calls |
| `include_fastmcp_meta` parameter | Removed | Remove if present |
| `FASTMCP_SHOW_CLI_BANNER` env var | Renamed to `FASTMCP_SHOW_SERVER_BANNER` | Update if used |
| `get_http_headers()` returns all headers | Now strips `authorization`, `content-length`, etc. by default (3.0.2+) | Use `include={"authorization"}` param |

## Step 6: Transport Changes

v3 uses `streamable-http` transport which requires session management:

- Clients must send `initialize` request first
- Server returns `Mcp-Session-Id` header
- Subsequent requests must include this session ID
- Direct curl requests without session will fail with "Missing session ID"

**Update test clients** to handle session initialization:

```python
class HttpMCPClient:
    def __init__(self, url, auth_token=None):
        self.session_id = None

    def _initialize(self):
        response = requests.post(self.url, json={
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "client", "version": "1.0.0"}
            }
        }, headers={"Authorization": f"Bearer {self.auth_token}"})

        self.session_id = response.headers.get("Mcp-Session-Id")

    def send_request(self, method, params=None):
        if not self.session_id:
            self._initialize()

        headers = {"Mcp-Session-Id": self.session_id}
        # ... make request
```

## Step 7: Testing Strategy

1. **Start server and check for import errors**:
   ```bash
   uv run python -c "import app"
   ```

2. **Start server and verify startup**:
   ```bash
   timeout 5 uv run python app.py
   ```

3. **Run existing test suite**:
   ```bash
   uv run pytest tests/ -v
   ```

4. **Common test issues**:
   - Python 3.14 + `mcp.types` import errors: Extract pure-Python functions to separate module
   - Session handling: Update HTTP test clients to initialize sessions
   - Auth tests: Ensure test tokens match server configuration

## Step 8: Python 3.14 Compatibility

If tests fail with `ModuleNotFoundError: No module named 'mcp.types'` when importing from your app module:

**Problem**: Test imports `from app import some_function` → triggers FastMCP import chain → fails on `mcp.types`

**Solution**: Extract pure-Python functions (that don't need FastMCP) to a separate module:

```python
# exclusion_filters.py (no FastMCP imports)
def my_pure_function():
    ...

# app.py
from exclusion_filters import my_pure_function

# tests/test_something.py
from exclusion_filters import my_pure_function  # Direct import, no FastMCP
```

## Step 9: Documentation Updates

1. Update CHANGELOG with v3 migration
2. Update version in `pyproject.toml`
3. Note any behavior changes in docs
4. Add future OAuth/scopes features to security docs if applicable

## Rollback Plan

If migration fails:

```bash
# Revert pyproject.toml
git checkout pyproject.toml

# Or pin to v2
# dependencies = ["fastmcp<3.0.0", ...]

# Restore dependencies
uv sync
```

## Future v3 Features (Can Add Later)

Once stable on v3, consider adopting:
- **Scopes-based authorization**: `require_scopes("read:data")`
- **User identity tracking**: Custom `AuthContext` for audit logging
- **Component versioning**: Version your tools
- **Transform system**: Middleware for components
- **Provider architecture**: Dynamic component sourcing

## Quick Reference

```bash
# Check version
uv run python -c "import fastmcp; print(fastmcp.__version__)"

# Install v3 stable
uv add "fastmcp>=3.0.0,<4.0.0"

# Sync dependencies
uv sync

# Test imports
uv run python -c "from fastmcp import FastMCP; print('OK')"
```
