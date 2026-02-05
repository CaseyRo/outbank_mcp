## Why

The `search_transactions` function accepts conflicting filter combinations (e.g., `date` with `date_start`/`date_end`, or `amount` with `amount_min`/`amount_max`) and invalid ranges (start > end) without validation. This leads to confusing behavior and doesn't match the expected behavior defined in `tests/features/invalid_inputs.feature`. Adding validation provides clear error messages and prevents ambiguous queries.

## What Changes

- Add validation to reject conflicting date filters (`date` cannot be used with `date_start`/`date_end`)
- Add validation to reject conflicting amount filters (`amount` cannot be used with `amount_min`/`amount_max`)
- Add validation to reject invalid date ranges (`date_start` must be ≤ `date_end`)
- Add validation to reject invalid amount ranges (`amount_min` must be ≤ `amount_max`)
- Return clear `ValueError` messages for each validation failure

## Capabilities

### Modified Capabilities
- `search_transactions`: Now validates filter combinations and ranges before processing, returning clear errors for invalid inputs

## Impact

- `app.py`: Add validation logic in `search_transactions` function (~20-30 lines)
