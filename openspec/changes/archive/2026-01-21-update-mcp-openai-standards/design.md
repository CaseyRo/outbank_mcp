## Context
The finance MCP service currently exposes tools over HTTP and documents optional shared-token auth. The request is to align tool presentation with OpenAI MCP standards, support stdio alongside HTTP, and update docs for a non-Docker workflow and security guidance.

## Goals / Non-Goals
- Goals:
  - Provide stdio and HTTP transports for MCP.
  - Ensure HTTP supports bearer-token auth with clear configuration.
  - Present tools with metadata aligned to OpenAI MCP expectations (names, descriptions, input schema, examples if required).
  - Update docs for security and non-Docker run instructions.
- Non-Goals:
  - Multi-user auth, token rotation services, or hosted deployment guidance.
  - Changing the core CSV parsing or query behavior.

## Decisions
- Implement a dual-transport startup that enables stdio by default and HTTP via config, or supports both concurrently if supported by the MCP framework.
- Encode OpenAI MCP tool presentation requirements in docs and in tool metadata where the framework supports it.
- Keep auth limited to a single shared bearer token for HTTP; stdio remains local-only.

## Alternatives considered
- HTTP-only with a separate stdio wrapper: rejected to avoid separate runtime paths.
- Full OAuth/API key management: rejected due to scope and local-only focus.

## Risks / Trade-offs
- Supporting two transports may introduce configuration complexity; mitigate with clear env var defaults and documentation.
- OpenAI MCP standard details may evolve; mitigate by linking docs to official references and noting version/date in docs.

## Migration Plan
- Add configuration for stdio/HTTP transport selection.
- Update tool metadata and expose required fields.
- Update docs for running, security, and OpenAI MCP approval readiness.

## Open Questions
- None. Align to MCP spec version 2025-11-25 and document approval readiness as a checklist based on that spec.
