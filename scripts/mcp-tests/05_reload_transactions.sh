#!/usr/bin/env bash
set -euo pipefail

MCP_URL="${MCP_URL:-http://localhost:6668/mcp/}"
AUTH_HEADER=()
if [[ -n "${MCP_AUTH_TOKEN:-}" ]]; then
  AUTH_HEADER=(-H "Authorization: Bearer ${MCP_AUTH_TOKEN}")
fi

curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  "${AUTH_HEADER[@]}" \
  -d '{
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
          "name": "reload_transactions",
          "arguments": {}
        }
      }' | python -m json.tool
