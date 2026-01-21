# Security Guide

This project is designed for local-only use. Exposing the MCP service to the
public internet is out of scope for this repository and entirely at your own
risk. If you publish this service, you are responsible for hardening,
monitoring, and access control.

## Recommended local-only setup
- Bind the MCP service to localhost (default `127.0.0.1` via `MCP_HOST`).
- Use a firewall or VPN if you must access the service remotely.

Example local-only binding:
```bash
MCP_HOST=127.0.0.1
```

## Stdio transport notes
Stdio is the default transport. When running in stdio mode (`MCP_TRANSPORT=stdio`),
the service is only reachable by local processes that can spawn the server, which
is the safest option.

## Required HTTP token auth
The MCP service **requires** authentication for all HTTP transport requests. When using HTTP transport, `MCP_HTTP_AUTH_TOKEN` must be configured, and the service will fail to start if it is not set.

### Configuration
Set this in `.env` or your shell environment when using HTTP transport:
- `MCP_HTTP_AUTH_TOKEN=your-secret-token` (required for HTTP transport)

**Token Security Requirements:**
- Minimum length: 16 characters (enforced)
- Recommended length: 32+ characters
- Should be randomly generated, not predictable patterns

The service will validate that `MCP_HTTP_AUTH_TOKEN` is set and meets minimum security requirements at startup when `MCP_TRANSPORT=http`. If the token is missing or too short, startup will fail with a clear error message.

### Generating a Secure Token

**Quick method (recommended):** Use the provided script that generates and copies the token to your clipboard:
```bash
python scripts/generate-auth-token.py
```

**Manual methods:**

Generate a secure random token using Python:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Or using OpenSSL:
```bash
openssl rand -base64 32
```

Or using `openssl rand -hex`:
```bash
openssl rand -hex 32
```

These commands generate tokens with sufficient entropy (128+ bits) for secure authentication. The provided script (`scripts/generate-auth-token.py`) automatically generates a token with 256 bits of entropy and copies it to your clipboard.

### Security Standards Compliance

This implementation adheres to established security standards for bearer token authentication:

**OWASP Session Management Guidelines:**
- ✅ Tokens have minimum 64 bits of entropy (16+ characters)
- ✅ Recommended 128+ bits of entropy (32+ characters)
- ✅ Validation enforces minimum length requirements
- ✅ Weak pattern detection warns about insecure tokens

**OAuth 2.0 Bearer Token Usage (RFC 6750):**
- ✅ Tokens are unpredictable and unforgeable (validated at startup)
- ✅ Bearer token authentication implemented correctly
- ✅ Tokens should be transmitted over secure channels (user responsibility for HTTPS/TLS)
- ✅ Token validation prevents weak or predictable tokens

**NIST Guidelines:**
- ✅ Minimum token length enforced (16 characters)
- ✅ Character diversity validation
- ✅ Weak pattern detection (common words, repeated characters)

**Implementation Details:**
- Token validation occurs at startup when HTTP transport is used
- Minimum 16 characters enforced (raises error if not met)
- Warnings issued for tokens < 32 characters or with weak patterns
- Clear error messages guide users to generate secure tokens
- Documentation includes secure token generation examples

### Client usage
Include a bearer token header. The service uses HTTP-only (no SSE streaming) and returns complete JSON responses:
```bash
curl -sS -X POST "http://localhost:6668/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer your-secret-token" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

**Note**: The `Accept: application/json, text/event-stream` header is required for FastMCP compatibility, but responses are always complete JSON objects (no streaming).

### Notes and limitations
- This is a single shared token for HTTP only.
- There is no per-user token management.

### Future improvements
The following security enhancements are out of scope for local-only deployment but
could be considered for multi-user or production scenarios:

- **Token rotation/expiration**: Implement time-limited tokens with automatic rotation
- **Per-user tokens**: Support multiple tokens with individual audit trails
- **OAuth 2.0 integration**: Full OAuth flow with refresh tokens
- **Rate limiting per token**: Individual rate limits based on token identity
