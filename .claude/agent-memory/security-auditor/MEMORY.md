# Security Auditor Memory - mcp_outbank

## Project Overview
Local-first MCP server exposing personal Outbank CSV banking transaction data.
Dual transport: stdio (local) and HTTP (network-accessible).
FastMCP 3.0.2, Python 3.11 (Docker) / 3.14 (local venv), Uvicorn/Starlette.

## Key Files
- `/Users/caseyromkes/dev/mcp_outbank/app.py` - Main server (middleware, tools, data loading)
- `/Users/caseyromkes/dev/mcp_outbank/exclusion_filters.py` - Category/tag exclusion filters
- `/Users/caseyromkes/dev/mcp_outbank/pyproject.toml` - Dependencies (no python-multipart in direct deps)
- `/Users/caseyromkes/dev/mcp_outbank/Dockerfile` - python:3.11-slim, uv:latest (unpinned), runs as root
- `/Users/caseyromkes/dev/mcp_outbank/docker-compose.yml` - No security hardening options
- `/Users/caseyromkes/dev/mcp_outbank/.env` - Contains live auth token (gitignored correctly)
- `/Users/caseyromkes/dev/mcp_outbank/logs/audit.log` - JSON audit trail

## Authentication Pattern
- HTTP transport: Bearer token via `Authorization` header, checked in `HTTPAuthMiddleware.on_request()`
- Token required, validated at startup for length (>=16) and weak patterns
- Bearer token comparison uses `!=` operator (NOT timing-safe - should use hmac.compare_digest)
- stdio transport: no auth (bypasses all HTTP middleware) - by design

## Known Vulnerabilities (First Audit - 2026-02-26)
1. MEDIUM: Timing attack on bearer token comparison (app.py:541, use hmac.compare_digest)
2. MEDIUM: Unbounded max_results allows bulk data exfiltration in one call
3. MEDIUM: No upper bound on query string length (CPU DoS via SequenceMatcher)
4. MEDIUM: X-Forwarded-For trusted without validation (IP spoofing in audit log)
5. MEDIUM: MCP_HOST defaults to 0.0.0.0 in Dockerfile and .env.example
6. MEDIUM: Request size limit bypassable via chunked Transfer-Encoding
7. LOW: describe_fields exposes full filesystem CSV path to HTTP clients
8. LOW: search_transactions returns source_file (CSV filename) in every result
9. LOW: reload_transactions tool has no additional authz beyond bearer token
10. LOW: Dockerfile runs as root, no non-root USER, no read_only filesystem
11. LOW: uv:latest and python:3.11-slim unpinned (supply chain)
12. LOW: docker-compose missing security_opt, cap_drop, read_only
13. LOW: No TLS - bearer token transmitted in plaintext over HTTP
14. LOW: Test token "test-token-12345678" in conftest.py is 20 chars but weak
15. INFO: exclusion_filters reads os.getenv() per transaction (perf, not security)
16. INFO: All transaction data in plain module-level memory (expected for local tool)

## What Is Correctly Secured
- .gitignore properly excludes .env, *.log, outbank_exports/
- Live .env has a strong 43-char random token (q0mTaNGwNskGpykHr9u5JJrargWq3X6zVbI62fewZEw)
- .env was never committed to git history
- CSV volume mounted read-only (:ro) in docker-compose
- Token security validation at startup (length, weak pattern checks)
- pre-commit hooks include detect-private-key, bandit, ruff
- python-multipart patched to 0.0.22 (CVE fix in recent commit)
- No SQL injection surface (in-memory data store)
- No template rendering / XSS surface
- Exclusion filters prevent sensitive categories from loading into memory
- audit logging captures tool name, parameters, client IP (for HTTP)

## See Also
- `findings.md` for detailed remediation code examples
