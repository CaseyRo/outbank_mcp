## MODIFIED Requirements

### Requirement: Input Validation for Search Filters
The `search_transactions` tool SHALL validate filter combinations and ranges, returning clear error messages for invalid inputs.

#### Scenario: Reject conflicting date filters
- **WHEN** `search_transactions` is called with both `date` and `date_start` parameters
- **THEN** the function raises `ValueError` with a message indicating conflicting date filters

#### Scenario: Reject conflicting date filters (date_end)
- **WHEN** `search_transactions` is called with both `date` and `date_end` parameters
- **THEN** the function raises `ValueError` with a message indicating conflicting date filters

#### Scenario: Reject invalid date range
- **WHEN** `search_transactions` is called with `date_start` greater than `date_end` (e.g., start="2024-12-31", end="2024-01-01")
- **THEN** the function raises `ValueError` with a message indicating invalid date range

#### Scenario: Reject conflicting amount filters
- **WHEN** `search_transactions` is called with both `amount` and `amount_min` parameters
- **THEN** the function raises `ValueError` with a message indicating conflicting amount filters

#### Scenario: Reject conflicting amount filters (amount_max)
- **WHEN** `search_transactions` is called with both `amount` and `amount_max` parameters
- **THEN** the function raises `ValueError` with a message indicating conflicting amount filters

#### Scenario: Reject invalid amount range
- **WHEN** `search_transactions` is called with `amount_min` greater than `amount_max` (e.g., min=100, max=-100)
- **THEN** the function raises `ValueError` with a message indicating invalid amount range

#### Scenario: Allow valid filter combinations
- **WHEN** `search_transactions` is called with valid filter combinations (e.g., `date` alone, or `date_start`/`date_end` together, or `amount_min`/`amount_max` together)
- **AND** ranges are valid (start ≤ end)
- **THEN** the function processes the search normally without raising errors
