## ADDED Requirements
### Requirement: Optional MCP authentication
The MCP service SHALL support optional token authentication for the HTTP
transport. When authentication is enabled, requests without a matching token
MUST be rejected. When disabled, requests SHALL be accepted without
authentication checks.

#### Scenario: Auth disabled by default
- **WHEN** auth is disabled or no token is configured
- **THEN** HTTP requests proceed without authentication

#### Scenario: HTTP auth enforced
- **WHEN** HTTP auth is enabled and a client request omits or mismatches the token
- **THEN** the MCP service rejects the request with an auth error

### Requirement: Security documentation
The system SHALL provide documentation describing how to enable optional MCP
auth for HTTP transport, how to bind the service to local-only interfaces, and
that exposing the MCP service publicly is out of scope and at the user's risk.

#### Scenario: Security guide available
- **WHEN** a user reads the documentation
- **THEN** they can find a security guide that explains optional HTTP auth,
  local-only configuration, and the public exposure warning
