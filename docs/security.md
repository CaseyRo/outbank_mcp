# Security Guide

This project is designed for local-only use. Exposing the MCP service to the
public internet is out of scope for this repository and entirely at your own
risk. If you publish this service, you are responsible for hardening,
monitoring, and access control.

## Recommended local-only setup
- Keep Docker ports bound to localhost.
- Use a firewall or VPN if you must access the service remotely.

Example Docker Compose port binding:
```yaml
ports:
  - "127.0.0.1:6668:6668"
```

## Optional HTTP token auth
The MCP service can enforce a single shared token for HTTP requests.

### Configuration
Set these in `.env` (or Docker Compose environment):
- `MCP_HTTP_AUTH_ENABLED=true`
- `MCP_HTTP_AUTH_TOKEN=your-secret-token`

If `MCP_HTTP_AUTH_ENABLED` is not set, the server will enable auth automatically
when `MCP_HTTP_AUTH_TOKEN` is set.

### Client usage
Include a bearer token header:
```bash
curl -sS -X POST "http://localhost:6668/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-token" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### Notes and limitations
- This is a single shared token for HTTP only.
- There is no per-user token management or audit trail.
