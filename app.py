import csv
import json
import logging
import os
import sys
import time
from datetime import date, datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from exclusion_filters import (
    env_exclusion_list,
    env_exclusion_list_display,
    matches_exclusion,
    should_exclude_transaction,
)

# Re-export for backwards compatibility
_env_exclusion_list = env_exclusion_list
_env_exclusion_list_display = env_exclusion_list_display
_matches_exclusion = matches_exclusion
_should_exclude_transaction = should_exclude_transaction

# Load environment variables from .env file if it exists
load_dotenv()

# Track server startup time for uptime calculation
_SERVER_START_TIME = time.time()


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_rate_limit() -> float | None:
    """Get rate limit configuration from environment.

    Format: "<count>/<period>" e.g., "100/minute", "1000/hour", or just a number for requests/second.
    Returns requests per second as a float, or None if not configured.
    """
    value = os.getenv("MCP_RATE_LIMIT")
    if not value or not value.strip():
        return None

    value = value.strip()

    # Try parsing as a simple number (requests per second)
    try:
        return float(value)
    except ValueError:
        pass

    # Try parsing as "count/period" format
    try:
        count_str, period = value.split("/")
        count = float(count_str)
        period = period.lower().strip()

        # Convert to requests per second
        if period in ("second", "sec", "s"):
            return count
        elif period in ("minute", "min", "m"):
            return count / 60.0
        elif period in ("hour", "hr", "h"):
            return count / 3600.0
        else:
            # Unknown period, assume per minute
            return count / 60.0
    except (ValueError, AttributeError):
        return None


def _env_request_timeout() -> int | None:
    """Get request timeout in seconds from environment.

    Returns None if not configured (no timeout).
    Default: 60 seconds when MCP_REQUEST_TIMEOUT is set without value.
    """
    value = os.getenv("MCP_REQUEST_TIMEOUT")
    if value is None:
        return None
    value = value.strip()
    if not value:
        return 60  # Default if env var exists but empty
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError("MCP_REQUEST_TIMEOUT must be an integer (seconds)") from exc


def _env_max_request_size() -> int:
    """Get maximum request size in bytes from environment.

    Default: 1MB (1048576 bytes)
    """
    return _env_int("MCP_MAX_REQUEST_SIZE", 1048576)


def _env_audit_enabled() -> bool:
    """Check if audit logging is enabled.

    Default: True for HTTP transport, False for stdio.
    Can be overridden with MCP_AUDIT_ENABLED env var.
    """
    explicit = os.getenv("MCP_AUDIT_ENABLED")
    if explicit is not None:
        return explicit.strip().lower() in {"1", "true", "yes", "on"}
    # Default: enabled for HTTP, disabled for stdio
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    return transport == "http"


def _env_audit_log_path() -> Path:
    """Get audit log file path from environment.

    Default: ./logs/audit.log
    """
    value = os.getenv("MCP_AUDIT_LOG", "./logs/audit.log")
    return Path(value).expanduser()


# Audit logger setup
_audit_logger: logging.Logger | None = None


def _setup_audit_logger() -> logging.Logger | None:
    """Set up the audit logger with JSON formatting to file."""
    global _audit_logger

    if not _env_audit_enabled():
        return None

    if _audit_logger is not None:
        return _audit_logger

    log_path = _env_audit_log_path()

    # Ensure log directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("mcp_audit")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Don't propagate to root logger

    # Remove existing handlers
    logger.handlers.clear()

    # Create file handler
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(logging.INFO)

    # Simple formatter - we'll format as JSON in the log call
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    _audit_logger = logger
    return logger


def _audit_log(tool_name: str, parameters: dict[str, Any], client_ip: str | None = None) -> None:
    """Log a tool invocation to the audit log."""
    logger = _setup_audit_logger()
    if logger is None:
        return

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": tool_name,
        "parameters": parameters,
    }
    if client_ip:
        entry["client_ip"] = client_ip

    logger.info(json.dumps(entry, default=str))


