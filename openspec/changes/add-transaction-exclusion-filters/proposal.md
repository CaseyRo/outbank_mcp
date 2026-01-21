# Change: Add transaction exclusion filters via .env configuration

## Why
Users may want to exclude certain transaction types from their queries (e.g., internal transfers between accounts, specific categories like "Transfer"). Currently, all transactions loaded from CSV files are included in search results. Adding configurable exclusion filters allows users to filter out noise at the data loading level, ensuring excluded transactions never appear in query results without requiring filter parameters on every search call.

## What Changes
- Add `.env` configuration variables for excluded categories and tags (comma-separated lists)
- Modify transaction loading logic to filter out transactions matching excluded categories or tags during CSV ingestion
- Update `.env.example` to document the new exclusion filter options
- Ensure excluded transactions are never added to the in-memory transaction store
- Excluded transactions should be filtered case-insensitively and support partial matches

## Impact
- Affected specs: finance-mcp
- Affected code: `app.py` (transaction loading and filtering logic), `.env.example` (documentation)
- Operational impact: Users can configure exclusion filters once in `.env` rather than filtering in every query
