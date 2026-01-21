Feature: Invalid Input Handling
  As a user
  I want to receive clear error messages for invalid inputs
  So that I can correct my queries

  Scenario: Invalid date range (start after end)
    Given the MCP server is running
    And CSV data is loaded
    When I search with date range from "2024-12-31" to "2024-01-01"
    Then I should receive an error message
    And the error should indicate invalid date range

  Scenario: Invalid amount range (min greater than max)
    Given the MCP server is running
    And CSV data is loaded
    When I search with amount range from "100" to "-100"
    Then I should receive an error message
    And the error should indicate invalid amount range

  Scenario: Invalid date format
    Given the MCP server is running
    And CSV data is loaded
    When I search with date "invalid-date"
    Then I should receive an error message
    And the error should indicate invalid date format

  Scenario: Conflicting date filters
    Given the MCP server is running
    And CSV data is loaded
    When I search with both date "2024-01-15" and date range from "2024-01-01" to "2024-01-31"
    Then I should receive an error message
    And the error should indicate conflicting filters
