# Change: Update finance MCP to read Outbank CSV folders

## Why
The current NocoDB + Docker setup is heavier than needed for local querying. A CSV-folder based MCP keeps the workflow simple while preserving local-first privacy.

## What Changes
- Replace NocoDB API access with folder-based CSV ingestion for Outbank exports
- Normalize CSV rows into an in-memory JSON representation for query operations
- Remove the requirement to run NocoDB or Docker for the MCP service
- Document the expected CSV header format and folder configuration
- Provide Python-first setup guidance using `uv`
- Add an MCP tool to reload CSV data without restarting the service

## Anonymized CSV sample
```
#;Account;Date;Value Date;Amount;Currency;Name;Number;Bank;Reason;Category;Subcategory;Category-Path;Tags;Note;Posting Text
1;DE00123456780000000000;18.01.2026;19.01.2026;-13,11;EUR;"Merchant A";"49277105";"Sample Bank";"Parking zone 5";"Category A";"Subcategory A";"Category A / Subcategory A";"commute,work";"Receipt stored";"Card payment"
```

## Normalized JSON example
```json
{
  "id": "1",
  "account": "DE00123456780000000000",
  "booking_date": "2026-01-18",
  "value_date": "2026-01-19",
  "amount": -13.11,
  "currency": "EUR",
  "name": "Merchant A",
  "number": "49277105",
  "bank": "Sample Bank",
  "reason": "Parking zone 5",
  "category": "Category A",
  "subcategory": "Subcategory A",
  "category_path": "Category A / Subcategory A",
  "tags": ["commute", "work"],
  "note": "Receipt stored",
  "posting_text": "Card payment",
  "source_file": "outbank_export_example.csv"
}
```

## Impact
- Affected specs: finance-mcp
- Affected code: `services/finance-mcp/app.py`, README/docs for setup guidance