def _require_http_auth() -> None:
    """Require HTTP authentication for all HTTP transport requests.

    This function is called from MCP tools when HTTP transport is used.
    Authentication is mandatory for HTTP transport - stdio transport
    does not call this function.
    """
    try:
        headers = get_http_headers()
    except Exception:
        # If we can't get headers (e.g., not HTTP transport), skip auth check
        return
    if headers is None or not headers:
        # No headers means not HTTP transport (stdio mode), skip auth check
        return
    auth_header = headers.get("authorization") or headers.get("Authorization") or ""
    scheme, _, provided = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not provided.strip():
        raise PermissionError("Unauthorized")
    expected = os.getenv("MCP_HTTP_AUTH_TOKEN", "").strip()
    if not expected:
        raise PermissionError("Unauthorized: MCP_HTTP_AUTH_TOKEN not set")
    if provided.strip() != expected:
        raise PermissionError("Unauthorized")


def _parse_amount(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(" ", "")
        if cleaned == "":
            return None
        cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
        for fmt in (
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%d.%m.%Y",
        ):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None
    return None


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _similarity(needle: str, haystack: str) -> float:
    if not needle:
        return 1.0
    if not haystack:
        return 0.0
    # Exact substring match
    if needle in haystack:
        return 1.0
    # Check if needle is contained in any word (handles plural/singular variations)
    # e.g., "grocery" matches "groceries", "shop" matches "shopping"
    haystack_words = haystack.split()
    for word in haystack_words:
        if needle in word or word in needle:
            return 1.0
    # Fall back to fuzzy matching for partial matches
    return SequenceMatcher(None, needle, haystack).ratio()


EXPECTED_HEADERS = [
    "#",
    "Account",
    "Date",
    "Value Date",
    "Amount",
    "Currency",
    "Name",
    "Number",
    "Bank",
    "Reason",
    "Category",
    "Subcategory",
    "Category-Path",
    "Tags",
    "Note",
    "Posting Text",
]

_TRANSACTIONS: list[dict[str, Any]] = []
_TRANSACTION_KEYS: set[str] = set()
_DATA_LOADED = False
_STORE_METADATA: dict[str, Any] = {"files_scanned": 0}


def _csv_directory() -> Path:
    return Path(os.getenv("OUTBANK_CSV_DIR", "./outbank_exports")).expanduser()


def _csv_glob() -> str:
    return os.getenv("OUTBANK_CSV_GLOB", "*.csv")


def _validate_headers(fieldnames: list[str] | None, source_file: str) -> None:
    if not fieldnames:
        raise ValueError(f"{source_file} has no headers")
    missing = [header for header in EXPECTED_HEADERS if header not in fieldnames]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"{source_file} is missing headers: {missing_list}")


def _list_csv_files() -> list[Path]:
    csv_dir = _csv_directory()
    if not csv_dir.exists():
        raise ValueError(f"CSV folder not found: {csv_dir}")
    files = sorted(csv_dir.glob(_csv_glob()))
    if not files:
        raise ValueError(f"No CSV files found in {csv_dir}")
    return files


