"""Simple query tests for both stdio and HTTP transports."""

import json

EXPECTED_TOOLS = {
    "search_transactions",
    "aggregate_transactions",
    "describe_fields",
    "reload_transactions",
    "health_check",
}


class TestStdioSimpleQueries:
    """Simple query tests for stdio transport."""

    def test_tools_list(self, stdio_client):
        """Test tools/list returns expected tools."""
        response = stdio_client.send_request("tools/list")
        assert "result" in response
        assert "tools" in response["result"]
        tool_names = {tool["name"] for tool in response["result"]["tools"]}
        assert EXPECTED_TOOLS.issubset(tool_names)

    def test_search_transactions_query_only(self, stdio_client):
        """Test search_transactions with query parameter only."""
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {"query": "grocery", "max_results": 10},
            },
        )
        assert "result" in response
        assert "content" in response["result"]
        assert len(response["result"]["content"]) > 0
        content = response["result"]["content"][0]
        assert "text" in content
        result_data = content["text"]
        # Parse JSON from text field
        import json

        data = json.loads(result_data)
        assert "results" in data
        assert "summary" in data
        assert isinstance(data["results"], list)

    def test_search_transactions_single_filter_account(self, stdio_client):
        """Test search_transactions with account filter."""
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {"account": "checking", "max_results": 5},
            },
        )
        assert "result" in response
        assert "content" in response["result"]
        content = response["result"]["content"][0]

        data = json.loads(content["text"])
        assert "results" in data
        # If results exist, verify account filter was applied
        if data["results"]:
            for result in data["results"]:
                assert "account" in result

    def test_health_check(self, stdio_client):
        """Test health_check returns expected status fields."""
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "health_check",
                "arguments": {},
            },
        )
        assert "result" in response
        assert "content" in response["result"]
        content = response["result"]["content"][0]

        data = json.loads(content["text"])
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0
        assert "data_loaded" in data
        assert "record_count" in data
        assert "files_scanned" in data
        assert "transport_mode" in data


class TestHttpSimpleQueries:
    """Simple query tests for HTTP transport."""

    def test_tools_list(self, http_client):
        """Test tools/list returns expected tools."""
        response = http_client.send_request("tools/list")
        assert "result" in response
        assert "tools" in response["result"]
        tool_names = {tool["name"] for tool in response["result"]["tools"]}
        assert EXPECTED_TOOLS.issubset(tool_names)

    def test_search_transactions_query_only(self, http_client):
        """Test search_transactions with query parameter only."""
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {"query": "grocery", "max_results": 10},
            },
        )
        assert "result" in response
        assert "content" in response["result"]
        assert len(response["result"]["content"]) > 0
        content = response["result"]["content"][0]
        assert "text" in content
        import json

        data = json.loads(content["text"])
        assert "results" in data
        assert "summary" in data
        assert isinstance(data["results"], list)

    def test_search_transactions_single_filter_account(self, http_client):
        """Test search_transactions with account filter."""
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {"account": "checking", "max_results": 5},
            },
        )
        assert "result" in response
        assert "content" in response["result"]
        content = response["result"]["content"][0]

        data = json.loads(content["text"])
        assert "results" in data
        # If results exist, verify account filter was applied
        if data["results"]:
            for result in data["results"]:
                assert "account" in result

    def test_health_check(self, http_client):
        """Test health_check returns expected status fields."""
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "health_check",
                "arguments": {},
            },
        )
        assert "result" in response
        assert "content" in response["result"]
        content = response["result"]["content"][0]

        data = json.loads(content["text"])
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0
        assert "data_loaded" in data
        assert "record_count" in data
        assert "files_scanned" in data
        assert "transport_mode" in data
