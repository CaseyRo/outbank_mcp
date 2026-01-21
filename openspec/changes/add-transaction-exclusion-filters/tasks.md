## 1. Environment Configuration
- [x] 1.1 Add `EXCLUDED_CATEGORIES` environment variable support (comma-separated list)
- [x] 1.2 Add `EXCLUDED_TAGS` environment variable support (comma-separated list)
- [x] 1.3 Update `.env.example` with documentation and example values for exclusion filters
- [x] 1.4 Add helper functions to parse comma-separated exclusion lists from environment

## 2. Transaction Filtering Logic
- [x] 2.1 Modify `_load_transactions()` to apply exclusion filters during CSV ingestion
- [x] 2.2 Create helper function to check if a transaction matches any excluded category
- [x] 2.3 Create helper function to check if a transaction matches any excluded tag
- [x] 2.4 Ensure exclusion matching is case-insensitive and supports partial matches
- [x] 2.5 Skip transactions that match exclusion criteria before adding to transaction store

## 3. Testing and Validation
- [x] 3.1 Add test cases verifying transactions with excluded categories are not loaded
- [x] 3.2 Add test cases verifying transactions with excluded tags are not loaded
- [x] 3.3 Add test cases verifying exclusion filters work case-insensitively
- [x] 3.4 Add test cases verifying partial matches work correctly
- [x] 3.5 Verify excluded transactions do not appear in search results
- [x] 3.6 Test with empty exclusion lists (no exclusions should occur)

## 4. Documentation
- [x] 4.1 Update README.md to document exclusion filter configuration
- [x] 4.2 Add examples showing how to exclude common transaction types (e.g., "transfer")
