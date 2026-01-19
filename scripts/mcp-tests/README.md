# MCP Test Scripts

These scripts exercise the MCP server over HTTP using JSON-RPC.

## Prereqs
- MCP server running on `http://localhost:6668/mcp`
- Optional: set `MCP_URL` to override the endpoint
- Optional: set `MCP_AUTH_TOKEN` if HTTP auth is enabled

## Usage
```bash
export MCP_URL="http://localhost:6668/mcp"
export MCP_AUTH_TOKEN="your-secret-token"
./scripts/mcp-tests/01_list_tools.sh
./scripts/mcp-tests/02_describe_fields.sh
./scripts/mcp-tests/03_search_basic.sh
./scripts/mcp-tests/04_search_advanced.sh
```
