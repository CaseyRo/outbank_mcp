"""Error handling and edge case tests for both transports."""

import json

import pytest
import requests


class TestStdioErrorHandling:
    """Error handling tests for stdio transport."""

    def test_invalid_json_rpc_request(self, stdio_client):
        """Test handling of invalid JSON-RPC request."""
        # Send malformed request directly
        stdio_client.process.stdin.write("invalid json\n")
        stdio_client.process.stdin.flush()
        # Server should handle gracefully - might return error or ignore
        # We just verify it doesn't crash
        assert stdio_client.process.poll() is None

    def test_empty_result_set(self, stdio_client):
        """Test search with filter that matches no transactions."""
        # Use a filter that definitely won't match (future date)
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {
                    "date_start": "2099-01-01",
                    "date_end": "2099-12-31",
                    "max_results": 10,
                },
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        data = json.loads(content["text"])
        assert "results" in data
        assert isinstance(data["results"], list)
        assert "summary" in data
        assert data["summary"]["matched"] == 0
        assert len(data["results"]) == 0


class TestHttpErrorHandling:
    """Error handling tests for HTTP transport."""

    def test_invalid_json_rpc_request(self, http_client):
        """Test handling of invalid JSON-RPC request."""
        # Send malformed request (must include auth header to pass auth layer)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {http_client.auth_token}",
        }
        response = requests.post(
            http_client.url,
            data="invalid json",
            headers=headers,
            timeout=5,
        )
        # Should return error response (401 is possible if auth rejects the
        # session, 406 is also acceptable for FastMCP)
        assert response.status_code in [400, 401, 406, 500]
        if response.status_code not in [401, 406]:
            data = response.json()
            assert "error" in data

    def test_empty_result_set(self, http_client):
        """Test search with filter that matches no transactions."""
        # Use a filter that definitely won't match (future date)
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {
                    "date_start": "2099-01-01",
                    "date_end": "2099-12-31",
                    "max_results": 10,
                },
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        data = json.loads(content["text"])
        assert "results" in data
        assert isinstance(data["results"], list)
        assert "summary" in data
        assert data["summary"]["matched"] == 0
        assert len(data["results"]) == 0

    def test_http_auth_required(self, http_client_with_auth):
        """Test HTTP auth is mandatory - authenticated requests should succeed."""
        # HTTP transport requires authentication - test that authenticated requests work
        # Note: This assumes server is running with TEST_MCP_AUTH_TOKEN
        try:
            response = http_client_with_auth.send_request("tools/list")
            assert "result" in response
        except requests.HTTPError as e:
            # If auth fails, that's a problem since auth is mandatory
            pytest.fail(f"Authenticated request failed (auth is mandatory): {e}")

    def test_http_auth_without_token_fails(self, http_client_no_auth):
        """Test that requests without token fail (auth is mandatory for HTTP transport)."""
        # HTTP transport requires authentication - requests without token
        # should fail with HTTP 401 from the auth layer.
        with pytest.raises(requests.HTTPError) as exc_info:
            http_client_no_auth.send_request("tools/list")
        assert exc_info.value.response.status_code == 401
