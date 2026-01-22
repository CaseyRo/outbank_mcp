## MODIFIED Requirements

### Requirement: FastMCP Version
The MCP server SHALL use FastMCP 3.0 or later as its framework.

#### Scenario: Server starts with FastMCP 3.0
- **WHEN** the server is started
- **THEN** it uses FastMCP version 3.x
- **AND** all tools are registered and functional

#### Scenario: Middleware works with FastMCP 3.0
- **WHEN** an HTTP request is made
- **THEN** `AuthMiddleware` with `require_auth` validates the bearer token
- **AND** rate limiting middleware enforces request limits
- **AND** request size middleware validates payload size
- **AND** audit logging middleware records the invocation

### Requirement: Backward Compatibility
The MCP server SHALL maintain all existing functionality after migration.

#### Scenario: All tools remain functional
- **WHEN** the server is migrated to FastMCP 3.0
- **THEN** `search_transactions` tool works as before
- **AND** `describe_fields` tool works as before
- **AND** `reload_transactions` tool works as before
- **AND** `health_check` tool works as before

#### Scenario: HTTP transport works
- **WHEN** using HTTP transport with FastMCP 3.0
- **THEN** bearer token authentication is required
- **AND** JSON-RPC requests are processed correctly
- **AND** responses are returned in expected format

#### Scenario: Stdio transport works
- **WHEN** using stdio transport with FastMCP 3.0
- **THEN** stdin/stdout communication works correctly
- **AND** no authentication is required

## ADDED Requirements

### Requirement: Version Pinning
The project SHALL pin FastMCP to a specific major version to prevent unexpected breaking changes.

#### Scenario: Dependency specification
- **WHEN** reviewing pyproject.toml
- **THEN** fastmcp dependency specifies version `>=3.0.0,<4.0.0`

### Requirement: Bearer Token Authentication
The MCP server SHALL use custom middleware for bearer token authentication.

#### Scenario: Authentication uses custom middleware
- **GIVEN** v3's `AuthMiddleware` is designed for OAuth/JWT tokens
- **WHEN** the server needs simple bearer token validation
- **THEN** the custom `HTTPAuthMiddleware` class validates against `MCP_HTTP_AUTH_TOKEN`
- **AND** the middleware is compatible with v3's `Middleware` base class

#### Scenario: Bearer token validation
- **WHEN** an HTTP request is made without a valid bearer token
- **THEN** the server returns 401 Unauthorized
- **AND** authentication is handled by custom `HTTPAuthMiddleware`

### Requirement: Future Auth Improvements (Out of Scope)
The following authorization features are documented as future improvements:
- Scopes-based authorization using `require_scopes`
- User identity extraction via custom `AuthContext`
- Role-based access control for tools
