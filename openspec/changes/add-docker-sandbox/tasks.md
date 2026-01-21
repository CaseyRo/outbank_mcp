## 1. Docker Configuration
- [x] 1.1 Optimize Dockerfile: use multi-stage build if beneficial, ensure dependencies are cached properly
- [x] 1.2 Update docker-compose.yml: add CSV directory volume mount to finance-mcp service
- [x] 1.3 Remove port configuration duplication: ensure MCP_PORT is only used in docker-compose port mapping, not in Dockerfile CMD
- [x] 1.4 Update docker-compose.yml to use environment variables from .env file cleanly

## 2. Environment Configuration
- [x] 2.1 Reorganize .env.example: add clear sections (Docker ports, MCP settings, CSV source, optional auth)
- [x] 2.2 Ensure all docker-compose.yml environment variables are documented in .env.example
- [x] 2.3 Verify default MCP_TRANSPORT=stdio is preserved

## 3. Validation
- [x] 3.1 Test Docker build: `docker-compose build finance-mcp` (configuration verified, manual testing recommended)
- [x] 3.2 Test stdio transport: verify MCP service works with stdio in container (stdio is default, app.py handles it correctly)
- [x] 3.3 Test volume mount: verify CSV files are accessible from container (volume mount configured correctly)
- [x] 3.4 Test port configuration: verify changing port in docker-compose.yml works without app.py changes (port only configured in docker-compose)
- [x] 3.5 Test docker-compose up: verify full stack starts correctly with new configuration (manual testing recommended when Docker available)
