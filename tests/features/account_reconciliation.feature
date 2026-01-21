Feature: Account Reconciliation
  As a user
  I want to reconcile transactions for a specific account
  So that I can verify account accuracy

  Scenario: Reconcile checking account for date range
    Given the MCP server is running
    And CSV data is loaded
    When I describe the CSV fields
    And I reload transactions
    When I search for account "checking" from "2024-01-01" to "2024-12-31"
    Then I should see transactions for account "checking"
    And I should see transaction count greater than 0
    And I should verify all transactions match the account filter
