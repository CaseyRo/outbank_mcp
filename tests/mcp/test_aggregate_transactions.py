"""Tests for aggregate_transactions tool across both stdio and HTTP transports."""

import json

EXPECTED_GROUP_FIELDS = {"group", "count", "total", "average", "min", "max"}


def _call_aggregate(client, **kwargs):
    """Helper to call aggregate_transactions and parse the response."""
    response = client.send_request(
        "tools/call",
        params={"name": "aggregate_transactions", "arguments": kwargs},
    )
    assert "result" in response, f"Expected result, got: {response}"
    content = response["result"]["content"][0]
    return json.loads(content["text"])


class TestStdioAggregateTransactions:
    """Aggregate transaction tests for stdio transport."""

    def test_aggregate_by_category_default(self, stdio_client):
        """Test default aggregation groups by category."""
        data = _call_aggregate(stdio_client)

        assert "filters" in data
        assert data["filters"]["group_by"] == "category"
        assert "summary" in data
        assert data["summary"]["transactions_matched"] > 0
        assert data["summary"]["groups_returned"] > 0
        assert "grand_total" in data["summary"]
        assert "groups" in data
        assert len(data["groups"]) == data["summary"]["groups_returned"]

    def test_aggregate_group_fields_complete(self, stdio_client):
        """Test each group has all expected fields with correct types."""
        data = _call_aggregate(stdio_client, group_by="category")

        for group in data["groups"]:
            assert EXPECTED_GROUP_FIELDS == set(group.keys())
            assert isinstance(group["group"], str)
            assert isinstance(group["count"], int)
            assert group["count"] > 0
            assert isinstance(group["total"], (int, float))
            assert isinstance(group["average"], (int, float))
            assert isinstance(group["min"], (int, float))
            assert isinstance(group["max"], (int, float))
            assert group["min"] <= group["max"]

    def test_aggregate_by_month(self, stdio_client):
        """Test aggregation by month returns YYYY-MM formatted keys."""
        data = _call_aggregate(stdio_client, group_by="month")

        assert data["filters"]["group_by"] == "month"
        assert len(data["groups"]) > 0
        for group in data["groups"]:
            # Month keys should be YYYY-MM or "Unknown"
            if group["group"] != "Unknown":
                assert len(group["group"]) == 7
                assert group["group"][4] == "-"

    def test_aggregate_by_counterparty(self, stdio_client):
        """Test aggregation by counterparty."""
        data = _call_aggregate(stdio_client, group_by="counterparty")

        assert data["filters"]["group_by"] == "counterparty"
        assert len(data["groups"]) > 0
        # Counterparty grouping typically produces more groups than category
        assert data["summary"]["groups_returned"] > 0

    def test_aggregate_by_subcategory(self, stdio_client):
        """Test aggregation by subcategory."""
        data = _call_aggregate(stdio_client, group_by="subcategory")

        assert data["filters"]["group_by"] == "subcategory"
        assert len(data["groups"]) > 0

    def test_aggregate_by_account(self, stdio_client):
        """Test aggregation by account."""
        data = _call_aggregate(stdio_client, group_by="account")

        assert data["filters"]["group_by"] == "account"
        assert len(data["groups"]) > 0

    def test_aggregate_with_date_range_filter(self, stdio_client):
        """Test aggregation restricted to a date range."""
        data = _call_aggregate(
            stdio_client,
            group_by="category",
            date_start="2024-01-01",
            date_end="2024-12-31",
        )

        assert data["filters"]["date_start"] == "2024-01-01"
        assert data["filters"]["date_end"] == "2024-12-31"
        assert data["summary"]["transactions_matched"] >= 0

    def test_aggregate_with_amount_range_filter(self, stdio_client):
        """Test aggregation with amount range filter."""
        data = _call_aggregate(
            stdio_client,
            group_by="category",
            amount_min=-1000,
            amount_max=-10,
        )

        assert data["filters"]["amount_min"] == -1000
        assert data["filters"]["amount_max"] == -10
        assert data["summary"]["transactions_matched"] >= 0

    def test_aggregate_empty_result_future_date(self, stdio_client):
        """Test aggregation with filters that match nothing."""
        data = _call_aggregate(
            stdio_client,
            group_by="category",
            date_start="2099-01-01",
            date_end="2099-12-31",
        )

        assert data["summary"]["transactions_matched"] == 0
        assert data["summary"]["groups_returned"] == 0
        assert data["summary"]["grand_total"] == 0.0
        assert data["groups"] == []

    def test_aggregate_grand_total_equals_sum_of_groups(self, stdio_client):
        """Test that grand_total equals the sum of all group totals."""
        data = _call_aggregate(stdio_client, group_by="category")

        group_sum = round(sum(g["total"] for g in data["groups"]), 2)
        assert abs(data["summary"]["grand_total"] - group_sum) < 0.02

    def test_aggregate_invalid_group_by(self, stdio_client):
        """Test that invalid group_by value returns an error."""
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "aggregate_transactions",
                "arguments": {"group_by": "invalid_field"},
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        # Tool errors come back as text content with isError flag
        assert response["result"].get("isError") is True or "must be one of" in content["text"]

    def test_aggregate_invalid_date_format(self, stdio_client):
        """Test that invalid date format returns an error."""
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "aggregate_transactions",
                "arguments": {"date_start": "not-a-date"},
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        assert response["result"].get("isError") is True or "ISO format" in content["text"]

    def test_aggregate_inverted_date_range(self, stdio_client):
        """Test that date_start > date_end returns an error."""
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "aggregate_transactions",
                "arguments": {"date_start": "2025-12-31", "date_end": "2025-01-01"},
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        assert response["result"].get("isError") is True or "less than or equal" in content["text"]

    def test_aggregate_inverted_amount_range(self, stdio_client):
        """Test that amount_min > amount_max returns an error."""
        response = stdio_client.send_request(
            "tools/call",
            params={
                "name": "aggregate_transactions",
                "arguments": {"amount_min": 100, "amount_max": -100},
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        assert response["result"].get("isError") is True or "less than or equal" in content["text"]


class TestHttpAggregateTransactions:
    """Aggregate transaction tests for HTTP transport."""

    def test_aggregate_by_category_default(self, http_client):
        """Test default aggregation groups by category."""
        data = _call_aggregate(http_client)

        assert data["filters"]["group_by"] == "category"
        assert data["summary"]["transactions_matched"] > 0
        assert data["summary"]["groups_returned"] > 0
        assert len(data["groups"]) == data["summary"]["groups_returned"]

    def test_aggregate_group_fields_complete(self, http_client):
        """Test each group has all expected fields with correct types."""
        data = _call_aggregate(http_client, group_by="category")

        for group in data["groups"]:
            assert EXPECTED_GROUP_FIELDS == set(group.keys())
            assert isinstance(group["count"], int)
            assert group["count"] > 0
            assert group["min"] <= group["max"]

    def test_aggregate_by_month(self, http_client):
        """Test aggregation by month returns YYYY-MM formatted keys."""
        data = _call_aggregate(http_client, group_by="month")

        assert data["filters"]["group_by"] == "month"
        for group in data["groups"]:
            if group["group"] != "Unknown":
                assert len(group["group"]) == 7
                assert group["group"][4] == "-"

    def test_aggregate_by_counterparty(self, http_client):
        """Test aggregation by counterparty."""
        data = _call_aggregate(http_client, group_by="counterparty")

        assert data["filters"]["group_by"] == "counterparty"
        assert data["summary"]["groups_returned"] > 0

    def test_aggregate_with_date_range_filter(self, http_client):
        """Test aggregation restricted to a date range."""
        data = _call_aggregate(
            http_client,
            group_by="month",
            date_start="2024-01-01",
            date_end="2024-06-30",
        )

        assert data["filters"]["date_start"] == "2024-01-01"
        assert data["filters"]["date_end"] == "2024-06-30"
        # All month keys should be within the filtered range
        for group in data["groups"]:
            if group["group"] != "Unknown":
                assert "2024-01" <= group["group"] <= "2024-06"

    def test_aggregate_with_amount_range_filter(self, http_client):
        """Test aggregation with amount range filter."""
        data = _call_aggregate(
            http_client,
            group_by="category",
            amount_min=-500,
            amount_max=-50,
        )

        assert data["filters"]["amount_min"] == -500
        assert data["filters"]["amount_max"] == -50

    def test_aggregate_empty_result_future_date(self, http_client):
        """Test aggregation with filters that match nothing."""
        data = _call_aggregate(
            http_client,
            group_by="category",
            date_start="2099-01-01",
            date_end="2099-12-31",
        )

        assert data["summary"]["transactions_matched"] == 0
        assert data["summary"]["groups_returned"] == 0
        assert data["groups"] == []

    def test_aggregate_grand_total_equals_sum_of_groups(self, http_client):
        """Test that grand_total equals the sum of all group totals."""
        data = _call_aggregate(http_client, group_by="category")

        group_sum = round(sum(g["total"] for g in data["groups"]), 2)
        assert abs(data["summary"]["grand_total"] - group_sum) < 0.02

    def test_aggregate_invalid_group_by(self, http_client):
        """Test that invalid group_by value returns an error."""
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "aggregate_transactions",
                "arguments": {"group_by": "invalid_field"},
            },
        )
        assert "result" in response
        content = response["result"]["content"][0]
        assert response["result"].get("isError") is True or "must be one of" in content["text"]