def _format_date(value: date | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _split_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def _normalize_transaction(row: dict[str, Any], source_file: str, row_index: int) -> dict[str, Any]:
    row_id = str(row.get("#") or "").strip()
    if not row_id:
        row_id = str(row_index)

    booking_date = _format_date(_parse_date(row.get("Date")))
    value_date = _format_date(_parse_date(row.get("Value Date")))
    amount = _parse_amount(row.get("Amount"))
    tags = _split_tags(row.get("Tags"))
    record_key = f"{source_file}:{row_id}"

    return {
        "id": row_id,
        "account": str(row.get("Account") or "").strip(),
        "booking_date": booking_date,
        "value_date": value_date,
        "amount": amount,
        "currency": str(row.get("Currency") or "").strip(),
        "name": str(row.get("Name") or "").strip(),
        "number": str(row.get("Number") or "").strip(),
        "bank": str(row.get("Bank") or "").strip(),
        "reason": str(row.get("Reason") or "").strip(),
        "category": str(row.get("Category") or "").strip(),
        "subcategory": str(row.get("Subcategory") or "").strip(),
        "category_path": str(row.get("Category-Path") or "").strip(),
        "tags": tags,
        "note": str(row.get("Note") or "").strip(),
        "posting_text": str(row.get("Posting Text") or "").strip(),
        "source_file": source_file,
        "record_key": record_key,
    }


def _load_transactions() -> tuple[list[dict[str, Any]], set[str], int, int, int]:
    """Load transactions from CSV files.

    Returns:
        Tuple of (transactions list, transaction keys set, file count, excluded count, total parsed count)
    """
    transactions: list[dict[str, Any]] = []
    keys: set[str] = set()
    excluded_count = 0
    total_parsed = 0
    files = _list_csv_files()

    for file_path in files:
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";")
            _validate_headers(reader.fieldnames, file_path.name)
            for row_index, row in enumerate(reader, start=1):
                if not row or not any(value for value in row.values()):
                    continue
                transaction = _normalize_transaction(row, file_path.name, row_index)
                total_parsed += 1

                # Apply exclusion filters
                if _should_exclude_transaction(transaction):
                    excluded_count += 1
                    continue

                key = transaction["record_key"]
                if key in keys:
                    continue
                keys.add(key)
                transactions.append(transaction)

    return transactions, keys, len(files), excluded_count, total_parsed


def _ensure_loaded() -> None:
    if not _DATA_LOADED:
        _reload_transactions()


def _reload_transactions() -> dict[str, Any]:
    global _DATA_LOADED, _STORE_METADATA, _TRANSACTION_KEYS, _TRANSACTIONS
    old_keys = set(_TRANSACTION_KEYS)
    transactions, keys, file_count, excluded_count, total_parsed = _load_transactions()

    _TRANSACTIONS = transactions
    _TRANSACTION_KEYS = keys
    _DATA_LOADED = True
    _STORE_METADATA = {
        "files_scanned": file_count,
        "excluded_count": excluded_count,
        "total_parsed": total_parsed,
    }

    return {
        "files_scanned": file_count,
        "total_records": len(keys),
        "new_records": len(keys - old_keys),
        "removed_records": len(old_keys - keys),
        "excluded_count": excluded_count,
        "total_parsed": total_parsed,
    }


def _row_matches_filters(
    row: dict[str, Any],
    account: str | None,
    iban: str | None,
    amount: float | None,
    amount_min: float | None,
    amount_max: float | None,
    date_exact: date | None,
    date_start: date | None,
    date_end: date | None,
) -> bool:
    row_account = _normalize_text(row.get("account"))
    row_iban = _normalize_text(row.get("number")).replace(" ", "")
    row_amount = _parse_amount(row.get("amount"))
    row_date = _parse_date(row.get("booking_date"))

    if account and account not in row_account:
        return False
    if iban and iban.replace(" ", "") not in row_iban:
        return False
    if amount is not None and (row_amount is None or abs(row_amount - amount) > 0.0001):
        return False
    if amount_min is not None and (row_amount is None or row_amount < amount_min):
        return False
    if amount_max is not None and (row_amount is None or row_amount > amount_max):
        return False
    if date_exact is not None and row_date != date_exact:
        return False
    if date_start is not None and (row_date is None or row_date < date_start):
        return False
    if date_end is not None and (row_date is None or row_date > date_end):
        return False
    return True


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    description = row.get("reason") or row.get("posting_text") or ""
    return {
        "id": row.get("id"),
        "date": row.get("booking_date"),
        "value_date": row.get("value_date"),
        "amount": row.get("amount"),
        "currency": row.get("currency"),
        "account": row.get("account"),
        "iban": row.get("number"),
        "counterparty": row.get("name"),
        "description": description,
        "category": row.get("category"),
        "subcategory": row.get("subcategory"),
        "category_path": row.get("category_path"),
        "tags": row.get("tags"),
        "note": row.get("note"),
        "posting_text": row.get("posting_text"),
        "source_file": row.get("source_file"),
    }


