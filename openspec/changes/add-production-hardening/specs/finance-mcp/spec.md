## ADDED Requirements

### Requirement: Rate Limiting
The MCP server SHALL enforce rate limiting for HTTP transport to prevent abuse.

#### Scenario: Rate limit not exceeded
- **WHEN** a client makes requests within the configured rate limit
- **THEN** all requests are processed normally

#### Scenario: Rate limit exceeded
- **WHEN** a client exceeds the configured rate limit (default: 100/minute)
- **THEN** subsequent requests receive a rate limit error until the window resets

#### Scenario: Rate limit configurable
- **WHEN** `MCP_RATE_LIMIT` environment variable is set (e.g., "50/minute", "1000/hour")
- **THEN** the server uses the configured rate limit instead of the default

### Requirement: Request Timeout
The MCP server SHALL enforce request timeouts to prevent hung connections.

#### Scenario: Request completes within timeout
- **WHEN** a tool call completes within the configured timeout (default: 60 seconds)
- **THEN** the response is returned normally

#### Scenario: Request exceeds timeout
- **WHEN** a tool call takes longer than the configured timeout
- **THEN** the request is terminated with a timeout error

#### Scenario: Timeout configurable
- **WHEN** `MCP_REQUEST_TIMEOUT` environment variable is set (integer seconds)
- **THEN** the server uses the configured timeout instead of the default

### Requirement: Request Size Limiting
The MCP server SHALL enforce maximum request size limits for HTTP transport.

#### Scenario: Request within size limit
- **WHEN** a request body is within the configured size limit (default: 1MB)
- **THEN** the request is processed normally

#### Scenario: Request exceeds size limit
- **WHEN** a request body exceeds the configured size limit
- **THEN** the request is rejected with a payload too large error

#### Scenario: Size limit configurable
- **WHEN** `MCP_MAX_REQUEST_SIZE` environment variable is set (integer bytes)
- **THEN** the server uses the configured limit instead of the default

### Requirement: Audit Logging
The MCP server SHALL log all tool invocations for audit trail purposes.

#### Scenario: Tool invocation logged
- **WHEN** any MCP tool is invoked
- **THEN** an audit log entry is written containing timestamp, tool name, and parameters

#### Scenario: Audit log includes client info for HTTP
- **WHEN** a tool is invoked via HTTP transport
- **THEN** the audit log entry includes client IP address

#### Scenario: Audit logging configurable
- **WHEN** `MCP_AUDIT_ENABLED` is set to "false"
- **THEN** audit logging is disabled

#### Scenario: Audit log location configurable
- **WHEN** `MCP_AUDIT_LOG` environment variable is set
- **THEN** audit logs are written to the specified file path

### Requirement: Health Check Tool
The MCP server SHALL provide a health_check tool for monitoring server status.

#### Scenario: Health check returns server status
- **WHEN** the health_check tool is invoked
- **THEN** it returns status, uptime, data_loaded flag, record_count, files_scanned, and transport_mode

#### Scenario: Health check requires auth for HTTP
- **WHEN** health_check is invoked via HTTP without valid bearer token
- **THEN** the request is rejected with an authentication error

### Requirement: Version History
The project SHALL maintain a CHANGELOG.md documenting version history.

#### Scenario: CHANGELOG exists
- **WHEN** reviewing the project root
- **THEN** a CHANGELOG.md file exists with version history entries

#### Scenario: CHANGELOG follows format
- **WHEN** reading CHANGELOG.md
- **THEN** entries follow Keep a Changelog format with version numbers and dates
