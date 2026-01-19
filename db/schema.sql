CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  bank TEXT,
  number TEXT,
  currency TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (name, bank, number, currency)
);

CREATE TABLE IF NOT EXISTS transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES accounts(id),
  booking_date DATE,
  value_date DATE,
  amount NUMERIC(12, 2),
  currency TEXT,
  counterparty_name TEXT,
  counterparty_account TEXT,
  counterparty_bank TEXT,
  reason TEXT,
  category TEXT,
  subcategory TEXT,
  category_path TEXT,
  tags TEXT,
  note TEXT,
  posting_text TEXT,
  raw_account TEXT NOT NULL,
  raw_date TEXT NOT NULL,
  raw_value_date TEXT,
  raw_amount TEXT NOT NULL,
  raw_currency TEXT NOT NULL,
  raw_name TEXT,
  raw_number TEXT,
  raw_bank TEXT,
  raw_reason TEXT,
  raw_category TEXT,
  raw_subcategory TEXT,
  raw_category_path TEXT,
  raw_tags TEXT,
  raw_note TEXT,
  raw_posting_text TEXT,
  dedupe_key TEXT GENERATED ALWAYS AS (
    md5(
      coalesce(raw_account, '') || '|' ||
      coalesce(raw_date, '') || '|' ||
      coalesce(raw_value_date, '') || '|' ||
      coalesce(raw_amount, '') || '|' ||
      coalesce(raw_currency, '') || '|' ||
      coalesce(raw_name, '') || '|' ||
      coalesce(raw_number, '') || '|' ||
      coalesce(raw_bank, '') || '|' ||
      coalesce(raw_reason, '') || '|' ||
      coalesce(raw_category, '') || '|' ||
      coalesce(raw_subcategory, '') || '|' ||
      coalesce(raw_category_path, '') || '|' ||
      coalesce(raw_tags, '') || '|' ||
      coalesce(raw_note, '') || '|' ||
      coalesce(raw_posting_text, '')
    )
  ) STORED,
  inserted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS transactions_dedupe_key_uidx
  ON transactions (dedupe_key);

CREATE INDEX IF NOT EXISTS transactions_booking_date_idx
  ON transactions (booking_date);

CREATE INDEX IF NOT EXISTS transactions_account_id_idx
  ON transactions (account_id);
