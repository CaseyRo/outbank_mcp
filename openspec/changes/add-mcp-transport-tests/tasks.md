## 1. Test infrastructure setup
- [x] 1.1 Review existing bash test scripts in `scripts/mcp-tests/` to understand current coverage
- [x] 1.2 Add pytest and mcp test dependencies to pyproject.toml
- [x] 1.3 Create test directory structure (tests/ or tests/mcp/)
- [x] 1.4 Create test utilities for stdio transport (spawn process, send JSON-RPC, read responses)
- [x] 1.5 Create test utilities for HTTP transport (make requests with proper headers, reuse patterns from bash scripts)

## 2. Simple query tests
- [x] 2.1 Test tools/list for stdio transport
- [x] 2.2 Test tools/list for HTTP transport
- [x] 2.3 Test search_transactions with query only (stdio)
- [x] 2.4 Test search_transactions with query only (HTTP)
- [x] 2.5 Test search_transactions with single filter like account (stdio)
- [x] 2.6 Test search_transactions with single filter like account (HTTP)

## 3. Advanced query tests
- [x] 3.1 Test search_transactions with multiple filters (account + date range) for stdio
- [x] 3.2 Test search_transactions with multiple filters (account + date range) for HTTP
- [x] 3.3 Test search_transactions with amount range filters for stdio
- [x] 3.4 Test search_transactions with amount range filters for HTTP
- [x] 3.5 Test search_transactions with sorting options for stdio
- [x] 3.6 Test search_transactions with sorting options for HTTP
- [x] 3.7 Test search_transactions with max_results limit for stdio
- [x] 3.8 Test search_transactions with max_results limit for HTTP

## 4. Error handling and edge cases
- [x] 4.1 Test invalid JSON-RPC requests for both transports
- [x] 4.2 Test missing required parameters for both transports
- [x] 4.3 Test HTTP auth when enabled for HTTP transport
- [x] 4.4 Test empty result sets for both transports

## 5. Documentation and validation
- [x] 5.1 Document how to run tests (pytest commands for each transport)
- [x] 5.2 Add README or docstring explaining test structure
- [x] 5.3 Verify tests pass for both stdio and HTTP modes
- [x] 5.4 Ensure tests can run with sample CSV data
