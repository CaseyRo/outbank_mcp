## Context
The finance MCP service currently assumes a trusted local environment. Since
the server can run over HTTP (bound to a host/port), we need a minimal, opt-in
security strategy that keeps existing users unblocked while protecting
deployments that expose a port.

## Goals / Non-Goals
- Goals: optional auth for HTTP, explicit configuration via env vars, clear
  documentation for secure local setups
- Non-Goals: multi-user auth, OAuth, external identity providers, encrypted
  storage, or remote hosting support

## Decisions
- Use a single shared token for HTTP authentication so configuration stays
  simple and portable for local-only users.
- Gate auth behind configuration (default disabled) to preserve backward
  compatibility.
- Support auth on HTTP transport only; stdio remains unchanged.
- HTTP clients pass a bearer token header using a single shared token.

## Risks / Trade-offs
- Token-based auth is static and does not provide per-user auditing.
  Mitigation: keep scope to local deployments and document limitations.

## Migration Plan
- Add new env vars with safe defaults (disabled)
- Implement auth checks for HTTP transport
- Document secure setups and update README links

## Open Questions
- Do we need to support per-user tokens in a future iteration, or is a shared
  token sufficient for local-only use?
