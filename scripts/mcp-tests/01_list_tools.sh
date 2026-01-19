#!/usr/bin/env bash
set -euo pipefail

MCP_URL="${MCP_URL:-http://localhost:6668/mcp}"
AUTH_HEADER=()
if [[ -n "${MCP_AUTH_TOKEN:-}" ]]; then
  AUTH_HEADER=(-H "Authorization: Bearer ${MCP_AUTH_TOKEN}")
fi

curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  "${AUTH_HEADER[@]}" \
  -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
      }' | python -m json.tool
