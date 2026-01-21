# Change: Add local NocoDB finance stack with Postgres and Metabase

## Why
Managing transactions in Google Sheets is slow and tedious. A local, trusted stack with NocoDB plus charts will streamline imports and analysis while keeping data private.

## What Changes
- Add a Docker Compose stack for NocoDB + Postgres + Metabase
- Define an Outbank CSV ingestion schema and mapping
- Establish idempotent import rules to avoid duplicates
- Provide baseline dashboards for spending analysis

## Impact
- Affected specs: finance-workspace
- Affected code: new Docker and schema docs/config
