# MCP Transport Tests

Automated tests for validating MCP server functionality across both stdio and HTTP transport modes.

## Overview

These tests verify that the MCP server works correctly regardless of transport mode:
- **Stdio transport**: Tests spawn the server process and communicate via stdin/stdout
- **HTTP transport**: Tests make HTTP requests to a running server. The service uses HTTP-only (no SSE streaming) and returns complete JSON responses. FastMCP uses SSE format internally, but responses are parsed transparently to provide pure JSON.

## Prerequisites

1. Install test dependencies:
   ```bash
   uv sync --group dev
   ```

2. For stdio tests: No server setup needed (tests spawn the server automatically)

3. For HTTP tests: **You must start the MCP server manually** before running HTTP tests:
   ```bash
   # In a separate terminal, start the server:
   MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=6668 uv run python app.py
   
   # Then run tests in another terminal
   uv run pytest tests/mcp/test_simple_queries.py::TestHttpSimpleQueries
   ```
   
   **Note**: If the server is not running, HTTP tests will fail with connection errors or 406 errors. The tests will skip automatically if the server is unreachable.

4. Ensure sample CSV data is available (tests will work with empty data but may have fewer assertions)

## Running Tests

### Run all tests
```bash
uv run pytest tests/
```

### Run stdio transport tests only
```bash
uv run pytest tests/mcp/test_simple_queries.py::TestStdioSimpleQueries
uv run pytest tests/mcp/test_advanced_queries.py::TestStdioAdvancedQueries
uv run pytest tests/mcp/test_error_handling.py::TestStdioErrorHandling
```

### Run HTTP transport tests only
```bash
uv run pytest tests/mcp/test_simple_queries.py::TestHttpSimpleQueries
uv run pytest tests/mcp/test_advanced_queries.py::TestHttpAdvancedQueries
uv run pytest tests/mcp/test_error_handling.py::TestHttpErrorHandling
```

### Run exclusion filter tests
```bash
# Unit tests for exclusion filter logic
uv run pytest tests/mcp/test_exclusion_filters.py::TestExclusionFilterLogic -v

# Integration tests with stdio transport
uv run pytest tests/mcp/test_exclusion_filters.py::TestStdioExclusionFilters -v

# Run all exclusion filter tests
uv run pytest tests/mcp/test_exclusion_filters.py -v
```

### Run specific test
```bash
uv run pytest tests/mcp/test_simple_queries.py::TestStdioSimpleQueries::test_tools_list
```

## Test Logs

Test logs are automatically saved to the `test-logs/` directory. The system keeps the last 3 test runs:

- Current run: `test-logs/pytest.log`
- Previous runs: `test-logs/pytest-YYYYMMDD-HHMMSS.log` (timestamped)

Old log files (beyond the last 3) are automatically cleaned up when tests run. Logs include:
- Test execution details
- INFO level messages
- Timestamps for each log entry

## Test Structure

- `conftest.py`: Test fixtures and utilities (StdioMCPClient, HttpMCPClient, workflow_context)
- `test_simple_queries.py`: Basic tests (tool discovery, simple searches)
- `test_advanced_queries.py`: Complex tests (multi-filter, sorting, pagination)
- `test_error_handling.py`: Error cases and edge conditions
- `test_exclusion_filters.py`: **Transaction exclusion filter tests** - validates category and tag exclusion functionality (see below)
- `test_user_workflow.py`: **Full user workflow test** - simulates normal MCP server usage (see below)
- `features/`: **BDD feature files** - Gherkin scenarios for workflow tests (see BDD Workflow Tests below)
- `step_defs/`: **BDD step definitions** - Python implementations for Gherkin steps

## Transaction Exclusion Filter Tests

The `test_exclusion_filters.py` test suite validates the transaction exclusion filter functionality. These tests verify:

1. **Unit Tests** (`TestExclusionFilterLogic`):
   - Parsing of exclusion lists from environment variables
   - Case-insensitive matching logic
   - Partial matching behavior
   - Empty list handling
   - Transaction exclusion decision logic

