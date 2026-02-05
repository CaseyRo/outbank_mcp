# Change: Remove redundant code and artifacts after functionality reduction

## Why
The project was simplified to a local-first, in-memory CSV MCP service with no database. Some artifacts and code remain from the previous scope (e.g. database schema, duplicate IDE command trees, dead backwards-compatibility aliases). Removing them reduces maintenance, avoids confusion, and keeps the repo aligned with current functionality.

## What Changes

### 1. Remove orphaned database artifacts
- **`db/schema.sql`** – PostgreSQL schema for accounts and transactions. The project explicitly uses in-memory CSV processing and "no database required for core functionality" (openspec/project.md). No code or pyproject references this schema; it is a leftover from the pre–CSV simplification (archived NocoDB/Postgres stack). Remove `db/` or move `schema.sql` to archive/docs if we want to preserve it for reference.

### 2. Consolidate duplicate opsx command and skill trees
- **`.claude/commands/opsx/`** and **`.cursor/commands/`** – Same opsx commands in two layouts (Claude: `opsx/apply.md`; Cursor: `opsx-apply.md`). Content is effectively identical.
- **`.claude/skills/`** and **`.cursor/skills/`** – Same openspec skills duplicated.
- Maintain a single source of truth (e.g. one tree or one canonical format) and either symlink, script-copy, or document "copy from X" for the other IDE so we don’t maintain two copies.

### 3. Remove dead backwards-compatibility re-exports in app.py
- **app.py** (lines 28–32) re-exports `env_exclusion_list`, `env_exclusion_list_display`, `matches_exclusion`, `should_exclude_transaction` as `_env_exclusion_list`, etc. "Re-export for backwards compatibility." No consumer imports these from `app`; tests and app logic use `exclusion_filters` directly or the real names. Remove the compat aliases and use the `exclusion_filters` names directly in app.py.

## Impact
- **Affected specs:** finance-mcp (code hygiene), documentation (repo layout)
- **Affected paths:** `db/`, `.claude/`, `.cursor/`, `app.py`
- **Operational impact:** None for runtime behavior. IDE users may need to use the consolidated command/skill location or follow updated docs.
