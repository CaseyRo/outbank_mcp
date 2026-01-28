#!/usr/bin/env python3
"""Query MCP server for grocery spending in previous quarter.

Connects to an existing MCP server (HTTP or stdio mode).
"""

import json
import os
import sys
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("Error: 'requests' and 'python-dotenv' libraries required.")
    print("Install with: uv sync --group dev")
    print("Then run with: uv run python scripts/query_groceries.py")
    sys.exit(1)

# Load .env file if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class MCPClient:
    """Simple MCP client that supports both HTTP and stdio."""

    def __init__(self, url: str | None = None, auth_token: str | None = None):
        """Initialize client.

        Args:
            url: HTTP server URL (if None, uses stdio mode)
            auth_token: Bearer token for HTTP auth (required if using HTTP)
        """
        self.url = url
        self.auth_token = auth_token
        self.request_id = 0
        self.session_id = None
        self._initialized = False
        self._is_http = url is not None

    def _initialize(self):
        """Initialize MCP session."""
        if self._initialized:
            return

        if self._is_http:
            self._initialize_http()
        else:
            # Stdio mode - initialization happens via stdin/stdout
            # For this script, we'll use HTTP if available
            raise RuntimeError("Stdio mode not supported in this script. Use HTTP mode.")

    def _initialize_http(self):
        """Initialize HTTP session."""
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "grocery-query", "version": "1.0.0"},
            },
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        try:
            response = requests.post(self.url, json=init_request, headers=headers, timeout=10)
            response.raise_for_status()

            # Extract session ID
            self.session_id = response.headers.get("Mcp-Session-Id") or response.headers.get(
                "mcp-session-id"
            )

            # Send initialized notification
            if self.session_id:
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                }
                headers_with_session = headers.copy()
                headers_with_session["Mcp-Session-Id"] = self.session_id
                try:
                    requests.post(
                        self.url,
                        json=initialized_notification,
                        headers=headers_with_session,
                        timeout=10,
                    )
                except Exception:
                    pass

            self._initialized = True
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                f"Cannot connect to MCP server at {self.url}. Is the server running?"
            ) from e
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise RuntimeError("Authentication failed. Check MCP_HTTP_AUTH_TOKEN.") from e
            raise

    def send_request(self, method: str, params: dict | None = None) -> dict:
        """Send a JSON-RPC request."""
        if not self._initialized:
            self._initialize()

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {},
        }

        if self._is_http:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            }
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            if self.session_id:
                headers["Mcp-Session-Id"] = self.session_id

            response = requests.post(self.url, json=request, headers=headers, timeout=30)
            response.raise_for_status()

            # Parse response (may be SSE or JSON)
            content_type = response.headers.get("Content-Type", "")
            if "text/event-stream" in content_type:
                # Parse SSE format
                for line in response.text.strip().split("\n"):
                    if line.startswith("data: "):
                        try:
                            return json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue

            return response.json()
        else:
            raise RuntimeError("Stdio mode not supported")


def main():
    """Query grocery spending for Q4 2024."""
    # Get configuration from environment
    mcp_url = os.getenv("MCP_URL", "http://127.0.0.1:6668/mcp")
    auth_token = os.getenv("MCP_HTTP_AUTH_TOKEN") or os.getenv("TEST_MCP_AUTH_TOKEN")

    if not auth_token:
        print("⚠️  Warning: No auth token found. Set MCP_HTTP_AUTH_TOKEN if using HTTP transport.")
        print("   Attempting connection anyway...\n")
    else:
        token_preview = auth_token[:8] + "..." if len(auth_token) > 8 else auth_token
        print(f"✓ Auth token found ({len(auth_token)} characters, starts with: {token_preview})\n")

    print(f"Connecting to MCP server at {mcp_url}...")

    try:
        client = MCPClient(url=mcp_url, auth_token=auth_token)
        print("✓ Connected to MCP server")

        # Search for grocery transactions in Q4 2024 (Oct 1 - Dec 31, 2024)
        print("\nSearching for grocery transactions in Q4 2024 (Oct 1 - Dec 31, 2024)...")
        search_response = client.send_request(
            "tools/call",
            {
                "name": "search_transactions",
                "arguments": {
                    "query": "groceries",
                    "date_start": "2024-10-01",
                    "date_end": "2024-12-31",
                    "max_results": 1000,  # Get as many as possible
                    "sort": "-date",
                },
            },
        )

        if "error" in search_response:
            print(f"❌ Error: {search_response['error']}")
            return 1

        # Parse results
        if "result" not in search_response:
            print(f"❌ Unexpected response format: {search_response}")
            return 1

        result = search_response["result"]
        if "content" not in result or not result["content"]:
            print(f"❌ No content in response: {result}")
            return 1

        result_content = result["content"][0].get("text", "")
        if not result_content:
            print(f"❌ Empty content in response: {result}")
            return 1

        # Check if response is an error message (not JSON)
        if result_content.startswith("Error calling tool"):
            print(f"❌ {result_content}")
            if "Unauthorized" in result_content:
                print("\n💡 Tip: Set MCP_HTTP_AUTH_TOKEN environment variable:")
                print("   export MCP_HTTP_AUTH_TOKEN=your-token")
                print("   Or run: python scripts/generate-auth-token.py")
            return 1

        try:
            data = json.loads(result_content)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print(f"   Response text: {result_content[:200]}...")
            return 1

        transactions = data.get("results", [])
        matched = data.get("summary", {}).get("matched", 0)

        print(f"✓ Found {matched} matching transactions")
        print(f"✓ Retrieved {len(transactions)} transactions\n")

        if not transactions:
            print("No grocery transactions found in Q4 2024.")
            return 0

        # Calculate total spending (negative amounts are expenses)
        total_spent = 0.0
        grocery_transactions = []

        for tx in transactions:
            amount = tx.get("amount", 0)
            if amount < 0:  # Only count expenses (negative amounts)
                total_spent += abs(amount)
                grocery_transactions.append(tx)

        # Display results
        print("=" * 70)
        print("GROCERY SPENDING - Q4 2024 (Oct 1 - Dec 31, 2024)")
        print("=" * 70)
        print(f"\nTotal transactions found: {matched}")
        print(f"Transactions analyzed: {len(grocery_transactions)}")
        print(f"\n💰 Total spent on groceries: €{total_spent:,.2f}")
        print("\nSample transactions:")
        print("-" * 70)

        # Show first 10 transactions
        for tx in grocery_transactions[:10]:
            date = tx.get("date", "N/A")
            amount = tx.get("amount", 0)
            description = tx.get("description", tx.get("counterparty", "N/A"))
            print(f"  {date}: €{abs(amount):,.2f} - {description}")

        if len(grocery_transactions) > 10:
            print(f"  ... and {len(grocery_transactions) - 10} more transactions")

        print("=" * 70)

        return 0

    except RuntimeError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
