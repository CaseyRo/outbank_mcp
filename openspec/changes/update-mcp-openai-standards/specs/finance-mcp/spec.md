## ADDED Requirements
### Requirement: MCP Dual Transport
The system SHALL support MCP connections over both stdio and HTTP transport modes.

#### Scenario: Stdio transport enabled
- **WHEN** the service starts in stdio mode
- **THEN** tools are available over stdio without HTTP bindings

#### Scenario: HTTP transport enabled
- **WHEN** the service starts in HTTP mode
- **THEN** tools are available via the MCP HTTP endpoint

### Requirement: HTTP Bearer Token Auth
The system SHALL support a shared bearer token for HTTP requests when configured.

#### Scenario: Auth enabled with token
- **WHEN** an HTTP request omits or provides an invalid bearer token
- **THEN** the request is rejected

#### Scenario: Auth disabled
- **WHEN** HTTP auth is disabled
- **THEN** valid requests are accepted without a bearer token

### Requirement: OpenAI MCP Tool Presentation
The system SHALL expose tool metadata aligned with OpenAI MCP standards, including clear names, descriptions, and JSON schema inputs.

#### Scenario: Tool listing for approval readiness
- **WHEN** a client lists available tools
- **THEN** each tool includes a stable name, a human-readable description, and a complete input schema
