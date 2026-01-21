## Context
The finance MCP service currently runs directly via `uv run python app.py` with manual dependency installation. Users want a more sandboxed, containerized setup that:
- Provides isolation and consistency
- Makes CSV data accessible via volume mounts
- Simplifies port configuration (no duplication)
- Maintains stdio transport as default (which should work in Docker via stdin/stdout)

## Goals / Non-Goals
- Goals:
  - Docker container that packages Python service and dependencies
  - CSV directory mounted as volume for easy data access
  - Single source of truth for port configuration (docker-compose)
  - Clean .env.example organization
  - Stdio transport continues to work (via docker-compose stdin/stdout)
- Non-Goals:
  - Multi-stage builds unless they provide clear benefits
  - Production-grade optimizations beyond basic sandboxing
  - Changing the core MCP service logic

## Decisions
- Decision: Use volume mount for CSV directory
  - Rationale: Allows users to update CSV files without rebuilding container, follows Docker best practices
  - Alternative considered: Copying CSV into image - rejected because it requires rebuilds for data updates

- Decision: Configure port only in docker-compose port mapping
  - Rationale: Eliminates duplication, Docker port mapping is the authoritative source
  - Implementation: Remove hardcoded port from Dockerfile CMD, use MCP_PORT env var from docker-compose

- Decision: Keep stdio as default transport
  - Rationale: Stdio works in Docker when container runs in interactive/attached mode or via docker-compose stdin/stdout
  - Note: HTTP transport remains available for users who prefer it

- Decision: Organize .env.example into logical sections
  - Rationale: Improves readability and makes it clear which settings are for Docker vs the service
  - Sections: Docker ports, MCP transport, CSV source, optional HTTP auth

## Risks / Trade-offs
- Stdio in Docker: Works but requires proper stdin/stdout handling in docker-compose. Risk: low - FastMCP handles this correctly.
- Volume mount path: Users need to provide correct host path. Mitigation: document in .env.example and README.
- Build time: No significant impact - Python slim image and uv are efficient.

## Migration Plan
1. Update Dockerfile and docker-compose.yml
2. Reorganize .env.example
3. Test both stdio and HTTP transports
4. Update README if needed for Docker usage instructions
5. No breaking changes for users running without Docker

## Open Questions
- None - straightforward containerization improvement