2. **Integration Tests** (`TestStdioExclusionFilters`):
   - Exclusion filters applied during CSV loading
   - Category-based exclusion
   - Tag-based exclusion
   - Case-insensitive matching in real scenarios
   - Empty exclusion list behavior

These tests use temporary CSV files to verify that excluded transactions are not loaded into the transaction store and do not appear in search results.

## Full User Workflow Test

The `test_user_workflow.py` test simulates a realistic user workflow and outputs results in nicely formatted JSON. This test demonstrates:

1. **Tool Discovery**: Lists available tools
2. **Data Reload**: Reloads CSV data from the configured directory
3. **Simple Search**: Performs a basic text search query
4. **Filtered Search**: Performs a search with date range filters
5. **Amount Range Search**: Performs a search filtered by amount range

### Running the User Workflow Test

**Stdio transport:**
```bash
uv run pytest tests/mcp/test_user_workflow.py::TestStdioUserWorkflow::test_full_user_workflow -v -s
```

**HTTP transport:**
```bash
# Start server first (in another terminal):
MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=6668 uv run python app.py

# Then run the test:
uv run pytest tests/mcp/test_user_workflow.py::TestHttpUserWorkflow::test_full_user_workflow -v -s
```

The `-s` flag ensures output is displayed (including the formatted JSON workflow results).

### Workflow Test Output

The test outputs a complete JSON workflow summary showing:
- Each step of the workflow
- Request details for each step
- Response summaries (parsed and formatted)
- Sample results from searches
- Reload statistics

This output is printed to stdout during test execution and is also captured in the test logs (`test-logs/pytest.log`).

See [`USER_WORKFLOW.md`](USER_WORKFLOW.md) for detailed documentation of the workflow test, including example output and use cases.

## BDD Workflow Tests

The test suite includes **Behavior-Driven Development (BDD)** workflow tests using `pytest-bdd` and Gherkin feature files. These tests provide human-readable scenarios that document expected behavior and serve as living documentation.

### Overview

BDD tests are organized into:
- **Feature files** (`tests/features/*.feature`): Gherkin scenarios written in plain English
- **Step definitions** (`tests/step_defs/test_*.py`): Python implementations that execute the scenarios

### Available BDD Workflows

#### 1. Monthly Expense Analysis (`monthly_expense.feature`)
Analyzes monthly expenses with date range filtering and expense calculations.

**Scenarios:**
- Analyze expenses for a specific month
- Analyze expenses for multiple months (Scenario Outline)

**Run:**
```bash
uv run pytest tests/step_defs/test_monthly_expense.py -v
```

#### 2. Account Reconciliation (`account_reconciliation.feature`)
Reconciles transactions for a specific account with date filtering.

**Scenarios:**
- Reconcile checking account for date range

**Run:**
```bash
uv run pytest tests/step_defs/test_account_reconciliation.py -v
```

#### 3. Progressive Refinement (`progressive_refinement.feature`)
Demonstrates narrowing down search results by progressively adding filters.

**Scenarios:**
- Narrow down search with multiple filters (query → date → amount)

**Run:**
```bash
uv run pytest tests/step_defs/test_progressive_refinement.py -v
```

#### 4. Invalid Input Handling (`invalid_inputs.feature`)
Tests error handling for various invalid input scenarios.

**Scenarios:**
- Invalid date range (start after end)
- Invalid amount range (min greater than max)
- Invalid date format
- Conflicting date filters

**Run:**
```bash
uv run pytest tests/step_defs/test_invalid_inputs.py -v
```

#### 5. Data State Management (`data_state.feature`)
Tests data consistency and state management across operations.

**Scenarios:**
- Search before reload auto-loads data
- Multiple reloads maintain consistency
- Data consistency across searches

**Run:**
```bash
uv run pytest tests/step_defs/test_data_state.py -v
```

