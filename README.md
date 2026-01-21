# Outbank MCP CSV Workspace

Local-first MCP query service that reads Outbank CSV exports from a folder,
normalizes transactions in memory, and exposes read-only search tools.
Supports both Docker containerized setup and direct Python execution.

## Purpose and responsibility
This project exists solely to supply LLMs with your finance data using exports
from the popular Outbank tool. You are responsible for how your data is
handled, exported, stored, and shared. Prefer local models over big-tech hosted
LLMs whenever possible. If you do use an external model, using an MCP to query
your local data is safer than uploading raw CSV exports repeatedly.

> ⚠️ 🔒 🚫 **Local-only warning**  
> This project is intended for local-only use.  
> Exposing the MCP service publicly is out of scope and entirely at your own risk.  
> See `docs/security.md` for recommended local-only setup and mandatory HTTP auth requirements.

> 🚨 **Security: Impersonation Warning**  
> **NEVER share credentials or CSV files with anyone claiming to be a contributor or maintainer of this project.**  
> Contributors and maintainers of this project will **NEVER** ask you for:
> - Your credentials (passwords, API keys, tokens)
> - Your CSV export files
> - Access to your financial data
> 
> If someone asks for these, they are impersonating us. Report them and do not comply.

## What is here
- Python MCP service for CSV-folder ingestion and query tools
- Automated test suite for stdio and HTTP transport modes
  - Unit tests, error handling, and user workflow tests
  - BDD workflow tests using Gherkin feature files (pytest-bdd)
- Notes on Outbank CSV export format and normalization
- Example Outbank CSV export (`outbank_export_example.csv`)

## Quick start

Choose either Docker or direct Python execution:

### Option 1: Docker (Recommended for isolated environments)

1. Ensure Docker and Docker Compose are installed
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
3. Configure your CSV directory in `.env`:
   ```bash
   OUTBANK_CSV_DIR=./outbank_exports
   ```
4. Build and start the service:
   ```bash
   docker-compose up --build
   ```
   The service will be available via stdio (default) or HTTP on the configured port.

   To run in detached mode:
   ```bash
   docker-compose up -d
   ```

   To view logs:
   ```bash
   docker-compose logs -f finance-mcp
   ```

   To stop:
   ```bash
   docker-compose down
   ```

### Option 2: Direct Python execution

1. Install `uv`: https://github.com/astral-sh/uv
2. Copy the environment template and configure:
   ```bash
   cp .env.example .env
   ```
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Run the MCP service with stdio transport (default):
   ```bash
   uv run python app.py
   ```
   Or with HTTP transport (JSON-only responses, no SSE streaming, **auth required**):
   ```bash
   MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=6668 \
     MCP_HTTP_AUTH_TOKEN=your-secret-token \
     uv run python app.py
   ```
   **Note**: `MCP_HTTP_AUTH_TOKEN` is required when using HTTP transport (minimum 16 characters, 32+ recommended). The service will fail to start if the token is missing or too short. Generate a secure token with:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

## CSV format
Outbank exports use semicolon-delimited CSV with German date format and
decimal commas. Expected header example:
```csv
#;Account;Date;Value Date;Amount;Currency;Name;Number;Bank;Reason;Category;Subcategory;Category-Path;Tags;Note;Posting Text
```

## Configuration

### Transaction Exclusion Filters

You can exclude certain transactions from being loaded by configuring exclusion filters in your `.env` file. Excluded transactions are filtered during CSV ingestion and will never appear in search results.

**Environment Variables:**
- `EXCLUDED_CATEGORIES`: Comma-separated list of categories to exclude (e.g., `Transfer,Internal,Reconciliation`)
- `EXCLUDED_TAGS`: Comma-separated list of tags to exclude (e.g., `transfer,internal`)

**Features:**
- **Multi-field matching**: Category exclusions check the `category`, `subcategory`, and `category_path` fields. For example, `Transfer` will match transactions with subcategory "Transfer" even if the category is "Finances & Insurances"
- **Case-insensitive matching**: Exclusion filters match regardless of case (e.g., `transfer` matches `Transfer`, `TRANSFER`, etc.)
- **Partial matching**: Exclusion values match if they appear anywhere in the category/subcategory/path or tag (e.g., `transfer` matches `internal-transfer` or `Finances & Insurances / Transfer`)
- **Applied at load time**: Excluded transactions are filtered during CSV ingestion, not at query time
- **Whitespace handling**: Extra spaces around values are automatically trimmed

