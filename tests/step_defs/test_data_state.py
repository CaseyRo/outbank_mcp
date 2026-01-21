"""Step definitions for data state management workflow."""

import json
import sys
from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

# Ensure we can import from tests.mcp.conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

# Link feature file
scenarios("../features/data_state.feature")


@given("the MCP server is running")
def server_running(stdio_client):
    """Verify server is running."""
    assert stdio_client.process.poll() is None


@given("no data is loaded")
def no_data_loaded(workflow_context):
    """Mark that no data is loaded."""
    workflow_context["data_loaded"] = False


@given("CSV data is loaded")
def csv_loaded(stdio_client, workflow_context):
    """Ensure CSV data is loaded."""
    response = stdio_client.send_request(
        "tools/call", {"name": "reload_transactions", "arguments": {}}
    )
    workflow_context["reload_response"] = response
    workflow_context["data_loaded"] = True
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            reload_data = json.loads(result_data)
            workflow_context["total_records"] = reload_data.get("total_records", 0)
        except json.JSONDecodeError:
            pass


@when("I search for transactions")
def search_transactions(stdio_client, workflow_context):
    """Search for transactions (should auto-load if needed)."""
    response = stdio_client.send_request(
        "tools/call", {"name": "search_transactions", "arguments": {"max_results": 10}}
    )
    workflow_context["search_response"] = response
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            search_data = json.loads(result_data)
            workflow_context["search_data"] = search_data
            workflow_context["results"] = search_data.get("results", [])
        except json.JSONDecodeError:
            pass


@then("data should be automatically loaded")
def verify_auto_load(workflow_context):
    """Verify data was automatically loaded."""
    # Data should be loaded (server handles this automatically)
    assert "search_response" in workflow_context
    assert (
        "result" in workflow_context["search_response"]
        or "error" not in workflow_context["search_response"]
    )


@then("I should receive search results")
def verify_search_results(workflow_context):
    """Verify search results received."""
    assert "search_response" in workflow_context
    assert "result" in workflow_context["search_response"]


@when("I reload transactions")
def reload_transactions(stdio_client, workflow_context):
    """Reload transactions."""
    response = stdio_client.send_request(
        "tools/call", {"name": "reload_transactions", "arguments": {}}
    )
    workflow_context["reload_response"] = response
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            reload_data = json.loads(result_data)
            workflow_context["total_records"] = reload_data.get("total_records", 0)
            workflow_context["new_records"] = reload_data.get("new_records", 0)
            workflow_context["removed_records"] = reload_data.get("removed_records", 0)
        except json.JSONDecodeError:
            pass


@then("I should see total records")
def verify_total_records(workflow_context):
    """Verify total records visible."""
    assert "total_records" in workflow_context
    assert workflow_context["total_records"] >= 0


@when("I reload transactions again")
def reload_transactions_again(stdio_client, workflow_context):
    """Reload transactions again."""
    first_count = workflow_context.get("total_records", 0)
    response = stdio_client.send_request(
        "tools/call", {"name": "reload_transactions", "arguments": {}}
    )
    workflow_context["second_reload_response"] = response
    workflow_context["first_count"] = first_count
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            reload_data = json.loads(result_data)
            workflow_context["second_total_records"] = reload_data.get("total_records", 0)
            workflow_context["second_new_records"] = reload_data.get("new_records", 0)
            workflow_context["second_removed_records"] = reload_data.get("removed_records", 0)
        except json.JSONDecodeError:
            pass


@then("I should see same total records")
def verify_same_total_records(workflow_context):
    """Verify same total records."""
    assert "first_count" in workflow_context
    assert "second_total_records" in workflow_context
    assert workflow_context["first_count"] == workflow_context["second_total_records"]


@then("new records count should be 0")
def verify_no_new_records(workflow_context):
    """Verify no new records."""
    assert "second_new_records" in workflow_context
    assert workflow_context["second_new_records"] == 0


@then("removed records count should be 0")
def verify_no_removed_records(workflow_context):
    """Verify no removed records."""
    assert "second_removed_records" in workflow_context
    assert workflow_context["second_removed_records"] == 0


@when(parsers.parse('I search with query "{query}"'))
def search_with_query(stdio_client, workflow_context, query):
    """Search with query."""
    response = stdio_client.send_request(
        "tools/call",
        {"name": "search_transactions", "arguments": {"query": query, "max_results": 100}},
    )
    workflow_context["search_response"] = response
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            search_data = json.loads(result_data)
            workflow_context["search_data"] = search_data
            workflow_context["results"] = search_data.get("results", [])
            if "first_results" not in workflow_context:
                workflow_context["first_results"] = workflow_context["results"]
                workflow_context["first_count"] = len(workflow_context["results"])
            else:
                workflow_context["second_results"] = workflow_context["results"]
                workflow_context["second_count"] = len(workflow_context["results"])
        except json.JSONDecodeError:
            pass


@when(parsers.parse('I search with query "{query}" again'))
def search_with_query_again(stdio_client, workflow_context, query):
    """Search with query again (for consistency testing)."""
    response = stdio_client.send_request(
        "tools/call",
        {"name": "search_transactions", "arguments": {"query": query, "max_results": 100}},
    )
    workflow_context["search_response"] = response
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            search_data = json.loads(result_data)
            workflow_context["search_data"] = search_data
            workflow_context["results"] = search_data.get("results", [])
            workflow_context["second_results"] = workflow_context["results"]
            workflow_context["second_count"] = len(workflow_context["results"])
        except json.JSONDecodeError:
            pass


@then("I should see results count")
def verify_results_count(workflow_context):
    """Verify results count."""
    assert "results" in workflow_context
    assert isinstance(workflow_context["results"], list)


@then("I should see same results count")
def verify_same_results_count(workflow_context):
    """Verify same results count."""
    assert "first_count" in workflow_context
    assert "second_count" in workflow_context
    assert workflow_context["first_count"] == workflow_context["second_count"]


@then("results should be identical")
def verify_results_identical(workflow_context):
    """Verify results are identical."""
    assert "first_results" in workflow_context
    assert "second_results" in workflow_context
    # Compare result IDs or first few results
    first_ids = [r.get("id") for r in workflow_context["first_results"][:10]]
    second_ids = [r.get("id") for r in workflow_context["second_results"][:10]]
    assert first_ids == second_ids
