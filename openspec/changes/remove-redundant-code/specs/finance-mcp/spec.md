## UPDATED Requirements (code hygiene)

### Requirement: No redundant re-exports
The application SHALL import exclusion filter helpers directly from the `exclusion_filters` module. It SHALL NOT re-export or alias those symbols in `app.py` for "backwards compatibility" when no other code depends on importing them from `app`.

#### Scenario: Exclusion logic uses exclusion_filters directly
- **GIVEN** the MCP server application
- **WHEN** transaction loading or filtering uses exclusion list or match helpers
- **THEN** those helpers are imported from `exclusion_filters` and used by name (e.g. `should_exclude_transaction`, `env_exclusion_list_display`)
- **AND** there are no duplicate underscore-prefixed aliases in `app.py` for the same symbols

#### Scenario: Tests remain valid after removal of compat aliases
- **GIVEN** the test suite for exclusion filters
- **WHEN** tests run after removing backwards-compat re-exports from app.py
- **THEN** all exclusion filter tests pass
- **AND** tests import from `exclusion_filters` (or app only for MCP tool behavior), not from app for exclusion helpers
