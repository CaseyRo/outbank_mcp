Feature: Progressive Search Refinement
  As a user
  I want to progressively narrow down search results
  So that I can find specific transactions efficiently

  Scenario: Narrow down search with multiple filters
    Given the MCP server is running
    And CSV data is loaded
    When I search with query "payment"
    Then I should see initial results
    When I add date filter from "2024-01-01" to "2024-12-31"
    Then I should see fewer results than initial
    When I add amount filter from "-1000" to "-100"
    Then I should see fewer results than previous step
    And all results should match all applied filters
