"""Tests for transaction exclusion filters.

This test suite validates the transaction exclusion filter functionality, which allows
users to exclude transactions based on category or tag values via environment variables.

The tests cover:
- Parsing exclusion lists from environment variables (comma-separated values)
- Case-insensitive matching (e.g., "transfer" matches "Transfer")
- Partial matching (e.g., "transfer" matches "internal-transfer")
- Integration with CSV loading (excluded transactions never enter the store)
- Both category-based and tag-based exclusions

See README.md "Configuration" section for user-facing documentation.
"""

import json

from tests.mcp.conftest import StdioMCPClient


class TestExclusionFilterLogic:
    """Unit tests for exclusion filter logic.

    These tests validate the core exclusion filter functions without requiring
    CSV files or MCP server setup. They test parsing, matching, and decision logic.
    """

    def test_env_exclusion_list_empty(self, monkeypatch):
        """Test parsing empty exclusion list."""
        from app import _env_exclusion_list

        monkeypatch.delenv("EXCLUDED_CATEGORIES", raising=False)
        result = _env_exclusion_list("EXCLUDED_CATEGORIES")
        assert result == []

        monkeypatch.setenv("EXCLUDED_CATEGORIES", "")
        result = _env_exclusion_list("EXCLUDED_CATEGORIES")
        assert result == []

    def test_env_exclusion_list_single_value(self, monkeypatch):
        """Test parsing single exclusion value."""
        from app import _env_exclusion_list

        monkeypatch.setenv("EXCLUDED_CATEGORIES", "Transfer")
        result = _env_exclusion_list("EXCLUDED_CATEGORIES")
        assert result == ["transfer"]

    def test_env_exclusion_list_multiple_values(self, monkeypatch):
        """Test parsing multiple exclusion values."""
        from app import _env_exclusion_list

        monkeypatch.setenv("EXCLUDED_CATEGORIES", "Transfer,Internal,Reconciliation")
        result = _env_exclusion_list("EXCLUDED_CATEGORIES")
        assert result == ["transfer", "internal", "reconciliation"]

    def test_env_exclusion_list_whitespace_handling(self, monkeypatch):
        """Test exclusion list handles whitespace correctly."""
        from app import _env_exclusion_list

        monkeypatch.setenv("EXCLUDED_CATEGORIES", " Transfer , Internal , Reconciliation ")
        result = _env_exclusion_list("EXCLUDED_CATEGORIES")
        assert result == ["transfer", "internal", "reconciliation"]

    def test_matches_exclusion_empty_list(self):
        """Test matching with empty exclusion list."""
        from app import _matches_exclusion

        assert _matches_exclusion("Transfer", []) is False

    def test_matches_exclusion_case_insensitive(self):
        """Test exclusion matching is case-insensitive."""
        from app import _matches_exclusion

        assert _matches_exclusion("Transfer", ["transfer"]) is True
        assert _matches_exclusion("TRANSFER", ["transfer"]) is True
        assert _matches_exclusion("transfer", ["Transfer"]) is True

    def test_matches_exclusion_partial_match(self):
        """Test exclusion matching supports partial matches."""
        from app import _matches_exclusion

        assert _matches_exclusion("internal-transfer", ["transfer"]) is True
        assert _matches_exclusion("transfer-internal", ["transfer"]) is True
        assert _matches_exclusion("some-transfer-thing", ["transfer"]) is True

    def test_matches_exclusion_exact_match(self):
        """Test exclusion matching works with exact matches."""
        from app import _matches_exclusion

        assert _matches_exclusion("transfer", ["transfer"]) is True
        assert _matches_exclusion("Transfer", ["transfer"]) is True

    def test_should_exclude_transaction_by_category(self, monkeypatch):
        """Test transaction exclusion by category."""
        from app import _should_exclude_transaction

        monkeypatch.setenv("EXCLUDED_CATEGORIES", "Transfer")
        transaction = {"category": "Transfer", "tags": []}
        assert _should_exclude_transaction(transaction) is True

        transaction = {"category": "Grocery", "tags": []}
        assert _should_exclude_transaction(transaction) is False

    def test_should_exclude_transaction_by_subcategory(self, monkeypatch):
        """Test transaction exclusion by subcategory."""
        from app import _should_exclude_transaction

        monkeypatch.setenv("EXCLUDED_CATEGORIES", "Transfer")
        # Transaction with Transfer in subcategory should be excluded
        transaction = {"category": "Finances & Insurances", "subcategory": "Transfer", "tags": []}
        assert _should_exclude_transaction(transaction) is True

        # Transaction without Transfer should not be excluded
        transaction = {"category": "Finances & Insurances", "subcategory": "Insurance", "tags": []}
        assert _should_exclude_transaction(transaction) is False

    def test_should_exclude_transaction_by_category_path(self, monkeypatch):
        """Test transaction exclusion by category_path."""
        from app import _should_exclude_transaction

        monkeypatch.setenv("EXCLUDED_CATEGORIES", "Transfer")
        # Transaction with Transfer in category_path should be excluded
        transaction = {
            "category": "Finances & Insurances",
            "subcategory": "Transfer",
            "category_path": "Finances & Insurances / Transfer",
            "tags": [],
        }
        assert _should_exclude_transaction(transaction) is True

        # Transaction without Transfer in path should not be excluded
        transaction = {
            "category": "Living",
            "subcategory": "Shopping",
            "category_path": "Living / Shopping",
            "tags": [],
        }
        assert _should_exclude_transaction(transaction) is False

    def test_should_exclude_transaction_by_tag(self, monkeypatch):
        """Test transaction exclusion by tag."""
        from app import _should_exclude_transaction

        monkeypatch.setenv("EXCLUDED_TAGS", "transfer")
        transaction = {"category": "Other", "tags": ["transfer"]}
        assert _should_exclude_transaction(transaction) is True

        transaction = {"category": "Other", "tags": ["grocery"]}
        assert _should_exclude_transaction(transaction) is False

    def test_should_exclude_transaction_partial_tag_match(self, monkeypatch):
        """Test transaction exclusion with partial tag match."""
        from app import _should_exclude_transaction

        monkeypatch.setenv("EXCLUDED_TAGS", "transfer")
        transaction = {"category": "Other", "tags": ["internal-transfer"]}
        assert _should_exclude_transaction(transaction) is True

    def test_should_exclude_transaction_case_insensitive(self, monkeypatch):
        """Test transaction exclusion is case-insensitive."""
        from app import _should_exclude_transaction

        monkeypatch.setenv("EXCLUDED_CATEGORIES", "transfer")
        transaction = {"category": "Transfer", "tags": []}
        assert _should_exclude_transaction(transaction) is True

        monkeypatch.setenv("EXCLUDED_TAGS", "TRANSFER")
        transaction = {"category": "Other", "tags": ["transfer"]}
        assert _should_exclude_transaction(transaction) is True

    def test_should_exclude_transaction_multiple_exclusions(self, monkeypatch):
        """Test transaction exclusion with multiple exclusion values."""
        from app import _should_exclude_transaction

        monkeypatch.setenv("EXCLUDED_CATEGORIES", "Transfer,Internal")
        transaction = {"category": "Transfer", "tags": []}
        assert _should_exclude_transaction(transaction) is True

        transaction = {"category": "Internal", "tags": []}
        assert _should_exclude_transaction(transaction) is True

        transaction = {"category": "Grocery", "tags": []}
        assert _should_exclude_transaction(transaction) is False

    def test_should_exclude_transaction_no_exclusions(self, monkeypatch):
        """Test transaction exclusion with no exclusions configured."""
        from app import _should_exclude_transaction

        monkeypatch.delenv("EXCLUDED_CATEGORIES", raising=False)
        monkeypatch.delenv("EXCLUDED_TAGS", raising=False)
        transaction = {"category": "Transfer", "tags": ["transfer"]}
        assert _should_exclude_transaction(transaction) is False