def _apply_sort(rows: list[dict[str, Any]], sort: str) -> list[dict[str, Any]]:
    direction = -1 if sort.startswith("-") else 1
    key = sort.lstrip("-")
    if key not in {"date", "amount"}:
        return rows

    def sort_key(item: dict[str, Any]) -> tuple[int, Any]:
        value = item.get(key)
        if key == "date":
            parsed = _parse_date(value)
            return (0, parsed or date.min)
        if key == "amount":
            return (0, item.get("amount") or 0.0)
        return (0, value)

    return sorted(rows, key=sort_key, reverse=direction < 0)


class HTTPAuthMiddleware(Middleware):
    """Middleware to enforce HTTP authentication for all requests.

    Only applies to HTTP transport - stdio transport bypasses this.
    """

    async def __call__(self, context: MiddlewareContext[Any], call_next: Any) -> Any:
        """Check authentication before processing any request."""
        # Check if we're using HTTP transport by trying to get headers
        try:
            headers = get_http_headers()
        except Exception:
            # No headers available - likely stdio transport, allow it
            return await call_next(context)

        if headers is None or not headers:
            # No headers - likely stdio transport, allow it
            return await call_next(context)

        # We have headers, so we're in HTTP mode - require auth
        auth_header = headers.get("authorization") or headers.get("Authorization") or ""
        scheme, _, provided = auth_header.partition(" ")
        if scheme.lower() != "bearer" or not provided.strip():
            raise PermissionError("Unauthorized: Missing or invalid bearer token")

        expected = os.getenv("MCP_HTTP_AUTH_TOKEN", "").strip()
        if not expected:
            raise PermissionError("Unauthorized: MCP_HTTP_AUTH_TOKEN not configured")

        if provided.strip() != expected:
            raise PermissionError("Unauthorized: Invalid bearer token")

        return await call_next(context)


class RequestSizeLimitMiddleware(Middleware):
    """Middleware to enforce maximum request size limits.

    Only applies to HTTP transport where Content-Length is available.
    """

    def __init__(self, max_size: int = 1048576):
        """Initialize with max request size in bytes (default 1MB)."""
        self.max_size = max_size

    async def __call__(self, context: MiddlewareContext[Any], call_next: Any) -> Any:
        """Check request size before processing."""
        try:
            headers = get_http_headers()
        except Exception:
            return await call_next(context)

        if headers is None or not headers:
            return await call_next(context)

        # Check Content-Length header
        content_length = headers.get("content-length") or headers.get("Content-Length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    raise ValueError(
                        f"Request payload too large: {size} bytes exceeds limit of {self.max_size} bytes"
                    )
            except ValueError as e:
                if "too large" in str(e):
                    raise
                # Invalid Content-Length header, let it through

        return await call_next(context)


class AuditLoggingMiddleware(Middleware):
    """Middleware to log all tool invocations for audit trail."""

    async def __call__(self, context: MiddlewareContext[Any], call_next: Any) -> Any:
        """Log tool invocation and execute."""
        # Get client IP if available (HTTP transport)
        client_ip = None
        try:
            headers = get_http_headers()
            if headers:
                # Try common headers for client IP
                client_ip = (
                    headers.get("x-forwarded-for")
                    or headers.get("X-Forwarded-For")
                    or headers.get("x-real-ip")
                    or headers.get("X-Real-IP")
                )
                if client_ip:
                    # Take first IP if comma-separated
                    client_ip = client_ip.split(",")[0].strip()
        except Exception:
            pass

        # Extract tool name and arguments from context
        tool_name = getattr(context, "tool_name", None) or getattr(context, "name", "unknown")
        arguments = getattr(context, "arguments", {}) or {}

        # Log before execution
        _audit_log(tool_name, arguments, client_ip)

        # Execute the tool
        return await call_next(context)


