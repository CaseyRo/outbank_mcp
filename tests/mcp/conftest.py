"""Pytest configuration and fixtures for MCP transport tests."""

import json
import os
import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import requests

# Token used by the managed HTTP server; must match server env.
_TEST_HTTP_AUTH_TOKEN = "test-token-12345678"


def _pick_free_port() -> int:
    """Bind to port 0 and return the assigned port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class StdioMCPClient:
    """Client for testing MCP server via stdio transport."""

    def __init__(self, app_path: str, env: dict[str, str] | None = None):
        """Initialize stdio client.

        Args:
            app_path: Path to app.py
            env: Optional environment variables to set
        """
        self.app_path = app_path
        self.env = env or {}
        self.process: subprocess.Popen | None = None
        self.request_id = 0

    def start(self) -> None:
        """Start the MCP server process and perform initialization handshake."""
        env = os.environ.copy()
        env.update(self.env)
        env["MCP_TRANSPORT"] = "stdio"
        self.process = subprocess.Popen(
            ["uv", "run", "python", self.app_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        # Perform MCP initialization handshake
        # 1. Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "clientInfo": {
                    "name": "pytest-mcp-client",
                    "version": "1.0.0",
                },
            },
        }
        request_json = json.dumps(init_request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        # 2. Read initialize response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No initialize response from server")
        init_response = json.loads(response_line.strip())
        if "error" in init_response:
            raise RuntimeError(f"Initialize failed: {init_response['error']}")

        # 3. Send notifications/initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        notification_json = json.dumps(initialized_notification) + "\n"
        self.process.stdin.write(notification_json)
        self.process.stdin.flush()

        # Reset request_id for actual test requests
        self.request_id = 0

    def stop(self) -> None:
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None

    def send_request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a JSON-RPC request and return the response.

        Args:
            method: JSON-RPC method name
            params: Optional parameters (defaults to empty dict if None)

        Returns:
            JSON-RPC response as dict
        """
        if not self.process:
            raise RuntimeError("Process not started")

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params if params is not None else {},
        }

        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        # Read response line by line until we get a complete JSON-RPC response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")

        response = json.loads(response_line.strip())
        return response


class HttpMCPClient:
    """Client for testing MCP server via HTTP transport (JSON-only responses).

    Note: FastMCP HTTP transport uses SSE format internally, but this client
    parses it transparently to provide pure JSON responses. Sessions are handled
    automatically for HTTP transport compatibility.
    """

    def __init__(self, url: str = "http://127.0.0.1:6668/mcp", auth_token: str | None = None):
        """Initialize HTTP client.

        Args:
            url: MCP server URL
            auth_token: Optional bearer token for authentication
        """
        self.url = url
        self.auth_token = auth_token
        self.request_id = 0
        self.session_id: str | None = None
        self._initialized = False

    def _initialize(self) -> None:
        """Initialize MCP session (required for HTTP transport, even without SSE)."""
        if self._initialized:
            return

        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "clientInfo": {
                    "name": "pytest-mcp-client",
                    "version": "1.0.0",
                },
            },
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        try:
            response = requests.post(
                self.url, json=init_request, headers=headers, timeout=10, allow_redirects=True
            )
            response.raise_for_status()

            # Extract session ID from response headers
            self.session_id = response.headers.get("Mcp-Session-Id") or response.headers.get(
                "mcp-session-id"
            )

            # Send initialized notification
            if self.session_id:
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                }
                headers_with_session = headers.copy()
                headers_with_session["Mcp-Session-Id"] = self.session_id
                # Notifications don't return responses, ignore errors
                try:
                    requests.post(
                        self.url,
                        json=initialized_notification,
                        headers=headers_with_session,
                        timeout=10,
                        allow_redirects=True,
                    )
                except Exception:
                    pass

            self._initialized = True
        except requests.exceptions.ConnectionError:
            pytest.skip(
                f"HTTP server not running at {self.url}. Start server with: MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=6668 uv run python app.py"
            )

    def send_request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a JSON-RPC request and return the response (HTTP JSON-only, no SSE streaming).

        Args:
            method: JSON-RPC method name
            params: Optional parameters (defaults to empty dict if None)

        Returns:
            JSON-RPC response as dict

        Raises:
            requests.exceptions.ConnectionError: If server is not running
            requests.exceptions.HTTPError: If server returns an error status
        """
        # Initialize session if not already done
        if not self._initialized:
            self._initialize()

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params if params is not None else {},
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        try:
            response = requests.post(
                self.url, json=request, headers=headers, timeout=10, allow_redirects=True
            )

            # Handle empty responses (202 Accepted for notifications, or empty 200)
            if not response.text.strip() or response.status_code == 202:
                return {"jsonrpc": "2.0", "id": self.request_id}

            # FastMCP may return responses in SSE format (text/event-stream)
            # Parse SSE format transparently to return pure JSON
            content_type = response.headers.get("Content-Type", "")
            if "text/event-stream" in content_type or response.text.strip().startswith("event:"):
                # Parse SSE format: extract JSON from "data: {json}" lines
                lines = response.text.strip().split("\n")
                for line in lines:
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            if "jsonrpc" in data:
                                return data
                        except (json.JSONDecodeError, ValueError):
                            continue
                # If we couldn't parse SSE, fall through to JSON parsing

            # Try to parse as plain JSON-RPC response
            try:
                data = response.json()
                # If it's a valid JSON-RPC response (success or error), return it
                if "jsonrpc" in data and ("result" in data or "error" in data):
                    return data
            except (ValueError, json.JSONDecodeError):
                pass

            # If response is empty or not JSON, check status code
            if not response.text.strip():
                # Empty response might be an error - check status code
                if response.status_code >= 400:
                    response.raise_for_status()
                # Otherwise return empty response structure
                return {"jsonrpc": "2.0", "id": self.request_id}

            response.raise_for_status()

            # Last resort: try to parse as JSON
            return response.json()
        except requests.exceptions.ConnectionError:
            pytest.skip(
                f"HTTP server not running at {self.url}. Start server with: MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=6668 uv run python app.py"
            )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Run stdio tests first, then HTTP tests (so HTTP server starts only when needed)."""

    def order_key(item: pytest.Item) -> tuple[int, str]:
        fixturenames = getattr(item, "fixturenames", ())
        uses_http = any(
            f in fixturenames
            for f in ("http_client", "http_client_with_auth", "http_client_no_auth")
        )
        return (1 if uses_http else 0, item.nodeid)

    items.sort(key=order_key)


