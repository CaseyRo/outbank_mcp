# Baseline Metabase Questions

## Connect Metabase
Add a new database connection to the Postgres service:
- Host: `postgres`
- Port: `5432`
- Database: `finance`
- Username: `finance`
- Password: `finance`

## Suggested questions

### Spend by month
```sql
SELECT
  date_trunc('month', booking_date) AS month,
  sum(amount) AS total_amount
FROM transactions
WHERE amount < 0
GROUP BY 1
ORDER BY 1;
```

### Spend by category
```sql
SELECT
  coalesce(category, 'Uncategorized') AS category,
  sum(amount) AS total_amount
FROM transactions
WHERE amount < 0
GROUP BY 1
ORDER BY total_amount;
```

### Spend by account
```sql
SELECT
  a.name AS account,
  sum(t.amount) AS total_amount
FROM transactions t
LEFT JOIN accounts a ON a.id = t.account_id
WHERE t.amount < 0
GROUP BY 1
ORDER BY total_amount;
```
