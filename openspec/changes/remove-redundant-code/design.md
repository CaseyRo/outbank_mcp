# Design: Remove redundant code and artifacts

## Scope

1. **db/** – Orphaned. No references in code or pyproject. Safe to remove; optionally keep `schema.sql` in `docs/archive/` or an openspec archive if we want historical reference.
2. **.claude/ vs .cursor/** – Duplicate opsx commands and skills. Content is the same; only path/layout differs (Claude: `opsx/apply.md`, Cursor: `opsx-apply.md`).
3. **app.py re-exports** – Dead code. Remove the four alias lines; use `exclusion_filters` names directly in app.py.

## Consolidation strategy for commands/skills

- **Option A (recommended):** Pick one tree as canonical (e.g. `.cursor/`). Keep it as the single source. Add a note in README or CLAUDE.md: "Opsx commands live under `.cursor/commands/`; for Claude, copy or symlink from there into `.claude/commands/opsx/` if needed."
- **Option B:** Single root-level `opsx/` (e.g. `opsx/commands/`, `opsx/skills/`) and symlink `.cursor/commands` → `opsx/commands`, `.claude/commands/opsx` → `opsx/commands`, etc. One copy, both IDEs point to it.
- **Option C:** Script (e.g. `scripts/sync-opsx.sh`) that copies from one tree to the other on demand; document "Run after editing opsx commands."

Implementation should choose one option and document it in the repo.
