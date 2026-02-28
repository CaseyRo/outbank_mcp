# Detailed Security Findings - mcp_outbank

## Audit Date: 2026-02-26
## Auditor: Claude Security Auditor (claude-sonnet-4-6)

---

## MEDIUM-1: Non-Timing-Safe Token Comparison
File: app.py:541
Fix: `if not hmac.compare_digest(provided.strip(), expected):`
Import: `import hmac` at top of file

## MEDIUM-2: Unbounded max_results
File: app.py:639,722
Fix: Add `max_results = min(max(1, max_results), 500)` before slicing

## MEDIUM-3: Unbounded query length
File: app.py:629,656
Fix: Add `if query and len(query) > 500: raise ValueError("query too long (max 500 chars)")`

## MEDIUM-4: X-Forwarded-For IP Spoofing in Audit Log
File: app.py:589-594
Fix: Only trust X-Forwarded-For if behind a trusted proxy, or use the actual connection IP

## MEDIUM-5: MCP_HOST defaults to 0.0.0.0
File: Dockerfile:17, .env.example:23, docker-compose.yml:8
Fix: Default to 127.0.0.1 everywhere except Dockerfile (where 0.0.0.0 is needed for container port exposure)

## MEDIUM-6: Size Limit Bypass via Chunked Transfer-Encoding
File: app.py:557-579
Fix: Implement body size check at the ASGI level, or configure Uvicorn's `limit_concurrency`

## LOW-1: describe_fields reveals filesystem path
File: app.py:752
Fix: Return only the basename or a sanitized display version

## LOW-2: source_file in search results
File: app.py:493
Fix: Remove or hash the source_file field before returning to HTTP clients

## LOW-3: Dockerfile runs as root
File: Dockerfile
Fix: Add `RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app` and `USER appuser`

## LOW-4: Unpinned uv:latest in Dockerfile
File: Dockerfile:6
Fix: `COPY --from=ghcr.io/astral-sh/uv:0.5.x /uv /usr/local/bin/uv` (pin a digest)

## LOW-5: docker-compose missing hardening
File: docker-compose.yml
Fix: Add `security_opt: [no-new-privileges:true]`, `read_only: true`, `cap_drop: [ALL]`

## LOW-6: No TLS
Fix: Deploy behind a TLS-terminating reverse proxy (Caddy, nginx, Cloudflare Tunnel)
     or configure Uvicorn with SSL certs

## LOW-7: Test token too weak
File: tests/mcp/conftest.py:16
Value: "test-token-12345678" (20 chars, passes 16-char minimum but contains "token" keyword)
Fix: Use a stronger test token like `secrets.token_urlsafe(32)`; this is test-only so LOW risk
