# Change: Add MCP transport tests for stdio and HTTP modes

## Why
The MCP server supports both stdio and HTTP transports, but currently only has manual HTTP test scripts (`scripts/mcp-tests/*.sh`). These scripts cover basic and advanced queries but only work for HTTP mode. Automated tests that validate both transport modes ensure reliability across deployment scenarios and catch regressions early. Simple and advanced query tests verify core functionality works correctly regardless of transport.

## What Changes
- Extend existing test coverage (`scripts/mcp-tests/`) to support both stdio and HTTP transports
- Add Python-based test suite that can test both transport modes (stdio via process spawning, HTTP via requests)
- Implement simple query tests (basic search_transactions calls with minimal filters) for both transports
- Implement advanced query tests (complex filters, date ranges, sorting, pagination) for both transports
- Test tool discovery (tools/list) for both transports
- Test error handling and edge cases for both transports
- Make tests runnable via pytest or similar test runner
- Document how to run tests for each transport mode
- Preserve or migrate existing bash test scripts as reference or HTTP-only fallback

## Impact
- Affected specs: finance-mcp
- Affected code: New test files, potentially test utilities/helpers
- Operational impact: Tests can be run in CI/CD or manually to validate MCP server functionality
