## Context
The MCP service currently supports optional HTTP authentication via `MCP_HTTP_AUTH_ENABLED` and `MCP_HTTP_AUTH_TOKEN`. This allows users to run HTTP transport without authentication, which creates a security risk if the service is exposed to untrusted networks. Making HTTP auth mandatory ensures that financial data is always protected when using HTTP transport.

## Goals / Non-Goals
- Goals:
  - Require authentication for all HTTP transport usage
  - Fail fast at startup if HTTP transport is used without a token configured
  - Maintain stdio transport without auth (local process spawning is inherently secure)
  - Provide clear error messages when token is missing
- Non-Goals:
  - Adding authentication to stdio transport
  - Changing the authentication mechanism (still bearer token)
  - Adding per-user tokens or token rotation
  - Supporting multiple authentication methods

## Decisions
- Decision: Make HTTP auth mandatory by requiring `MCP_HTTP_AUTH_TOKEN` when using HTTP transport
  - Rationale: HTTP transport exposes the service over a network, making it accessible to untrusted processes. Financial data requires protection.
- Decision: Remove `MCP_HTTP_AUTH_ENABLED` configuration option
  - Rationale: If auth is always required for HTTP, the enable/disable flag is unnecessary. The presence of `MCP_HTTP_AUTH_TOKEN` indicates auth is required.
- Decision: Validate token configuration at startup when HTTP transport is selected
  - Rationale: Fail fast with a clear error message rather than silently allowing unauthenticated requests.
- Decision: Keep stdio transport unchanged (no auth required)
  - Rationale: Stdio transport only works with local processes that can spawn the server, which is inherently secure.

## Alternatives Considered
- Option 1: Keep auth optional but default to enabled
  - Rejected: Still allows users to disable auth, creating security risk
- Option 2: Require auth for both HTTP and stdio
  - Rejected: Stdio is local process spawning, adding auth would be unnecessary complexity
- Option 3: Make HTTP transport require explicit opt-in with auth
  - Rejected: Similar to current proposal, but less clear error messaging

## Risks / Trade-offs
- Risk: Breaking change for existing HTTP deployments without auth
  - Mitigation: Clear error message at startup explaining the requirement, update documentation prominently
- Risk: Users may find it inconvenient to set a token for local HTTP usage
  - Mitigation: Stdio transport remains available without auth for local-only use cases
- Trade-off: Simpler configuration (one less env var) vs. explicit enable/disable control
  - Chosen: Simpler configuration with mandatory security

## Migration Plan
1. Update code to require `MCP_HTTP_AUTH_TOKEN` when `MCP_TRANSPORT=http`
2. Remove `MCP_HTTP_AUTH_ENABLED` logic
3. Update `.env.example` to show token as required for HTTP
4. Update documentation to reflect mandatory auth
5. Update tests to always use auth tokens for HTTP transport
6. Add startup validation that fails with clear error if HTTP transport is used without token

## Open Questions
- None