# Create FastMCP server with middleware for HTTP transport
# Check transport mode from environment directly to avoid function dependency
_transport_env = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

# Build middleware list for HTTP transport
_http_middlewares: list[Middleware] = []
if _transport_env == "http":
    _http_middlewares.append(HTTPAuthMiddleware())
    _http_middlewares.append(RequestSizeLimitMiddleware(_env_max_request_size()))

    # Add rate limiting if configured
    _rate_limit = _env_rate_limit()
    if _rate_limit:
        _http_middlewares.append(
            RateLimitingMiddleware(max_requests_per_second=_rate_limit, global_limit=True)
        )

    if _env_audit_enabled():
        _http_middlewares.append(AuditLoggingMiddleware())

mcp = FastMCP("finance-mcp", middleware=_http_middlewares)


@mcp.tool()
def search_transactions(
    query: str | None = None,
    account: str | None = None,
    iban: str | None = None,
    amount: float | None = None,
    amount_min: float | None = None,
    amount_max: float | None = None,
    date: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    max_results: int = 25,
    sort: str = "-date",
) -> dict[str, Any]:
    """Search transactions with fuzzy matching and optional filters.

    Inputs are optional unless noted:
    - query: free-text search needle
    - account, iban: string filters
    - amount, amount_min, amount_max: numeric filters
    - date, date_start, date_end: ISO dates (YYYY-MM-DD)
    - max_results: limit for returned results (default 25)
    - sort: -date, date, -amount, amount
    """
    _require_http_auth()
    _ensure_loaded()

    account_norm = _normalize_text(account)
    iban_norm = _normalize_text(iban)
    query_norm = _normalize_text(query)

    date_exact = _parse_date(date)
    range_start = _parse_date(date_start)
    range_end = _parse_date(date_end)
    if date and date_exact is None:
        raise ValueError("date must be ISO format like YYYY-MM-DD")
    if date_start and range_start is None:
        raise ValueError("date_start must be ISO format like YYYY-MM-DD")
    if date_end and range_end is None:
        raise ValueError("date_end must be ISO format like YYYY-MM-DD")

    results: list[dict[str, Any]] = []
    min_score = _env_float("MCP_MIN_SCORE", 0.55)

    for row in _TRANSACTIONS:
        if not _row_matches_filters(
            row,
            account_norm,
            iban_norm,
            amount,
            amount_min,
            amount_max,
            date_exact,
            range_start,
            range_end,
        ):
            continue

        haystack = " ".join(
            [
                _normalize_text(row.get("account")),
                _normalize_text(row.get("number")),
                _normalize_text(row.get("reason")),
                _normalize_text(row.get("name")),
                _normalize_text(row.get("posting_text")),
                _normalize_text(row.get("category")),
                _normalize_text(row.get("subcategory")),
                _normalize_text(row.get("category_path")),
            ]
        )
        score = _similarity(query_norm, haystack)
        if query_norm and score < min_score:
            continue

        normalized = _normalize_row(row)
        normalized["score"] = round(score, 4)
        results.append(normalized)

    sorted_results = _apply_sort(results, sort)
    limited = sorted_results[: max(1, max_results)]

    return {
        "filters": {
            "query": query,
            "account": account,
            "iban": iban,
            "amount": amount,
            "amount_min": amount_min,
            "amount_max": amount_max,
            "date": date,
            "date_start": date_start,
            "date_end": date_end,
            "sort": sort,
            "max_results": max_results,
        },
        "summary": {
            "matched": len(results),
            "returned": len(limited),
            "truncated": len(limited) < len(results),
        },
        "results": limited,
    }


