Feature: Data State Management
  As a user
  I want consistent data state across operations
  So that my queries return reliable results

  Scenario: Search before reload auto-loads data
    Given the MCP server is running
    And no data is loaded
    When I search for transactions
    Then data should be automatically loaded
    And I should receive search results

  Scenario: Multiple reloads maintain consistency
    Given the MCP server is running
    When I reload transactions
    Then I should see total records
    When I reload transactions again
    Then I should see same total records
    And new records count should be 0
    And removed records count should be 0

  Scenario: Data consistency across searches
    Given the MCP server is running
    And CSV data is loaded
    When I search with query "payment"
    Then I should see results count
    When I search with query "payment" again
    Then I should see same results count
    And results should be identical
