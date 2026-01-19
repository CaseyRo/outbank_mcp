import json
import os
from dataclasses import dataclass
from datetime import datetime, date
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
from fastmcp import FastMCP


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


def _parse_amount(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(" ", "")
        if cleaned == "":
            return None
        cleaned = cleaned.replace(",", ".")
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
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
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


@dataclass(frozen=True)
class FieldMap:
    row_id: str
    date: str
    amount: str
    currency: str
    account: str
    iban: str
    description: str
    counterparty: str


def _load_field_map() -> FieldMap:
    return FieldMap(
        row_id=os.getenv("NOCODB_FIELD_ID", "id"),
        date=os.getenv("NOCODB_FIELD_DATE", "booking_date"),
        amount=os.getenv("NOCODB_FIELD_AMOUNT", "amount"),
        currency=os.getenv("NOCODB_FIELD_CURRENCY", "currency"),
        account=os.getenv("NOCODB_FIELD_ACCOUNT", "account"),
        iban=os.getenv("NOCODB_FIELD_IBAN", "counterparty_account"),
        description=os.getenv("NOCODB_FIELD_DESCRIPTION", "reason"),
        counterparty=os.getenv("NOCODB_FIELD_COUNTERPARTY", "counterparty_name"),
    )


class NocoDBClient:
    def __init__(self) -> None:
        base_url = os.getenv("NOCODB_BASE_URL", "http://nocodb:8080").rstrip("/")
        table = os.getenv("NOCODB_TABLE")
        if not table:
            raise ValueError("NOCODB_TABLE is required (table id or name)")
        self.base_url = base_url
        self.table = table
        self.view_id = os.getenv("NOCODB_VIEW_ID")
        self.page_size = _env_int("NOCODB_PAGE_SIZE", 200)
        self.max_pages = _env_int("NOCODB_MAX_PAGES", 5)
        token = os.getenv("NOCODB_TOKEN")
        self.headers = {"xc-token": token} if token else {}

    def fetch_rows(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        offset = 0
        for _ in range(self.max_pages):
            params: Dict[str, Any] = {"limit": self.page_size, "offset": offset}
            if self.view_id:
                params["viewId"] = self.view_id
            response = requests.get(
                f"{self.base_url}/api/v2/tables/{self.table}/records",
                headers=self.headers,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
            batch = (
                payload.get("list")
                or payload.get("records")
                or payload.get("data")
                or []
            )
            if not isinstance(batch, list):
                raise ValueError("Unexpected NocoDB response format")
            rows.extend(batch)
            if len(batch) < self.page_size:
                break
            offset += self.page_size
        return rows


def _row_matches_filters(
    row: Dict[str, Any],
    fields: FieldMap,
    account: Optional[str],
    iban: Optional[str],
    amount: Optional[float],
    amount_min: Optional[float],
    amount_max: Optional[float],
    date_exact: Optional[date],
    date_start: Optional[date],
    date_end: Optional[date],
) -> bool:
    row_account = _normalize_text(row.get(fields.account))
    row_iban = _normalize_text(row.get(fields.iban)).replace(" ", "")
    row_amount = _parse_amount(row.get(fields.amount))
    row_date = _parse_date(row.get(fields.date))

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


def _normalize_row(row: Dict[str, Any], fields: FieldMap) -> Dict[str, Any]:
    return {
        "id": row.get(fields.row_id),
        "date": row.get(fields.date),
        "amount": _parse_amount(row.get(fields.amount)),
        "currency": row.get(fields.currency),
        "account": row.get(fields.account),
        "iban": row.get(fields.iban),
        "counterparty": row.get(fields.counterparty),
        "description": row.get(fields.description),
        "source_table": os.getenv("NOCODB_TABLE"),
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
    client = NocoDBClient()
    fields = _load_field_map()

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

    rows = client.fetch_rows()
    results: List[Dict[str, Any]] = []
    min_score = _env_float("MCP_MIN_SCORE", 0.55)

    for row in rows:
        if not _row_matches_filters(
            row,
            fields,
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
                _normalize_text(row.get(fields.account)),
                _normalize_text(row.get(fields.iban)),
                _normalize_text(row.get(fields.description)),
                _normalize_text(row.get(fields.counterparty)),
            ]
        )
        score = _similarity(query_norm, haystack)
        if query_norm and score < min_score:
            continue

        normalized = _normalize_row(row, fields)
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
    """Return current NocoDB field mapping configuration."""
    fields = _load_field_map()
    return {
        "table": os.getenv("NOCODB_TABLE"),
        "view_id": os.getenv("NOCODB_VIEW_ID"),
        "field_map": json.loads(json.dumps(fields.__dict__)),
    }


if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = _env_int("MCP_PORT", 6668)
    mcp.run(transport="http", host=host, port=port)