**Example `.env` configuration:**
```bash
# Exclude transfer transactions by category
EXCLUDED_CATEGORIES=Transfer,Internal

# Exclude transactions with specific tags
EXCLUDED_TAGS=transfer,internal
```

**Example use cases:**
- Exclude internal transfers between your own accounts
- Filter out reconciliation transactions
- Remove specific transaction types you don't want to analyze
- Clean up duplicate or noise transactions

**How it works:**
1. Configure exclusion filters in your `.env` file
2. When CSV files are loaded (on startup or via `reload_transactions`), transactions matching exclusion criteria are filtered out
3. Excluded transactions never enter the in-memory transaction store
4. Search results will not include excluded transactions

**Important notes:**
- Exclusion filters are applied when transactions are loaded or reloaded. After changing exclusion filters, use the `reload_transactions` tool to apply the new filters.
- If a transaction matches **any** excluded category **or** any excluded tag, it will be excluded
- Empty values or whitespace-only values in the exclusion list are ignored
- To disable exclusions, leave the environment variables unset or set them to empty strings

**Verifying exclusions:**
After configuring exclusion filters and reloading transactions, you can verify they're working:
1. Use `describe_fields` to see the total number of loaded records
2. Use `search_transactions` with a query that would normally match excluded transactions
3. Excluded transactions should not appear in results

## Docs
- MCP service details: `docs/mcp.md`
- Security guide: `docs/security.md`
- Outbank CSV import steps: `docs/outbank-import.md`

## Testing

Automated tests are available to validate MCP server functionality across both stdio and HTTP transport modes.

### Quick start

1. Install test dependencies:
   ```bash
   uv sync --group dev
   ```

2. Run all tests:
   ```bash
   uv run pytest tests/
   ```

3. For HTTP transport tests, start the server first with authentication:
   ```bash
   MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=6668 \
     MCP_HTTP_AUTH_TOKEN=test-token-12345678 \
     uv run python app.py
   ```

### Test Types

The test suite includes:

- **Unit tests**: Basic functionality tests (`test_simple_queries.py`, `test_advanced_queries.py`)
- **Error handling tests**: Edge cases and error conditions (`test_error_handling.py`)
- **User workflow tests**: End-to-end workflow simulation (`test_user_workflow.py`)
- **BDD workflow tests**: Behavior-Driven Development tests using Gherkin feature files (`tests/features/`, `tests/step_defs/`)

### BDD Workflow Tests

The project includes **Behavior-Driven Development (BDD)** tests using `pytest-bdd` and Gherkin feature files. These tests provide human-readable scenarios that serve as living documentation.

**Available BDD workflows:**
- Monthly expense analysis
- Account reconciliation
- Progressive search refinement
- Invalid input handling
- Data state management
- HTTP authentication

**Run BDD tests:**
```bash
# Run all BDD tests
uv run pytest tests/step_defs/ -v

# Run specific workflow
uv run pytest tests/step_defs/test_monthly_expense.py -v
```

**Example feature file:**
```gherkin
Feature: Monthly Expense Analysis
  Scenario: Analyze expenses for January 2024
    Given the MCP server is running
    And CSV data is loaded
    When I search for transactions from "2024-01-01" to "2024-01-31"
    Then I should see expense summary with transaction count
```

See `tests/README.md` for detailed test documentation including:
- Test structure and organization
- Running specific test suites (stdio vs HTTP)
- BDD workflow test details and examples
- Environment setup for authenticated HTTP tests
- Test coverage details
- OpenAI MCP compliance verification (`tests/MCP_COMPLIANCE.md`)

## Development

### Pre-commit hooks

This project uses [pre-commit](https://pre-commit.com/) to run code quality checks before each commit.

**Setup:**
```bash
uv sync --group dev
uv run pre-commit install
```

**What it checks:**
- Code formatting (ruff format)
- Linting (ruff check)
- Trailing whitespace, merge conflicts, large files
- YAML/JSON syntax validation

**Run manually:**
```bash
uv run pre-commit run --all-files
```

## Open source projects used here
- FastMCP: https://github.com/jlowin/fastmcp
- Python: https://www.python.org/
- uv: https://github.com/astral-sh/uv

## Outbank
- Product: https://outbankapp.com/
- Outbank team: https://outbankapp.com/ueber-outbank/
- Affiliate link (free month): https://outbankapp.com/affiliate-gratismonat/?id=outbank_mcp
  - Disclosure: this is an affiliate link.