@pytest.fixture
def app_path() -> str:
    """Return path to app.py."""
    return str(Path(__file__).parent.parent.parent / "app.py")


@pytest.fixture(scope="session")
def mcp_http_server() -> Iterator[str]:
    """Start MCP server in HTTP mode on a free port; yield MCP URL. Stopped after session."""
    app_path = str(Path(__file__).parent.parent.parent / "app.py")
    port = _pick_free_port()
    url = f"http://127.0.0.1:{port}/mcp"
    env = os.environ.copy()
    env.update(
        {
            "MCP_TRANSPORT": "http",
            "MCP_HOST": "127.0.0.1",
            "MCP_PORT": str(port),
            "MCP_HTTP_AUTH_TOKEN": _TEST_HTTP_AUTH_TOKEN,
        }
    )
    proc = subprocess.Popen(
        ["uv", "run", "python", app_path],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    try:
        # Wait until server responds (root may 404; any response means server is up)
        for _ in range(30):
            try:
                requests.get(f"http://127.0.0.1:{port}/", timeout=1)
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                time.sleep(0.2)
        else:
            proc.terminate()
            proc.wait(timeout=5)
            raise RuntimeError("HTTP server did not become ready in time")
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


@pytest.fixture
def stdio_client(app_path: str) -> Iterator[StdioMCPClient]:
    """Fixture providing stdio MCP client."""
    client = StdioMCPClient(app_path)
    client.start()
    try:
        # Give server a moment to start
        time.sleep(0.5)
        yield client
    finally:
        client.stop()


@pytest.fixture
def http_client(mcp_http_server: str) -> HttpMCPClient:
    """HTTP MCP client using the session-started server (auth token matches server)."""
    return HttpMCPClient(url=mcp_http_server, auth_token=_TEST_HTTP_AUTH_TOKEN)


@pytest.fixture
def http_client_with_auth(mcp_http_server: str) -> HttpMCPClient:
    """HTTP MCP client with auth token (same as http_client; auth is mandatory for HTTP)."""
    return HttpMCPClient(url=mcp_http_server, auth_token=_TEST_HTTP_AUTH_TOKEN)


@pytest.fixture
def http_client_no_auth(mcp_http_server: str) -> HttpMCPClient:
    """HTTP MCP client without auth token (for testing auth failures)."""
    return HttpMCPClient(url=mcp_http_server, auth_token=None)


@pytest.fixture
def workflow_context() -> dict[str, Any]:
    """Fixture for sharing data between BDD workflow steps."""
    return {}
