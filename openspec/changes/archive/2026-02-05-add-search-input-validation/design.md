## Context

The `search_transactions` function currently validates date format but doesn't check for conflicting filters or invalid ranges. The validation needs to happen after parsing dates/amounts but before the filtering logic runs.

## Goals / Non-Goals

**Goals:**
- Validate filter combinations and ranges early in the function
- Return clear, actionable error messages
- Maintain backward compatibility for valid inputs
- Keep validation logic simple and readable

**Non-Goals:**
- Changing the function signature or return format
- Adding new filter types or capabilities
- Optimizing the filtering logic itself

## Decisions

### Decision 1: Validation placement

Place validation immediately after parsing dates and before the main filtering loop. This ensures invalid inputs fail fast and provides clear error messages before any processing occurs.

### Decision 2: Error message format

Use `ValueError` with descriptive messages that clearly indicate what's wrong:
- "Cannot use 'date' filter together with 'date_start' or 'date_end'"
- "date_start must be less than or equal to date_end"
- Similar patterns for amount filters

### Decision 3: Validation order

Check conflicts first (date vs date range, amount vs amount range), then check ranges (start ≤ end). This provides the most logical error flow.