@mcp.tool()
def describe_fields() -> dict[str, Any]:
    """Return current CSV configuration and expected headers."""
    _require_http_auth()
    _ensure_loaded()
    return {
        "csv_dir": str(_csv_directory()),
        "csv_glob": _csv_glob(),
        "expected_headers": list(EXPECTED_HEADERS),
        "files_scanned": _STORE_METADATA.get("files_scanned", 0),
        "total_records": len(_TRANSACTIONS),
    }


@mcp.tool()
def reload_transactions() -> dict[str, Any]:
    """Reload CSV files and return record statistics."""
    _require_http_auth()
    return _reload_transactions()


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Return server health status for monitoring.

    Returns:
    - status: "healthy" if operational
    - uptime_seconds: seconds since server start
    - data_loaded: whether transaction data is loaded
    - record_count: number of transactions in memory
    - files_scanned: number of CSV files loaded
    - transport_mode: current transport (stdio/http)
    """
    _require_http_auth()

    uptime = time.time() - _SERVER_START_TIME

    return {
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "data_loaded": _DATA_LOADED,
        "record_count": len(_TRANSACTIONS),
        "files_scanned": _STORE_METADATA.get("files_scanned", 0),
        "transport_mode": _transport_mode(),
    }


def _transport_mode() -> str:
    mode = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    if mode not in {"http", "stdio"}:
        raise ValueError("MCP_TRANSPORT must be 'http' or 'stdio'")
    return mode


def _validate_token_security(token: str) -> None:
    """Validate token meets basic security requirements.

    Requirements:
    - Minimum 16 characters (enforced)
    - Recommended 32+ characters (warning)
    - Warns about weak patterns (all same char, common words)

    Raises ValueError if minimum requirements not met.
    """
    if len(token) < 16:
        raise ValueError(
            f"MCP_HTTP_AUTH_TOKEN must be at least 16 characters long (current: {len(token)}). "
            "For better security, use 32+ characters. "
            "Generate a secure token with: "
            'python -c "import secrets; print(secrets.token_urlsafe(32))"'
        )

    # Check for weak patterns (warn but don't fail)
    warnings = []

    if len(token) < 32:
        warnings.append(
            f"Token is {len(token)} characters. For better security, use 32+ characters."
        )

    # Check if all characters are the same
    if len(set(token)) == 1:
        warnings.append("Token contains only one unique character. Use a more diverse token.")

    # Check for common weak patterns
    common_weak = ["password", "secret", "token", "admin", "test", "123456", "qwerty"]
    token_lower = token.lower()
    if any(pattern in token_lower for pattern in common_weak):
        warnings.append("Token contains common weak patterns. Use a randomly generated token.")

    # Check entropy (rough estimate: unique characters / length)
    unique_ratio = len(set(token)) / len(token) if token else 0
    if unique_ratio < 0.3:
        warnings.append("Token has low character diversity. Use a randomly generated token.")

    if warnings:
        import warnings as py_warnings

        for warning in warnings:
            py_warnings.warn(f"Token security warning: {warning}", UserWarning, stacklevel=2)


def _validate_http_auth_config() -> None:
    """Validate that HTTP auth token is configured and secure when using HTTP transport."""
    transport = _transport_mode()
    if transport == "http":
        token = os.getenv("MCP_HTTP_AUTH_TOKEN", "").strip()
        if not token:
            raise ValueError(
                "MCP_HTTP_AUTH_TOKEN is required when using HTTP transport. "
                "Set MCP_HTTP_AUTH_TOKEN in your environment or .env file. "
                "For local-only use, consider using stdio transport (MCP_TRANSPORT=stdio) "
                "which does not require authentication. "
                "Generate a secure token with: "
                'python -c "import secrets; print(secrets.token_urlsafe(32))"'
            )
        _validate_token_security(token)


def _display_startup_info() -> None:
    """Display startup information using rich formatting.

    Prints to stderr to avoid interfering with stdio transport JSON-RPC communication.
    """
    # Use stderr for startup info to avoid interfering with stdio transport
    console = Console(file=sys.stderr)

    # Load transactions to get counts (always reload to get accurate stats)
    try:
        stats = _reload_transactions()
        total_records = stats.get("total_records", 0)
        excluded_count = stats.get("excluded_count", 0)
        total_parsed = stats.get("total_parsed", 0)
        files_scanned = stats.get("files_scanned", 0)
    except Exception as e:
        console.print(f"[red]Warning: Could not load transactions: {e}[/red]")
        total_records = 0
        excluded_count = 0
        total_parsed = 0
        files_scanned = 0

    # Get configuration
    transport = _transport_mode()
    csv_dir = _csv_directory()
    csv_glob = _csv_glob()
    # Use display version to preserve original case for user-friendly output
    excluded_categories_display = _env_exclusion_list_display("EXCLUDED_CATEGORIES")
    excluded_tags_display = _env_exclusion_list_display("EXCLUDED_TAGS")

    # Create info table
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("[bold cyan]Transport:[/bold cyan]", f"[green]{transport.upper()}[/green]")

    if transport == "http":
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = _env_int("MCP_PORT", 6668)
        table.add_row(
            "[bold cyan]Endpoint:[/bold cyan]", f"[yellow]http://{host}:{port}/mcp[/yellow]"
        )
        table.add_row("[bold cyan]Auth:[/bold cyan]", "[green]Required (Bearer token)[/green]")

    table.add_row("", "")  # Spacer
    table.add_row("[bold cyan]CSV Directory:[/bold cyan]", f"[white]{csv_dir}[/white]")
    table.add_row("[bold cyan]CSV Pattern:[/bold cyan]", f"[white]{csv_glob}[/white]")
    table.add_row("[bold cyan]Files Scanned:[/bold cyan]", f"[white]{files_scanned}[/white]")

    table.add_row("", "")  # Spacer
    table.add_row("[bold cyan]Transactions Found:[/bold cyan]", f"[white]{total_parsed:,}[/white]")

    if excluded_count > 0:
        table.add_row(
            "[bold cyan]Transactions Excluded:[/bold cyan]", f"[yellow]{excluded_count:,}[/yellow]"
        )

    table.add_row(
        "[bold cyan]Transactions Loaded:[/bold cyan]", f"[green]{total_records:,}[/green]"
    )

    # Show exclusion filters if configured (using display version to preserve original case)
    if excluded_categories_display or excluded_tags_display:
        table.add_row("", "")  # Spacer
        table.add_row("[bold yellow]Exclusion Filters:[/bold yellow]", "")

        if excluded_categories_display:
            categories_text = ", ".join(excluded_categories_display)
            table.add_row("  [dim]Categories:[/dim]", f"[yellow]{categories_text}[/yellow]")

        if excluded_tags_display:
            tags_text = ", ".join(excluded_tags_display)
            table.add_row("  [dim]Tags:[/dim]", f"[yellow]{tags_text}[/yellow]")

    # Create panel
    title = Text("Finance MCP Server", style="bold green")
    if transport == "http":
        title.append(" (HTTP)", style="bold yellow")
    else:
        title.append(" (Stdio)", style="bold cyan")

    panel = Panel(
        table,
        title=title,
        border_style="green",
        padding=(1, 2),
    )

    console.print(panel)

    if transport == "stdio":
        console.print(
            "[dim]Server running in stdio mode. Ready for MCP client connections.[/dim]\n"
        )
    else:
        console.print(
            f"[dim]Server running on http://{os.getenv('MCP_HOST', '127.0.0.1')}:{_env_int('MCP_PORT', 6668)}/mcp[/dim]\n"
        )


if __name__ == "__main__":
    transport = _transport_mode()

    # Display startup information
    _display_startup_info()

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        _validate_http_auth_config()
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = _env_int("MCP_PORT", 6668)
        # Use streamable-http transport which supports stateless JSON responses
        mcp.run(transport="streamable-http", host=host, port=port)
