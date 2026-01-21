"""Step definitions for monthly expense analysis workflow."""

import json
import sys
from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

# Ensure we can import from tests.mcp.conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

# Link feature file
scenarios("../features/monthly_expense.feature")


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
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            reload_data = json.loads(result_data)
            workflow_context["total_records"] = reload_data.get("total_records", 0)
        except json.JSONDecodeError:
            pass


@when(parsers.parse('I search for transactions from "{start}" to "{end}"'))
def search_date_range(stdio_client, workflow_context, start, end):
    """Search transactions in date range."""
    response = stdio_client.send_request(
        "tools/call",
        {
            "name": "search_transactions",
            "arguments": {"date_start": start, "date_end": end, "max_results": 100},
        },
    )
    workflow_context["search_response"] = response
    if "result" in response:
        result_data = response["result"].get("content", [{}])[0].get("text", "{}")
        try:
            search_data = json.loads(result_data)
            workflow_context["search_data"] = search_data
            workflow_context["results"] = search_data.get("results", [])
            workflow_context["matched"] = search_data.get("summary", {}).get("matched", 0)
        except json.JSONDecodeError:
            pass


@when("I calculate expense totals")
def calculate_expense_totals(workflow_context):
    """Calculate totals from search results."""
    results = workflow_context.get("results", [])
    total_expenses = sum(abs(r.get("amount", 0)) for r in results if r.get("amount", 0) < 0)
    workflow_context["total_expenses"] = total_expenses

    # Count categories
    categories = {}
    for result in results:
        cat = result.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
    workflow_context["categories"] = categories
    workflow_context["top_categories"] = sorted(
        categories.items(), key=lambda x: x[1], reverse=True
    )[:5]


@then("I should see expense summary with transaction count")
def verify_expense_summary(workflow_context):
    """Verify expense summary."""
    assert "search_data" in workflow_context
    search_data = workflow_context["search_data"]
    assert "summary" in search_data
    assert "results" in search_data
    assert isinstance(search_data["results"], list)


@then("I should see total expenses amount")
def verify_total_expenses(workflow_context):
    """Verify total expenses calculated."""
    assert "total_expenses" in workflow_context
    assert workflow_context["total_expenses"] >= 0


@then("I should see top expense categories")
def verify_top_categories(workflow_context):
    """Verify top categories are identified."""
    assert "top_categories" in workflow_context
    assert isinstance(workflow_context["top_categories"], list)
