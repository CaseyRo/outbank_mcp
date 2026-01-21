import csv
import os
from datetime import date, datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers


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


def _http_auth_enabled() -> bool:
    token = os.getenv("MCP_HTTP_AUTH_TOKEN", "").strip()
    if os.getenv("MCP_HTTP_AUTH_ENABLED") is None:
        return bool(token)
    return _env_bool("MCP_HTTP_AUTH_ENABLED", False)


def _require_http_auth() -> None:
    if not _http_auth_enabled():
        return
    try:
        headers = get_http_headers()
    except Exception:
        return
    if not headers:
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


def _parse_amount(value: Any) -> Optional[float]:
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


def _parse_date(value: Any) -> Optional[date]:
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
    if needle in haystack:
        return 1.0
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

_TRANSACTIONS: List[Dict[str, Any]] = []
_TRANSACTION_KEYS: Set[str] = set()
_DATA_LOADED = False
_STORE_METADATA: Dict[str, Any] = {"files_scanned": 0}


def _csv_directory() -> Path:
    return Path(os.getenv("OUTBANK_CSV_DIR", "./outbank_exports")).expanduser()


def _csv_glob() -> str:
    return os.getenv("OUTBANK_CSV_GLOB", "*.csv")


def _validate_headers(fieldnames: Optional[List[str]], source_file: str) -> None:
    if not fieldnames:
        raise ValueError(f"{source_file} has no headers")
    missing = [header for header in EXPECTED_HEADERS if header not in fieldnames]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"{source_file} is missing headers: {missing_list}")


def _list_csv_files() -> List[Path]:
    csv_dir = _csv_directory()
    if not csv_dir.exists():
        raise ValueError(f"CSV folder not found: {csv_dir}")
    files = sorted(csv_dir.glob(_csv_glob()))
    if not files:
        raise ValueError(f"No CSV files found in {csv_dir}")
    return files


def _format_date(value: Optional[date]) -> Optional[str]:
    if value is None:
        return None
    return value.isoformat()


def _split_tags(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def _normalize_transaction(
    row: Dict[str, Any], source_file: str, row_index: int
) -> Dict[str, Any]:
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


def _load_transactions() -> Tuple[List[Dict[str, Any]], Set[str], int]:
    transactions: List[Dict[str, Any]] = []
    keys: Set[str] = set()
    files = _list_csv_files()

    for file_path in files:
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";")
            _validate_headers(reader.fieldnames, file_path.name)
            for row_index, row in enumerate(reader, start=1):
                if not row or not any(value for value in row.values()):
                    continue
                transaction = _normalize_transaction(row, file_path.name, row_index)
                key = transaction["record_key"]
                if key in keys:
                    continue
                keys.add(key)
                transactions.append(transaction)

    return transactions, keys, len(files)


def _ensure_loaded() -> None:
    if not _DATA_LOADED:
        _reload_transactions()


def _reload_transactions() -> Dict[str, Any]:
    global _DATA_LOADED, _STORE_METADATA, _TRANSACTION_KEYS, _TRANSACTIONS
    old_keys = set(_TRANSACTION_KEYS)
    transactions, keys, file_count = _load_transactions()

    _TRANSACTIONS = transactions
    _TRANSACTION_KEYS = keys
    _DATA_LOADED = True
    _STORE_METADATA = {"files_scanned": file_count}

    return {
        "files_scanned": file_count,
        "total_records": len(keys),
        "new_records": len(keys - old_keys),
        "removed_records": len(old_keys - keys),
    }


def _row_matches_filters(
    row: Dict[str, Any],
    account: Optional[str],
    iban: Optional[str],
    amount: Optional[float],
    amount_min: Optional[float],
    amount_max: Optional[float],
    date_exact: Optional[date],
    date_start: Optional[date],
    date_end: Optional[date],
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


def _normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
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


def _apply_sort(rows: List[Dict[str, Any]], sort: str) -> List[Dict[str, Any]]:
    direction = -1 if sort.startswith("-") else 1
    key = sort.lstrip("-")
    if key not in {"date", "amount"}:
        return rows

    def sort_key(item: Dict[str, Any]) -> Tuple[int, Any]:
        value = item.get(key)
        if key == "date":
            parsed = _parse_date(value)
            return (0, parsed or date.min)
        if key == "amount":
            return (0, item.get("amount") or 0.0)
        return (0, value)

    return sorted(rows, key=sort_key, reverse=direction < 0)


mcp = FastMCP("finance-mcp")


@mcp.tool()
def search_transactions(
    query: Optional[str] = None,
    account: Optional[str] = None,
    iban: Optional[str] = None,
    amount: Optional[float] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    date: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    max_results: int = 25,
    sort: str = "-date",
) -> Dict[str, Any]:
    """Search transactions with fuzzy matching and optional filters."""
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

    results: List[Dict[str, Any]] = []
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
def describe_fields() -> Dict[str, Any]:
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
def reload_transactions() -> Dict[str, Any]:
    """Reload CSV files and return record statistics."""
    _require_http_auth()
    return _reload_transactions()


if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = _env_int("MCP_PORT", 6668)
    mcp.run(transport="http", host=host, port=port)
