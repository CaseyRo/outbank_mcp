## 1. Remove orphaned database artifacts
- [x] 1.1 Confirm no code or scripts reference `db/` or `schema.sql`
- [x] 1.2 Remove `db/` directory (or move `db/schema.sql` to `docs/archive/` / openspec archive if we want to keep for reference)
- [x] 1.3 Update `.gitignore` or docs if they mention `db/`

## 2. Consolidate opsx commands and skills
- [x] 2.1 Choose single source of truth (e.g. `.cursor/` or `.claude/` or a shared `opsx/` at repo root)
- [x] 2.2 Keep one set of command and skill files; add symlinks or a small script to sync to the other IDE’s paths, OR document "copy from X" in README/CLAUDE/AGENTS
- [x] 2.3 Remove the duplicate tree(s) or replace with symlinks so only one copy is edited
- [x] 2.4 Update any docs that reference `.claude/` or `.cursor/` paths

## 3. Remove dead re-exports in app.py
- [x] 3.1 Remove the "Re-export for backwards compatibility" block (lines 28–32) that aliases `_env_exclusion_list`, `_env_exclusion_list_display`, `_matches_exclusion`, `_should_exclude_transaction`
- [x] 3.2 Ensure all usages in app.py use the names imported from `exclusion_filters` (e.g. `should_exclude_transaction`, `env_exclusion_list_display`) with no local underscore aliases
- [x] 3.3 Run tests to confirm exclusion behavior unchanged

## 4. Documentation and verification
- [x] 4.1 Update README or docs if they referenced `db/` or the old dual-IDE layout
- [x] 4.2 Run full test suite and manual smoke check (load CSV, search, reload)
