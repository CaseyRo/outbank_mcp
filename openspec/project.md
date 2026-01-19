# Project Context

## Purpose
Provide a trustworthy, local-first finance data workspace using NocoDB + Docker, starting with Outbank CSV imports and evolving toward automated refreshes and rich visual insights.

## Tech Stack
- Docker Compose for local orchestration
- NocoDB as the data hub and UI
- Postgres (default) or SQLite for storage (prefer Postgres for multi-user and backup)
- Optional visualization layer (Metabase or Apache Superset) for dashboards

## Project Conventions

### Code Style
- Favor declarative Docker Compose configs with clear service names
- Use kebab-case for container and volume names
- Keep README-like docs short and task-oriented

### Architecture Patterns
- Local-first: all data stays on the user's machine
- CSV ingestion: import Outbank CSVs into a normalized "transactions" table
- Idempotent updates: re-importing the same CSV should not create duplicates
- Views-first UX: expose NocoDB views and charts as primary interaction surfaces

### Testing Strategy
- Manual verification: import CSV, validate row counts, and check de-duplication
- Spot-check metrics: account totals and monthly rollups

### Git Workflow
- Small, focused commits per feature or doc update
- Keep Docker and data schema changes in separate commits when possible

## Domain Context
- Outbank CSVs include account, booking date, value date, amount, currency, and purpose fields
- Primary entity is a transaction; accounts act as a dimension for grouping
- Regular updates will append new transactions, not rewrite history

## Important Constraints
- Privacy-first: no external uploads or hosted services unless explicitly approved
- Must work with local Docker only
- Avoid vendor lock-in; keep data exportable as CSV/SQL

## External Dependencies
- NocoDB Docker image
- Postgres Docker image (or SQLite volume if chosen)
- Optional: Metabase/Superset for graphs and dashboards
