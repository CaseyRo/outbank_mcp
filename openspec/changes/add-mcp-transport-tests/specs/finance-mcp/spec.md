## ADDED Requirements

### Requirement: Automated MCP Transport Tests
The system SHALL provide automated tests that validate MCP server functionality for both stdio and HTTP transport modes.

#### Scenario: Stdio transport tests run successfully
- **WHEN** tests are executed with stdio transport mode
- **THEN** all test cases pass by spawning the MCP server process and communicating via stdin/stdout

#### Scenario: HTTP transport tests run successfully
- **WHEN** tests are executed with HTTP transport mode
- **THEN** all test cases pass by making HTTP requests to the MCP server endpoint

### Requirement: Simple Query Test Coverage
The test suite SHALL include simple query tests that validate basic MCP tool functionality.

#### Scenario: Tool discovery test for stdio
- **WHEN** a tools/list request is sent via stdio transport
- **THEN** the response includes all expected tools (search_transactions, describe_fields, reload_transactions)

#### Scenario: Basic search query test for stdio
- **WHEN** a search_transactions call is made via stdio with only a query parameter
- **THEN** the response contains matching transactions with proper structure

#### Scenario: Basic search query test for HTTP
- **WHEN** a search_transactions call is made via HTTP with only a query parameter
- **THEN** the response contains matching transactions with proper structure

#### Scenario: Single filter query test
- **WHEN** a search_transactions call is made with a single filter (e.g., account name) via both transports
- **THEN** results are filtered correctly and responses match between transports

### Requirement: Advanced Query Test Coverage
The test suite SHALL include advanced query tests that validate complex filtering, sorting, and pagination.

#### Scenario: Multi-filter query test
- **WHEN** a search_transactions call is made with multiple filters (account, date range, amount range) via both transports
- **THEN** results match all filter criteria and responses are consistent between transports

#### Scenario: Sorting validation test
- **WHEN** search_transactions calls are made with different sort options (-date, date, -amount, amount) via both transports
- **THEN** results are sorted correctly according to the specified option

#### Scenario: Pagination test
- **WHEN** search_transactions calls are made with max_results limits via both transports
- **THEN** the number of returned results respects the limit and summary indicates truncation when applicable

### Requirement: Error Handling Test Coverage
The test suite SHALL validate error handling and edge cases for both transports.

#### Scenario: Invalid request handling
- **WHEN** invalid JSON-RPC requests are sent via both transports
- **THEN** appropriate error responses are returned

#### Scenario: HTTP authentication test
- **WHEN** HTTP transport tests run with authentication enabled
- **THEN** requests without valid bearer tokens are rejected and authenticated requests succeed

#### Scenario: Empty result set handling
- **WHEN** search queries match no transactions via both transports
- **THEN** responses indicate zero matches with empty results array
