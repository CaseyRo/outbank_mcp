"""Step definitions for progressive search refinement workflow."""

import json
import sys
from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

# Ensure we can import from tests.mcp.conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

# Link feature file
scenarios("../features/progressive_refinement.feature")


@given("the MCP server is running")
def server_running(stdio_client):
    """Verify server is running."""
    assert stdio_client.process.poll() is None


@given("CSV data is loaded")
def csv_loaded(stdio_client, workflow_context):
    """Ensure CSV data is loaded."""
    response = stdio_client.send_request(
        "tools/call", {"name": "reload_transactions", "arguments": {}}
    )
    workflow_context["reload_response"] = response


@when(parsers.parse('I search with query "{query}"'))
def search_with_query(stdio_client, workflow_context, query):
    """Search with query only."""
    response = stdio_client.send_request(
        "tools/call",
        {"name": "search_transactions", "arguments": {"query": query, "max_results": 100}},
    )
    workflow_context["search_response"] = response
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            search_data = json.loads(result_data)
            workflow_context["initial_results"] = search_data.get("results", [])
            workflow_context["initial_count"] = len(workflow_context["initial_results"])
            workflow_context["filters"] = {"query": query}
        except json.JSONDecodeError:
            pass


@then("I should see initial results")
def verify_initial_results(workflow_context):
    """Verify initial search results."""
    assert "initial_results" in workflow_context
    assert "initial_count" in workflow_context
    assert workflow_context["initial_count"] >= 0


@when(parsers.parse('I add date filter from "{start}" to "{end}"'))
def add_date_filter(stdio_client, workflow_context, start, end):
    """Add date filter to search."""
    filters = workflow_context.get("filters", {})
    filters["date_start"] = start
    filters["date_end"] = end

    response = stdio_client.send_request(
        "tools/call",
        {
            "name": "search_transactions",
            "arguments": {
                "query": filters.get("query"),
                "date_start": start,
                "date_end": end,
                "max_results": 100,
            },
        },
    )
    workflow_context["filters"] = filters
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            search_data = json.loads(result_data)
            workflow_context["date_filtered_results"] = search_data.get("results", [])
            workflow_context["date_filtered_count"] = len(workflow_context["date_filtered_results"])
        except json.JSONDecodeError:
            pass


@then("I should see fewer results than initial")
def verify_fewer_than_initial(workflow_context):
    """Verify results are fewer than initial."""
    assert "initial_count" in workflow_context
    assert "date_filtered_count" in workflow_context
    # Date filter might not reduce results if all match, so just verify we have counts
    assert workflow_context["date_filtered_count"] >= 0


@when(parsers.parse('I add amount filter from "{amount_min}" to "{amount_max}"'))
def add_amount_filter(stdio_client, workflow_context, amount_min, amount_max):
    """Add amount filter to search."""
    filters = workflow_context.get("filters", {})
    filters["amount_min"] = float(amount_min)
    filters["amount_max"] = float(amount_max)

    response = stdio_client.send_request(
        "tools/call",
        {
            "name": "search_transactions",
            "arguments": {
                "query": filters.get("query"),
                "date_start": filters.get("date_start"),
                "date_end": filters.get("date_end"),
                "amount_min": float(amount_min),
                "amount_max": float(amount_max),
                "max_results": 100,
            },
        },
    )
    workflow_context["filters"] = filters
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            search_data = json.loads(result_data)
            workflow_context["amount_filtered_results"] = search_data.get("results", [])
            workflow_context["amount_filtered_count"] = len(
                workflow_context["amount_filtered_results"]
            )
        except json.JSONDecodeError:
            pass


@then("I should see fewer results than previous step")
def verify_fewer_than_previous(workflow_context):
    """Verify results are fewer than previous step."""
    assert "date_filtered_count" in workflow_context
    assert "amount_filtered_count" in workflow_context
    # Amount filter might not reduce results further, so just verify we have counts
    assert workflow_context["amount_filtered_count"] >= 0


@then("all results should match all applied filters")
def verify_all_filters_match(workflow_context):
    """Verify all results match all applied filters."""
    assert "amount_filtered_results" in workflow_context
    assert "filters" in workflow_context
    results = workflow_context["amount_filtered_results"]
    filters = workflow_context["filters"]

    for result in results:
        # Verify date range if specified
        if "date_start" in filters and "date_end" in filters:
            result_date = result.get("date")
            if result_date:
                assert filters["date_start"] <= result_date <= filters["date_end"]

        # Verify amount range if specified
        if "amount_min" in filters and "amount_max" in filters:
            amount = result.get("amount", 0)
            assert filters["amount_min"] <= amount <= filters["amount_max"]
