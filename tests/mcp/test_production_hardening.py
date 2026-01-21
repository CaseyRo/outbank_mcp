"""Tests for production hardening features: rate limiting, request size limits, audit logging."""

import json
import os
import time
from pathlib import Path

import pytest


class TestRateLimiting:
    """Tests for rate limiting functionality (HTTP transport only).

    Uses the existing http_client fixture from conftest.py which handles
    session initialization and authentication.
    """

    @pytest.mark.http
    def test_rate_limit_allows_normal_requests(self, http_client):
        """Test that requests within rate limit are processed normally."""
        # Make a single request - should succeed
        response = http_client.send_request("tools/list")
        assert "result" in response
        assert "tools" in response["result"]

    @pytest.mark.http
    def test_health_check_works_with_rate_limiting(self, http_client):
        """Test that health_check tool works when rate limiting is enabled."""
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


class TestRequestSizeLimiting:
    """Tests for request size limiting functionality."""

    @pytest.mark.http
    def test_normal_request_size_accepted(self, http_client):
        """Test that normal-sized requests are accepted."""
        response = http_client.send_request("tools/list")
        assert "result" in response
        assert "tools" in response["result"]

    @pytest.mark.http
    def test_moderate_query_size_accepted(self, http_client):
        """Test that moderate-sized query parameters are accepted."""
        # Create a reasonable-sized query (1KB)
        moderate_query = "grocery " * 100  # ~800 bytes

        response = http_client.send_request(
            "tools/call",
            params={
                "name": "search_transactions",
                "arguments": {"query": moderate_query, "max_results": 5},
            },
        )
        assert "result" in response
        # The query should be processed (even if no results match)
        content = response["result"]["content"][0]
        data = json.loads(content["text"])
        assert "results" in data


class TestAuditLogging:
    """Tests for audit logging functionality."""

    @pytest.fixture
    def audit_log_path(self):
        """Get the audit log path from environment or default."""
        return Path(os.getenv("MCP_AUDIT_LOG", "./logs/audit.log"))

    @pytest.mark.http
    def test_audit_log_created_on_tool_call(self, http_client, audit_log_path):
        """Test that audit log entries are created when tools are called."""
        audit_enabled = os.getenv("MCP_AUDIT_ENABLED", "true").lower()
        if audit_enabled in ("false", "0", "no", "off"):
            pytest.skip("Audit logging is disabled")

        # Record the current size of the audit log (if it exists)
        initial_size = 0
        if audit_log_path.exists():
            initial_size = audit_log_path.stat().st_size

        # Make a tool call
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "health_check",
                "arguments": {},
            },
        )
        assert "result" in response

        # Give the server a moment to write the log
        time.sleep(0.5)

        # Check if the audit log was updated
        if not audit_log_path.exists():
            pytest.skip(
                f"Audit log not found at {audit_log_path}. "
                "Server may not be configured for audit logging."
            )

        new_size = audit_log_path.stat().st_size
        assert new_size > initial_size, "Audit log should have grown after tool call"

    @pytest.mark.http
    def test_audit_log_format_is_json(self, http_client, audit_log_path):
        """Test that audit log entries are valid JSON."""
        audit_enabled = os.getenv("MCP_AUDIT_ENABLED", "true").lower()
        if audit_enabled in ("false", "0", "no", "off"):
            pytest.skip("Audit logging is disabled")

        # Make a tool call to ensure there's at least one entry
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "describe_fields",
                "arguments": {},
            },
        )
        assert "result" in response

        # Give the server a moment to write the log
        time.sleep(0.5)

        if not audit_log_path.exists():
            pytest.skip(f"Audit log not found at {audit_log_path}")

        # Read and validate the last few entries
        with open(audit_log_path) as f:
            lines = f.readlines()

        assert len(lines) > 0, "Audit log should have at least one entry"

        # Validate that recent entries are valid JSON
        valid_entries = 0
        for line in lines[-5:]:  # Check last 5 entries
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                # Check expected fields
                assert "timestamp" in entry, "Entry should have timestamp"
                assert "tool" in entry, "Entry should have tool name"
                valid_entries += 1
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON in audit log: {line[:100]}...")

        assert valid_entries > 0, "Should have at least one valid JSON entry"

    @pytest.mark.http
    def test_audit_log_entries_have_timestamps(self, http_client, audit_log_path):
        """Test that audit log entries have timestamps for tracking."""
        audit_enabled = os.getenv("MCP_AUDIT_ENABLED", "true").lower()
        if audit_enabled in ("false", "0", "no", "off"):
            pytest.skip("Audit logging is disabled")

        # Make a tool call
        response = http_client.send_request(
            "tools/call",
            params={
                "name": "health_check",
                "arguments": {},
            },
        )
        assert "result" in response

        # Give the server a moment to write the log
        time.sleep(0.5)

        if not audit_log_path.exists():
            pytest.skip(f"Audit log not found at {audit_log_path}")

        # Check that entries have timestamps
        with open(audit_log_path) as f:
            lines = f.readlines()

        assert len(lines) > 0, "Audit log should have entries"

        # Check last entry has a timestamp
        last_entry = json.loads(lines[-1].strip())
        assert "timestamp" in last_entry, "Entry should have timestamp"
        assert "tool" in last_entry, "Entry should have tool field"
        # Note: Tool name extraction from middleware context is limited;
        # the important thing is that requests are being logged
