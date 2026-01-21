Feature: Monthly Expense Analysis
  As a user
  I want to analyze my monthly expenses
  So that I can understand my spending patterns

  Scenario: Analyze expenses for January 2024
    Given the MCP server is running
    And CSV data is loaded
    When I search for transactions from "2024-01-01" to "2024-01-31"
    And I calculate expense totals
    Then I should see expense summary with transaction count
    And I should see total expenses amount
    And I should see top expense categories

  Scenario Outline: Analyze expenses for different months
    Given the MCP server is running
    And CSV data is loaded
    When I search for transactions from "<start_date>" to "<end_date>"
    Then I should see expense summary with transaction count

    Examples:
      | start_date   | end_date     |
      | 2024-01-01   | 2024-01-31   |
      | 2024-02-01   | 2024-02-29   |
      | 2024-12-01   | 2024-12-31   |
