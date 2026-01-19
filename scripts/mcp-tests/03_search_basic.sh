#!/usr/bin/env bash
set -euo pipefail

MCP_URL="${MCP_URL:-http://localhost:6668/mcp}"

curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
          "name": "search_transactions",
          "arguments": {
            "query": "grocery",
            "max_results": 10
          }
        }
      }' | python -m json.tool
