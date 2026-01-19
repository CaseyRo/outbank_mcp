# Change: Add optional MCP security guidance

## Why
The MCP service can run in both HTTP and stdio modes, which makes it easy to
accidentally expose sensitive finance data if a port is bound broadly or if
local tooling runs without guardrails. Providing an optional, documented
security strategy keeps the default local-first experience simple while giving
users a clear, supported path to lock down access when needed.

## What Changes
- Add optional, token-based authentication for MCP requests over HTTP
  (opt-in, backwards-compatible)
- Define environment configuration for enabling/disabling HTTP auth
- Add `docs/security.md` with recommended local-only and HTTP token setups
- Link the security guide from the README and MCP service docs, and add a clear
  warning that exposing the MCP service publicly is out of scope and at the
  user's risk
- Update `.env.example` to document security-related configuration

## Impact
- Affected specs: finance-mcp
- Affected code: MCP service runtime, Docker Compose, `.env.example`, docs
