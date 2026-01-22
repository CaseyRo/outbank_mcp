# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-01-22

### Changed
- **BREAKING**: Upgraded to FastMCP 3.0.0b1 (requires fastmcp>=3.0.0b1,<4.0.0)
- Updated security documentation with scopes-based auth as future improvement

### Technical Notes
- v3's `AuthMiddleware` with `require_auth` is designed for OAuth/JWT tokens
- Custom `HTTPAuthMiddleware` retained for simple bearer token validation
- All existing middleware (rate limiting, request size, audit logging) compatible with v3
- All imports and middleware patterns verified compatible with FastMCP 3.0

## [0.9.0] - 2026-01-21

### Added
- `health_check` tool for monitoring server status (uptime, record count, data status)
- Rate limiting support via `MCP_RATE_LIMIT` environment variable (HTTP transport, uses FastMCP's RateLimitingMiddleware)
- Request size limiting via `MCP_MAX_REQUEST_SIZE` environment variable (default 1MB)
- Audit logging for all tool invocations (`MCP_AUDIT_ENABLED`, `MCP_AUDIT_LOG`)
- Pre-commit hooks for code quality (ruff formatting and linting)
- Production hardening tests for rate limiting, request size limits, and audit logging
- This CHANGELOG file

### Changed
- Updated security documentation with future improvement notes for token rotation
- Improved code quality with ruff linting and formatting across codebase

## [0.1.0] - 2026-01-21

### Added
- Initial release
- MCP server with `search_transactions`, `reload_transactions`, `describe_fields` tools
- Fuzzy transaction search with filters (account, IBAN, amount, date range)
- HTTP and stdio transport support
- Bearer token authentication for HTTP transport
- Transaction exclusion filters (`EXCLUDED_CATEGORIES`, `EXCLUDED_TAGS`)
- Docker support with docker-compose
- Comprehensive test suite (pytest, BDD scenarios)

[Unreleased]: https://github.com/user/mcp_outbank/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/mcp_outbank/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/user/mcp_outbank/compare/v0.1.0...v0.9.0
[0.1.0]: https://github.com/user/mcp_outbank/releases/tag/v0.1.0
