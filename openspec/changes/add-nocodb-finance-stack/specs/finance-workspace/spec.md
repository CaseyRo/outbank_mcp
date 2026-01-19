## ADDED Requirements
### Requirement: Local Docker Stack
The system SHALL provide a Docker Compose stack with NocoDB, Postgres, and Metabase services for local use.

#### Scenario: Bring up stack
- **WHEN** the user runs the provided Docker Compose command
- **THEN** NocoDB, Postgres, and Metabase are reachable on local ports

### Requirement: Outbank CSV Ingestion
The system SHALL support importing Outbank CSV files using semicolon delimiters and German date formats.

#### Scenario: Import sample CSV
- **WHEN** the user imports an Outbank CSV with columns Account, Date, Value Date, Amount, Currency, Name, Number, Bank, Reason, Category, Subcategory, Category-Path, Tags, Note, Posting Text
- **THEN** transactions are stored with parsed dates and amounts and the raw strings are preserved

### Requirement: Idempotent Updates
The system SHALL prevent duplicate transactions when the same CSV file is imported more than once.

#### Scenario: Re-import same file
- **WHEN** the user imports the same CSV file again
- **THEN** the system does not create duplicate rows for existing transactions

### Requirement: Privacy-First Operation
The system SHALL operate locally without requiring outbound network access after images are pulled.

#### Scenario: Local-only usage
- **WHEN** the stack is running
- **THEN** user data remains on the local machine and no external services are required

### Requirement: Baseline Dashboards
The system SHALL provide baseline dashboards for spend by month, category, and account using Metabase.

#### Scenario: View dashboards
- **WHEN** the user opens Metabase and connects it to the Postgres database
- **THEN** preconfigured questions or dashboards can be used as starting points
