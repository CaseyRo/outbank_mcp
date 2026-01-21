## ADDED Requirements
### Requirement: OpenAI MCP Approval Guidance
The documentation SHALL include a concise checklist describing OpenAI MCP tool presentation requirements and approval readiness criteria.

#### Scenario: Reader verifies approval readiness
- **WHEN** a reader follows the checklist
- **THEN** they can confirm tool naming, descriptions, and schemas meet the standard

### Requirement: Dual Transport Run Instructions
The documentation SHALL explain how to run the MCP service over stdio and HTTP without Docker.

#### Scenario: Reader starts stdio mode
- **WHEN** a reader follows the stdio instructions
- **THEN** the service runs using stdio transport locally

#### Scenario: Reader starts HTTP mode with auth
- **WHEN** a reader follows the HTTP instructions and sets an auth token
- **THEN** the service requires a bearer token for HTTP calls

### Requirement: Updated Security Notes
The documentation SHALL describe local-only expectations and the limits of shared-token HTTP auth.

#### Scenario: Reader reviews security guidance
- **WHEN** a reader reads the security section
- **THEN** they understand the risks of exposing the service publicly and the scope of the auth model
