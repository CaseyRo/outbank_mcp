## 1. Discovery and alignment
- [ ] 1.1 Review OpenAI MCP tooling standards and approval criteria
- [ ] 1.2 Map required tool metadata fields to FastMCP capabilities

## 2. Service changes
- [ ] 2.1 Add stdio transport support (configurable)
- [ ] 2.2 Ensure HTTP transport supports bearer-token auth
- [ ] 2.3 Update tool metadata (names, descriptions, schemas) for approval readiness

## 3. Documentation
- [ ] 3.1 Update `docs/mcp.md` with tool presentation guidance and dual-transport usage
- [ ] 3.2 Update `docs/security.md` for HTTP auth and local-only guidance
- [ ] 3.3 Update `README.md` for non-Docker run flow and transport options

## 4. Validation
- [ ] 4.1 Run MCP test scripts for stdio and HTTP modes
- [ ] 4.2 Document any manual verification steps
