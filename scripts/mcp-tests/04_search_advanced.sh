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
        "id": 4,
        "method": "tools/call",
        "params": {
          "name": "search_transactions",
          "arguments": {
            "query": "rent",
            "account": "checking",
            "iban": "NL00TEST123",
            "amount_min": -1500,
            "amount_max": -500,
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "sort": "-date",
            "max_results": 5
          }
        }
      }' | python -m json.tool
