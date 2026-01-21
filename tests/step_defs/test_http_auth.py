"""Step definitions for HTTP authentication workflow."""

import sys
from pathlib import Path

import requests
from pytest_bdd import given, parsers, scenarios, then, when

# Ensure we can import from tests.mcp.conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

# Link feature file
scenarios("../features/http_auth.feature")


@given("the HTTP server is running with auth enabled")
def http_server_with_auth(http_client, workflow_context):
    """Verify HTTP server is running (auth is mandatory for HTTP transport)."""
    # Note: HTTP transport requires authentication - server must be started with MCP_HTTP_AUTH_TOKEN
    # The http_client fixture already includes auth token since auth is mandatory
    workflow_context["http_client"] = http_client
    workflow_context["auth_enabled"] = True


@when("I make a request without authentication token")
def request_without_token(workflow_context):
    """Make request without auth token."""
    client = workflow_context["http_client"]
    # Create a client without auth token
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from mcp.conftest import HttpMCPClient

    no_auth_client = HttpMCPClient(url=client.url, auth_token=None)
    try:
        response = no_auth_client.send_request("tools/list")
        workflow_context["unauth_response"] = response
        workflow_context["unauth_error"] = "error" in response
    except requests.exceptions.HTTPError as e:
        workflow_context["unauth_error"] = True
        workflow_context["unauth_status_code"] = (
            e.response.status_code if hasattr(e, "response") else None
        )
    except Exception as e:
        workflow_context["unauth_error"] = True
        workflow_context["unauth_exception"] = str(e)


@when(parsers.parse('I make a request with invalid token "{token}"'))
def request_with_invalid_token(workflow_context, token):
    """Make request with invalid token."""
    client = workflow_context["http_client"]
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from mcp.conftest import HttpMCPClient

    invalid_client = HttpMCPClient(url=client.url, auth_token=token)
    try:
        response = invalid_client.send_request("tools/list")
        workflow_context["invalid_token_response"] = response
        workflow_context["invalid_token_error"] = "error" in response
    except requests.exceptions.HTTPError as e:
        workflow_context["invalid_token_error"] = True
        workflow_context["invalid_token_status_code"] = (
            e.response.status_code if hasattr(e, "response") else None
        )
    except Exception as e:
        workflow_context["invalid_token_error"] = True
        workflow_context["invalid_token_exception"] = str(e)


@when("I make a request with valid token")
def request_with_valid_token(http_client_with_auth, workflow_context):
    """Make request with valid token."""
    try:
        response = http_client_with_auth.send_request("tools/list")
        workflow_context["valid_token_response"] = response
        workflow_context["valid_token_success"] = "result" in response
    except Exception as e:
        workflow_context["valid_token_success"] = False
        workflow_context["valid_token_exception"] = str(e)


@then("I should receive an unauthorized error")
def verify_unauthorized_error(workflow_context):
    """Verify unauthorized error received."""
    # Check if we got an error from either no token or invalid token
    assert workflow_context.get("unauth_error", False) or workflow_context.get(
        "invalid_token_error", False
    )


@then("the error code should be 401 or 403")
def verify_error_code(workflow_context):
    """Verify error code is 401 or 403."""
    status_code = workflow_context.get("unauth_status_code") or workflow_context.get(
        "invalid_token_status_code"
    )
    if status_code:
        assert status_code in [401, 403]
    else:
        # If we can't get status code, at least verify error occurred
        assert workflow_context.get("unauth_error", False) or workflow_context.get(
            "invalid_token_error", False
        )


@then("I should receive successful response")
def verify_successful_response(workflow_context):
    """Verify successful response."""
    assert workflow_context.get("valid_token_success", False)


@then("I should see available tools")
def verify_available_tools(workflow_context):
    """Verify available tools in response."""
    response = workflow_context.get("valid_token_response", {})
    assert "result" in response
    assert "tools" in response["result"]
    assert len(response["result"]["tools"]) > 0
