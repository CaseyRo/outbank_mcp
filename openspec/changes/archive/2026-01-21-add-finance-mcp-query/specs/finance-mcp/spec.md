## ADDED Requirements
### Requirement: MCP Query Service
The system SHALL provide a FastMCP-based Python service that exposes tools for querying NocoDB finance data via its API.

#### Scenario: Service is running
- **WHEN** the Docker Compose stack is started
- **THEN** the MCP service is reachable on the configured host port

### Requirement: Configurable MCP Port
The system SHALL expose the MCP service on a port set by environment configuration, defaulting to `6668`.

#### Scenario: Default port
- **WHEN** no port is configured
- **THEN** the MCP service listens on port `6668`

#### Scenario: Custom port
- **WHEN** a custom MCP port is configured
- **THEN** the MCP service listens on that port

### Requirement: Fuzzy Transaction Search
The system SHALL provide a tool that returns matching transactions using fuzzy search over transaction fields.

#### Scenario: Query by account and date range
- **WHEN** the caller provides an account name and a date range
- **THEN** the tool returns transactions matching those filters using fuzzy matching

### Requirement: Optional Search Filters
The system SHALL accept optional filters for account, IBAN, amount, amount range, date, and date range, and allow combinations of these filters in a single query.

#### Scenario: Query by amount range and IBAN
- **WHEN** the caller provides an amount range and an IBAN
- **THEN** the tool returns matching transactions
