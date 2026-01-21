## MODIFIED Requirements
### Requirement: HTTP Bearer Token Auth
The MCP service SHALL require token authentication for all HTTP transport requests. When HTTP transport is used, `MCP_HTTP_AUTH_TOKEN` MUST be configured, and requests without a matching bearer token MUST be rejected. HTTP transport SHALL fail to start if `MCP_HTTP_AUTH_TOKEN` is not configured.

#### Scenario: HTTP transport requires token at startup
- **WHEN** HTTP transport is selected (`MCP_TRANSPORT=http`) and `MCP_HTTP_AUTH_TOKEN` is not set
- **THEN** the service fails to start with a clear error message requiring token configuration

#### Scenario: HTTP auth enforced for all requests
- **WHEN** HTTP transport is used and a client request omits or provides an invalid bearer token
- **THEN** the MCP service rejects the request with an authentication error

#### Scenario: Valid token allows HTTP access
- **WHEN** HTTP transport is used and a client provides a valid bearer token matching `MCP_HTTP_AUTH_TOKEN`
- **THEN** the MCP service processes the request normally

#### Scenario: Stdio transport requires no auth
- **WHEN** stdio transport is used (`MCP_TRANSPORT=stdio`)
- **THEN** authentication is not required and requests proceed without token validation

## MODIFIED Requirements
### Requirement: Security documentation
The system SHALL provide documentation describing that HTTP transport requires authentication via `MCP_HTTP_AUTH_TOKEN`, how to bind the service to local-only interfaces, and that exposing the MCP service publicly is out of scope and at the user's risk.

#### Scenario: Security guide explains mandatory HTTP auth
- **WHEN** a user reads the security documentation
- **THEN** they understand that HTTP transport requires `MCP_HTTP_AUTH_TOKEN` to be set, how to configure local-only binding, and the risks of public exposure