#### 6. HTTP Authentication (`http_auth.feature`)
Tests HTTP authentication scenarios (HTTP transport only).

**Scenarios:**
- Unauthorized access without token
- Invalid token is rejected
- Valid token allows access

**Run:**
```bash
uv run pytest tests/step_defs/test_http_auth.py -v -m http_only
```

### Running BDD Tests

**Run all BDD tests:**
```bash
uv run pytest tests/step_defs/ -v
```

**Run specific feature:**
```bash
uv run pytest tests/step_defs/test_monthly_expense.py -v
```

**Run with tags/markers:**
```bash
# Run stdio transport tests
uv run pytest -m "stdio" tests/step_defs/

# Run HTTP transport tests
uv run pytest -m "http" tests/step_defs/

# Run integration workflow tests
uv run pytest -m "integration" tests/step_defs/
```

**Run specific scenario:**
```bash
uv run pytest tests/step_defs/test_monthly_expense.py -k "Analyze expenses for January"
```

### Example Feature File

```gherkin
Feature: Monthly Expense Analysis
  As a user
  I want to analyze my monthly expenses
  So that I can understand my spending patterns

  Scenario: Analyze expenses for January 2024
    Given the MCP server is running
    And CSV data is loaded
    When I search for transactions from "2024-01-01" to "2024-01-31"
    And I calculate expense totals
    Then I should see expense summary with transaction count
    And I should see total expenses amount
    And I should see top expense categories
```

### Benefits of BDD Approach

- **Readability**: Feature files are human-readable specifications
- **Documentation**: Features serve as living documentation
- **Collaboration**: Non-technical stakeholders can read and contribute
- **Maintainability**: Clear separation between scenarios and implementation
- **Reusability**: Step definitions can be shared across features
- **Reporting**: pytest-bdd integrates with pytest's reporting

### BDD Test Structure

```
tests/
  features/
    monthly_expense.feature          # Gherkin scenarios
    account_reconciliation.feature
    progressive_refinement.feature
    invalid_inputs.feature
    data_state.feature
    http_auth.feature
  step_defs/
    test_monthly_expense.py          # Step definitions
    test_account_reconciliation.py
    test_progressive_refinement.py
    test_invalid_inputs.py
    test_data_state.py
    test_http_auth.py
```

### Writing New BDD Tests

1. **Create feature file** in `tests/features/` with Gherkin scenarios
2. **Create step definitions** in `tests/step_defs/` that link to the feature file
3. **Use shared fixtures** like `stdio_client`, `http_client`, `workflow_context`
4. **Run tests** to verify scenarios work correctly

Example step definition:
```python
from pytest_bdd import scenarios, given, when, then, parsers

scenarios('../features/my_feature.feature')

@given("the MCP server is running")
def server_running(stdio_client):
    assert stdio_client.process.poll() is None
```

## Environment Variables

For HTTP tests (authentication is mandatory):
```bash
export TEST_MCP_AUTH_TOKEN=your-test-token
MCP_TRANSPORT=http MCP_HTTP_AUTH_TOKEN=your-test-token \
  MCP_HOST=127.0.0.1 MCP_PORT=6668 uv run python app.py
```

## OpenAI MCP Compliance

The test suite is verified to be compliant with OpenAI's MCP specification. See [`MCP_COMPLIANCE.md`](MCP_COMPLIANCE.md) for:
- Compliance verification checklist
- JSON-RPC 2.0 format validation
- Response structure validation
- Transport-specific requirements (stdio initialization, HTTP headers)
- Recommended enhancements

## Notes

- **Stdio tests**: Automatically spawn and manage the server process - no manual setup needed
- **HTTP tests**: Require a manually started server (see Prerequisites above)
  - If server is not running, tests will skip with a helpful message
  - If server returns 406 errors, check that it's running with correct transport mode
- Tests are designed to work with or without CSV data (empty results are handled gracefully)
- The existing bash scripts in `scripts/mcp-tests/` remain as reference/fallback for HTTP-only manual testing
