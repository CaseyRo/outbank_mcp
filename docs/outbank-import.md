# Outbank CSV Import

Outbank exports use semicolon delimiters and German date formats (`DD.MM.YYYY`).

## Column mapping
| Outbank column | Target column |
| --- | --- |
| Account | raw_account |
| Date | raw_date |
| Value Date | raw_value_date |
| Amount | raw_amount |
| Currency | raw_currency |
| Name | raw_name |
| Number | raw_number |
| Bank | raw_bank |
| Reason | raw_reason |
| Category | raw_category |
| Subcategory | raw_subcategory |
| Category-Path | raw_category_path |
| Tags | raw_tags |
| Note | raw_note |
| Posting Text | raw_posting_text |

## Import steps
1. Import the CSV into NocoDB as the `transactions` table.
2. Map the CSV columns to the `raw_*` columns above.
3. Run the SQL below to populate typed columns and accounts.

## Post-import normalization
```sql
INSERT INTO accounts (name, bank, number, currency)
SELECT DISTINCT raw_account, raw_bank, raw_number, raw_currency
FROM transactions
WHERE raw_account IS NOT NULL
ON CONFLICT DO NOTHING;

UPDATE transactions t
SET
  account_id = a.id,
  booking_date = to_date(t.raw_date, 'DD.MM.YYYY'),
  value_date = CASE
    WHEN nullif(t.raw_value_date, '') IS NULL THEN NULL
    ELSE to_date(t.raw_value_date, 'DD.MM.YYYY')
  END,
  amount = replace(replace(t.raw_amount, '.', ''), ',', '.')::numeric,
  currency = t.raw_currency,
  counterparty_name = t.raw_name,
  counterparty_account = t.raw_number,
  counterparty_bank = t.raw_bank,
  reason = t.raw_reason,
  category = t.raw_category,
  subcategory = t.raw_subcategory,
  category_path = t.raw_category_path,
  tags = t.raw_tags,
  note = t.raw_note,
  posting_text = t.raw_posting_text
FROM accounts a
WHERE a.name = t.raw_account
  AND a.bank IS NOT DISTINCT FROM t.raw_bank
  AND a.number IS NOT DISTINCT FROM t.raw_number
  AND a.currency IS NOT DISTINCT FROM t.raw_currency;
```

## Idempotency
`transactions.dedupe_key` is a generated column based on all raw fields. The unique index prevents duplicate imports of the same CSV rows.
