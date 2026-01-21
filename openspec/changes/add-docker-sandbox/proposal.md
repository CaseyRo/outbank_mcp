# Change: Add Docker Sandbox for Finance MCP Service

## Why
The current setup requires manual dependency installation and doesn't provide a consistent, isolated runtime environment. Adding Docker containerization will:
- Sandbox the Python service for consistent behavior across environments
- Simplify deployment by packaging dependencies
- Enable CSV data access via volume mounts for better data management
- Centralize port configuration in docker-compose to avoid duplication

## What Changes
- Add optimized Dockerfile that builds the Python service with dependencies
- Update docker-compose.yml to mount CSV directory as a volume
- Simplify port configuration: remove port duplication, only configure in docker-compose port mapping
- Organize .env.example with clear sections for Docker and service configuration
- Ensure stdio transport remains the default for MCP communication
- Verify stdio transport works correctly in Docker environment

## Impact
- Affected specs: New `docker-sandbox` capability
- Affected code:
  - `Dockerfile` (optimize build process)
  - `docker-compose.yml` (add volume mount, simplify port config)
  - `.env.example` (reorganize for clarity)
  - `app.py` (no changes needed, but verify stdio compatibility)
