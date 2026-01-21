"""Advanced query tests for both stdio and HTTP transports."""

import json


class TestStdioAdvancedQueries:
    """Advanced query tests for stdio transport."""

    def test_search_multiple_filters_account_date_range(self, stdio_client):
        """Test search_transactions with account and date range filters."""
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {
                    "account": "checking",
                    "date_start": "2024-01-01",
                    "date_end": "2024-12-31",
                    "max_results": 5,
                },
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        data = json.loads(content["text"])
        assert "results" in data
        assert "filters" in data
        assert data["filters"]["account"] == "checking"
        assert data["filters"]["date_start"] == "2024-01-01"
        assert data["filters"]["date_end"] == "2024-12-31"

    def test_search_amount_range_filters(self, stdio_client):
        """Test search_transactions with amount range filters."""
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {
                    "amount_min": -1500,
                    "amount_max": -500,
                    "max_results": 5,
                },
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        data = json.loads(content["text"])
        assert "results" in data
        assert "filters" in data
        assert data["filters"]["amount_min"] == -1500
        assert data["filters"]["amount_max"] == -500
        # Verify amounts are in range
        for result in data["results"]:
            if result.get("amount") is not None:
                assert -1500 <= result["amount"] <= -500

    def test_search_sorting_options(self, stdio_client):
        """Test search_transactions with different sort options."""
        sort_options = ["-date", "date", "-amount", "amount"]
        for sort_option in sort_options:
            response = stdio_client.send_request(
                "tools/call",
                params={
                    "name": "search_transactions",
                    "arguments": {"sort": sort_option, "max_results": 10},
                },
            )
            assert "result" in response
            content = response["result"]["content"][0]
            data = json.loads(content["text"])
            assert "results" in data
            assert "filters" in data
            assert data["filters"]["sort"] == sort_option

    def test_search_max_results_limit(self, stdio_client):
        """Test search_transactions respects max_results limit."""
        max_results = 3
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {"max_results": max_results},
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        data = json.loads(content["text"])
        assert "results" in data
        assert len(data["results"]) <= max_results
        if data["summary"]["matched"] > max_results:
            assert data["summary"]["truncated"] is True


class TestHttpAdvancedQueries:
    """Advanced query tests for HTTP transport."""

    def test_search_multiple_filters_account_date_range(self, http_client):
        """Test search_transactions with account and date range filters."""
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {
                    "account": "checking",
                    "date_start": "2024-01-01",
                    "date_end": "2024-12-31",
                    "max_results": 5,
                },
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        data = json.loads(content["text"])
        assert "results" in data
        assert "filters" in data
        assert data["filters"]["account"] == "checking"
        assert data["filters"]["date_start"] == "2024-01-01"
        assert data["filters"]["date_end"] == "2024-12-31"

    def test_search_amount_range_filters(self, http_client):
        """Test search_transactions with amount range filters."""
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {
                    "amount_min": -1500,
                    "amount_max": -500,
                    "max_results": 5,
                },
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        data = json.loads(content["text"])
        assert "results" in data
        assert "filters" in data
        assert data["filters"]["amount_min"] == -1500
        assert data["filters"]["amount_max"] == -500
        # Verify amounts are in range
        for result in data["results"]:
            if result.get("amount") is not None:
                assert -1500 <= result["amount"] <= -500

    def test_search_sorting_options(self, http_client):
        """Test search_transactions with different sort options."""
        sort_options = ["-date", "date", "-amount", "amount"]
        for sort_option in sort_options:
            response = http_client.send_request(
                "tools/call",
                params={
                    "name": "search_transactions",
                    "arguments": {"sort": sort_option, "max_results": 10},
                },
            )
            assert "result" in response
            content = response["result"]["content"][0]
            data = json.loads(content["text"])
            assert "results" in data
            assert "filters" in data
            assert data["filters"]["sort"] == sort_option

    def test_search_max_results_limit(self, http_client):
        """Test search_transactions respects max_results limit."""
        max_results = 3
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {"max_results": max_results},
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        data = json.loads(content["text"])
        assert "results" in data
        assert len(data["results"]) <= max_results
        if data["summary"]["matched"] > max_results:
            assert data["summary"]["truncated"] is True
