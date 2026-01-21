## ADDED Requirements

### Requirement: Transaction Exclusion Filters
The system SHALL support configurable exclusion of transactions based on category or tag values via environment variables.

#### Scenario: Exclude transactions by category
- **WHEN** `EXCLUDED_CATEGORIES` is set to a comma-separated list (e.g., "Transfer,Internal")
- **AND** transactions are loaded from CSV files
- **THEN** transactions matching any excluded category are not added to the transaction store
- **AND** excluded transactions never appear in search results

#### Scenario: Exclude transactions by tag
- **WHEN** `EXCLUDED_TAGS` is set to a comma-separated list (e.g., "transfer,internal")
- **AND** transactions are loaded from CSV files
- **THEN** transactions with tags matching any excluded tag are not added to the transaction store
- **AND** excluded transactions never appear in search results

#### Scenario: Case-insensitive exclusion matching
- **WHEN** exclusion filters are configured (e.g., `EXCLUDED_CATEGORIES=transfer`)
- **AND** a transaction has category "Transfer" (different case)
- **THEN** the transaction is excluded regardless of case differences

#### Scenario: Partial match exclusion
- **WHEN** exclusion filters are configured (e.g., `EXCLUDED_TAGS=transfer`)
- **AND** a transaction has tag "internal-transfer"
- **THEN** the transaction is excluded if the exclusion value appears anywhere in the tag

#### Scenario: Multiple exclusion values
- **WHEN** `EXCLUDED_CATEGORIES` contains multiple comma-separated values (e.g., "Transfer,Internal,Reconciliation")
- **AND** transactions are loaded
- **THEN** transactions matching any of the excluded categories are filtered out

#### Scenario: Empty exclusion lists
- **WHEN** exclusion environment variables are not set or set to empty strings
- **THEN** no transactions are excluded
- **AND** all transactions from CSV files are loaded normally

#### Scenario: Exclusion applies at load time
- **WHEN** exclusion filters are configured
- **AND** CSV files are reloaded via `reload_transactions` tool
- **THEN** excluded transactions are filtered during the reload operation
- **AND** excluded transactions do not appear in subsequent search results
