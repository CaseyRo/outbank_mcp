#!/usr/bin/env bash
set -euo pipefail

MCP_URL="${MCP_URL:-http://localhost:6668/mcp}"

curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d '{
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
          "name": "describe_fields",
          "arguments": {}
        }
      }' | python -m json.tool