class TestStdioExclusionFilters:
    """Integration tests for exclusion filters with stdio transport."""

    def test_exclusion_filters_applied_on_reload(self, app_path, monkeypatch, tmp_path):
        """Test that exclusion filters are applied when transactions are reloaded."""
        # Create a temporary CSV file with test data
        csv_dir = tmp_path / "csv_data"
        csv_dir.mkdir()
        csv_file = csv_dir / "test.csv"

        # Create CSV with headers and test transactions
        csv_content = """#;Account;Date;Value Date;Amount;Currency;Name;Number;Bank;Reason;Category;Subcategory;Category-Path;Tags;Note;Posting Text
1;Checking;01.01.2024;01.01.2024;100.00;EUR;Test Transfer;DE123456789;Test Bank;Transfer reason;Transfer;;Transfer;transfer,internal;Test note;Posting
2;Checking;02.01.2024;02.01.2024;50.00;EUR;Grocery Store;DE987654321;Grocery Bank;Grocery purchase;Grocery;;Grocery;grocery,food;;Posting
"""
        csv_file.write_text(csv_content, encoding="utf-8-sig")

        # Set up environment with exclusion filters
        env = {
            "OUTBANK_CSV_DIR": str(csv_dir),
            "OUTBANK_CSV_GLOB": "*.csv",
            "EXCLUDED_CATEGORIES": "Transfer",
            "MCP_TRANSPORT": "stdio",
        }

        client = StdioMCPClient(app_path, env=env)
        client.start()
        try:
            import time

            time.sleep(0.5)

            # Reload transactions
            response = client.send_request(
                "tools/call",
                params={"name": "reload_transactions", "arguments": {}},
            )
            assert "result" in response

            # Search for all transactions - Transfer should be excluded
            response = client.send_request(
                "tools/call",
                params={
                    "name": "search_transactions",
                    "arguments": {"max_results": 100},
                },
            )
            assert "result" in response
            content = response["result"]["content"][0]
            data = json.loads(content["text"])
            assert "results" in data

            # Verify Transfer transaction is excluded
            results = data["results"]
            categories = [r.get("category", "") for r in results]
            assert "Transfer" not in categories
            # Grocery transaction should still be present
            assert any("Grocery" in r.get("category", "") for r in results)

        finally:
            client.stop()

    def test_exclusion_filters_by_tag(self, app_path, monkeypatch, tmp_path):
        """Test exclusion filters work with tags."""
        # Create a temporary CSV file with test data
        csv_dir = tmp_path / "csv_data"
        csv_dir.mkdir()
        csv_file = csv_dir / "test.csv"

        csv_content = """#;Account;Date;Value Date;Amount;Currency;Name;Number;Bank;Reason;Category;Subcategory;Category-Path;Tags;Note;Posting Text
1;Checking;01.01.2024;01.01.2024;100.00;EUR;Test Transfer;DE123456789;Test Bank;Transfer reason;Other;;Other;transfer,internal;Test note;Posting
2;Checking;02.01.2024;02.01.2024;50.00;EUR;Grocery Store;DE987654321;Grocery Bank;Grocery purchase;Grocery;;Grocery;grocery,food;;Posting
"""
        csv_file.write_text(csv_content, encoding="utf-8-sig")

        env = {
            "OUTBANK_CSV_DIR": str(csv_dir),
            "OUTBANK_CSV_GLOB": "*.csv",
            "EXCLUDED_TAGS": "transfer",
            "MCP_TRANSPORT": "stdio",
        }

        client = StdioMCPClient(app_path, env=env)
        client.start()
        try:
            import time

            time.sleep(0.5)

            # Reload transactions
            client.send_request(
                "tools/call",
                params={"name": "reload_transactions", "arguments": {}},
            )

            # Search for transactions
            response = client.send_request(
                "tools/call",
                params={
                    "name": "search_transactions",
                    "arguments": {"max_results": 100},
                },
            )
            assert "result" in response
            content = response["result"]["content"][0]
            data = json.loads(content["text"])

            # Verify transaction with "transfer" tag is excluded
            results = data["results"]
            for result in results:
                tags = result.get("tags", [])
                assert "transfer" not in [t.lower() for t in tags]

        finally:
            client.stop()

    def test_exclusion_filters_case_insensitive(self, app_path, monkeypatch, tmp_path):
        """Test exclusion filters are case-insensitive."""
        csv_dir = tmp_path / "csv_data"
        csv_dir.mkdir()
        csv_file = csv_dir / "test.csv"

        csv_content = """#;Account;Date;Value Date;Amount;Currency;Name;Number;Bank;Reason;Category;Subcategory;Category-Path;Tags;Note;Posting Text
1;Checking;01.01.2024;01.01.2024;100.00;EUR;Test Transfer;DE123456789;Test Bank;Transfer reason;Transfer;;Transfer;transfer,internal;Test note;Posting
2;Checking;02.01.2024;02.01.2024;50.00;EUR;Grocery Store;DE987654321;Grocery Bank;Grocery purchase;Grocery;;Grocery;grocery,food;;Posting
"""
        csv_file.write_text(csv_content, encoding="utf-8-sig")

        # Use lowercase exclusion value
        env = {
            "OUTBANK_CSV_DIR": str(csv_dir),
            "OUTBANK_CSV_GLOB": "*.csv",
            "EXCLUDED_CATEGORIES": "transfer",  # lowercase
            "MCP_TRANSPORT": "stdio",
        }

        client = StdioMCPClient(app_path, env=env)
        client.start()
        try:
            import time

            time.sleep(0.5)

            client.send_request(
                "tools/call",
                params={"name": "reload_transactions", "arguments": {}},
            )

            response = client.send_request(
                "tools/call",
                params={
                    "name": "search_transactions",
                    "arguments": {"max_results": 100},
                },
            )
            assert "result" in response
            content = response["result"]["content"][0]
            data = json.loads(content["text"])

            # Transfer (capitalized) should be excluded even though exclusion is lowercase
            results = data["results"]
            categories = [r.get("category", "") for r in results]
            assert "Transfer" not in categories

        finally:
            client.stop()

    def test_exclusion_filters_empty_lists(self, app_path, monkeypatch, tmp_path):
        """Test that empty exclusion lists don't exclude anything."""
        csv_dir = tmp_path / "csv_data"
        csv_dir.mkdir()
        csv_file = csv_dir / "test.csv"

        csv_content = """#;Account;Date;Value Date;Amount;Currency;Name;Number;Bank;Reason;Category;Subcategory;Category-Path;Tags;Note;Posting Text
1;Checking;01.01.2024;01.01.2024;100.00;EUR;Test Transfer;DE123456789;Test Bank;Transfer reason;Transfer;;Transfer;transfer,internal;Test note;Posting
2;Checking;02.01.2024;02.01.2024;50.00;EUR;Grocery Store;DE987654321;Grocery Bank;Grocery purchase;Grocery;;Grocery;grocery,food;;Posting
"""
        csv_file.write_text(csv_content, encoding="utf-8-sig")

        # Empty exclusion lists
        env = {
            "OUTBANK_CSV_DIR": str(csv_dir),
            "OUTBANK_CSV_GLOB": "*.csv",
            "EXCLUDED_CATEGORIES": "",
            "EXCLUDED_TAGS": "",
            "MCP_TRANSPORT": "stdio",
        }

        client = StdioMCPClient(app_path, env=env)
        client.start()
        try:
            import time

            time.sleep(0.5)

            client.send_request(
                "tools/call",
                params={"name": "reload_transactions", "arguments": {}},
            )

            response = client.send_request(
                "tools/call",
                params={
                    "name": "search_transactions",
                    "arguments": {"max_results": 100},
                },
            )
            assert "result" in response
            content = response["result"]["content"][0]
            data = json.loads(content["text"])

            # All transactions should be present
            results = data["results"]
            assert len(results) >= 2  # Both transactions should be present

        finally:
            client.stop()
