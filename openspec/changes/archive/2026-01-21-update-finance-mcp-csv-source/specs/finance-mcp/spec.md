## ADDED Requirements
### Requirement: CSV Folder Source
The system SHALL load Outbank CSV exports from a configured local folder for MCP queries.

#### Scenario: Load multiple CSV files
- **WHEN** the configured folder contains multiple Outbank CSV files
- **THEN** the service loads and aggregates transactions from all files

### Requirement: Outbank CSV Parsing
The system SHALL parse semicolon-delimited Outbank CSVs with German date formatting and decimal comma amounts.

#### Scenario: Parse a sample row
- **WHEN** a CSV row contains a booking date like `18.01.2026` and an amount like `-13,11`
- **THEN** the service parses the date and amount into normalized values

### Requirement: In-Memory Normalization
The system SHALL normalize parsed CSV rows into an in-memory JSON representation used for search and filtering.

#### Scenario: Query uses normalized data
- **WHEN** a search query is executed
- **THEN** the results are derived from the normalized in-memory transaction list

### Requirement: CSV Reload Tool
The system SHALL expose an MCP tool to reload transactions from the configured CSV folder without restarting the service.

#### Scenario: Reload after new export
- **WHEN** the user exports a new CSV into the folder and calls the reload tool
- **THEN** subsequent queries include transactions from the new CSV

### Requirement: Reload Statistics
The system SHALL return reload statistics including total record count and record deltas.

#### Scenario: Reload returns counts
- **WHEN** the reload tool completes
- **THEN** the response includes total records, new records, and removed records

### Requirement: Python Setup With UV
The system SHALL document a Python-first setup using `uv` for installing dependencies and running the MCP service.

#### Scenario: Install and run with uv
- **WHEN** the user follows the documented `uv` commands
- **THEN** the MCP service starts successfully without Docker

### Requirement: No NocoDB Dependency
The system SHALL run without requiring NocoDB, Postgres, or Docker to answer MCP queries.

#### Scenario: Run MCP service without Docker
- **WHEN** the MCP service starts with only CSV files available
- **THEN** queries are answered without external database services
