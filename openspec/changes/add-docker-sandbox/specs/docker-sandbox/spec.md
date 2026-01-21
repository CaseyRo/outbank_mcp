## ADDED Requirements
### Requirement: Docker Container for Finance MCP Service
The system SHALL provide a Docker container that packages the Python finance MCP service with all dependencies, ready to run in an isolated environment.

#### Scenario: Container builds successfully
- **WHEN** `docker-compose build finance-mcp` is executed
- **THEN** the container image is created with Python dependencies installed

#### Scenario: Container starts service
- **WHEN** the container is started via docker-compose
- **THEN** the MCP service is available and ready to handle requests

### Requirement: CSV Directory Volume Mount
The system SHALL mount the Outbank CSV directory as a Docker volume, allowing CSV files to be read from the host filesystem without rebuilding the container.

#### Scenario: CSV files accessible in container
- **WHEN** CSV files exist in the configured host directory
- **THEN** the MCP service can read and process those files from within the container

#### Scenario: CSV directory update without rebuild
- **WHEN** new CSV files are added to the mounted directory on the host
- **THEN** the service can access them after calling reload_transactions without container rebuild

### Requirement: Single Source of Truth for Port Configuration
The system SHALL configure the MCP service port only in docker-compose.yml port mapping, eliminating duplication with application code.

#### Scenario: Port configured in docker-compose
- **WHEN** a port is specified in docker-compose.yml port mapping (e.g., "6668:6668")
- **THEN** the MCP service uses the container-internal port from the environment variable, without hardcoding

#### Scenario: Port change in docker-compose
- **WHEN** the port mapping in docker-compose.yml is changed (e.g., "7777:6668")
- **THEN** no changes to Dockerfile or app.py are required

### Requirement: Organized Environment Configuration
The system SHALL provide a clearly organized .env.example file with logical sections for Docker settings, MCP configuration, CSV source, and optional authentication.

#### Scenario: Environment file sections
- **WHEN** a user opens .env.example
- **THEN** they see clearly labeled sections: Docker ports, MCP transport settings, CSV source configuration, and optional HTTP auth

#### Scenario: All docker-compose variables documented
- **WHEN** docker-compose.yml references an environment variable
- **THEN** that variable is documented in .env.example with a description and default value

### Requirement: Stdio Transport in Docker
The system SHALL support stdio MCP transport when running in a Docker container, using stdin/stdout for communication.

#### Scenario: Stdio transport works in container
- **WHEN** MCP_TRANSPORT=stdio and the container runs with stdin/stdout attached
- **THEN** the MCP service communicates correctly via stdio

#### Scenario: Stdio remains default
- **WHEN** no MCP_TRANSPORT is specified
- **THEN** the service defaults to stdio transport
