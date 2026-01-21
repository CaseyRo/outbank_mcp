Feature: HTTP Authentication
  As a user
  I want secure access to the MCP server
  So that my financial data is protected

  @http_only
  Scenario: Unauthorized access without token
    Given the HTTP server is running with auth enabled
    When I make a request without authentication token
    Then I should receive an unauthorized error
    And the error code should be 401 or 403

  @http_only
  Scenario: Invalid token is rejected
    Given the HTTP server is running with auth enabled
    When I make a request with invalid token "wrong-token"
    Then I should receive an unauthorized error

  @http_only
  Scenario: Valid token allows access
    Given the HTTP server is running with auth enabled
    When I make a request with valid token
    Then I should receive successful response
    And I should see available tools
