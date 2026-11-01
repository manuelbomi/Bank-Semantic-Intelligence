-- Bank domain contract. All data used by the demo is fabricated.
CREATE TABLE IF NOT EXISTS customers (
 customer_id BIGINT PRIMARY KEY, full_name TEXT NOT NULL,
 dob DATE, email TEXT, region TEXT, marketing_consent BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE IF NOT EXISTS accounts (
 account_id BIGINT PRIMARY KEY, customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
 account_type TEXT NOT NULL, opened_at DATE NOT NULL
);
CREATE TABLE IF NOT EXISTS transactions (
 transaction_id BIGINT PRIMARY KEY, account_id BIGINT NOT NULL REFERENCES accounts(account_id),
 amount_cents BIGINT NOT NULL, currency CHAR(3) NOT NULL,
 tx_type TEXT NOT NULL, country CHAR(2) NOT NULL, occurred_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS alerts (
 alert_id BIGINT PRIMARY KEY, transaction_id BIGINT NOT NULL REFERENCES transactions(transaction_id),
 rule_name TEXT NOT NULL, disposition TEXT NOT NULL DEFAULT 'open'
);
CREATE INDEX IF NOT EXISTS idx_tx_account ON transactions(account_id);
