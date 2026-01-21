# Outbank CSV Import

Outbank exports use semicolon delimiters and German date formats (`DD.MM.YYYY`).

## CSV headers
The MCP service expects the following headers (semicolon-delimited):
```
#;Account;Date;Value Date;Amount;Currency;Name;Number;Bank;Reason;Category;Subcategory;Category-Path;Tags;Note;Posting Text
```

## Import steps
1. Export CSVs from Outbank.
2. Place the CSV files in the folder configured by `OUTBANK_CSV_DIR`.
3. (Optional) Call `reload_transactions` to refresh without restarting.

## Notes
- The service reads all matching CSV files in the folder and aggregates them in memory.
- Dates and amounts are normalized for query filters and sorting.
