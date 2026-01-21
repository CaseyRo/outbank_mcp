# User Workflow Test

## Overview

The `test_user_workflow.py` test simulates a realistic user workflow with the MCP server. It demonstrates the complete flow of:
1. Discovering available tools
2. Reloading CSV data
3. Performing various search queries

## Test Process

The workflow test executes 5 sequential steps:

### Step 1: Discover Tools
- **Action**: `tools/list`
- **Purpose**: Lists all available MCP tools
- **Output**: Number of tools found and their details

### Step 2: Reload Transactions
- **Action**: `tools/call` with `reload_transactions`
- **Purpose**: Reloads CSV data from the configured directory
- **Output**: Statistics about loaded records (total, new, removed, files scanned)

### Step 3: Simple Search
- **Action**: `tools/call` with `search_transactions` (query: "grocery")
- **Purpose**: Performs a basic text search
- **Output**: Number of results found and sample results

### Step 4: Filtered Search
- **Action**: `tools/call` with `search_transactions` (query: "payment", date range: 2024-01-01 to 2024-12-31)
- **Purpose**: Demonstrates search with date filters
- **Output**: Results count, filters applied, and sample results

### Step 5: Amount Range Search
- **Action**: `tools/call` with `search_transactions` (amount range: -1000 to -100)
- **Purpose**: Demonstrates search filtered by amount range
- **Output**: Results count, amount range, and sample results

## Running the Test

### Stdio Transport
```bash
uv run pytest tests/mcp/test_user_workflow.py::TestStdioUserWorkflow::test_full_user_workflow -v -s
```

### HTTP Transport
```bash
# Start server first (in another terminal):
MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=6668 uv run python app.py

# Then run the test:
uv run pytest tests/mcp/test_user_workflow.py::TestHttpUserWorkflow::test_full_user_workflow -v -s
```

**Note**: The `-s` flag is important to see the formatted JSON output in the console.

## Output Format

The test outputs a complete JSON workflow summary with the following structure:

```json
{
  "workflow": "stdio_user_workflow" | "http_user_workflow",
  "steps": [
    {
      "step": 1,
      "action": "discover_tools",
      "request": { "method": "tools/list", "params": {} },
      "response": { ... },
      "tools_found": 3
    },
    {
      "step": 2,
      "action": "reload_transactions",
      "request": { ... },
      "response": { ... },
      "reload_summary": {
        "total_records": 18659,
        "new_records": 18659,
        "removed_records": 0,
        "files_scanned": 1
      }
    },
    {
      "step": 3,
      "action": "simple_search",
      "request": { ... },
      "response": { ... },
      "search_summary": {
        "results_count": 0,
        "matched": 0,
        "sample_results": []
      }
    },
    {
      "step": 4,
      "action": "filtered_search",
      "request": { ... },
      "response": { ... },
      "search_summary": {
        "results_count": 3,
        "matched": 987,
        "filters_applied": { ... },
        "sample_results": [ ... ]
      }
    },
    {
      "step": 5,
      "action": "amount_range_search",
      "request": { ... },
      "response": { ... },
      "search_summary": {
        "results_count": 3,
        "matched": 1886,
        "amount_range": { "min": -1000, "max": -100 },
        "sample_results": [ ... ]
      }
    }
  ]
}
```

## Output Location

The formatted JSON output is:
- **Printed to stdout** during test execution (when using `-s` flag)
- **Captured in test logs** (`test-logs/pytest.log`) for later review
- **Included in pytest output** for both console and log files

## Example Output

When run successfully, you'll see output like:

```
================================================================================
STDIO USER WORKFLOW TEST RESULTS
================================================================================
{
  "workflow": "stdio_user_workflow",
  "steps": [
    {
      "step": 1,
      "action": "discover_tools",
      ...
    },
    ...
  ]
}
================================================================================
```

## Use Cases

This test is useful for:
- **Integration testing**: Verifying the complete workflow works end-to-end
- **Documentation**: Demonstrating how to use the MCP server
- **Debugging**: Seeing the full request/response cycle
- **Performance**: Understanding the flow of operations
- **Validation**: Ensuring all tools work together correctly

## Notes

- The test works with both stdio and HTTP transports
- Results vary based on available CSV data
- Empty results are handled gracefully
- All responses are parsed and formatted for readability
- Sample results are limited to 2 items per search for readability
