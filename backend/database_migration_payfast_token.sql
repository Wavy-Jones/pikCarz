-- Adds support for PayFast recurring billing (subscription tokens)
-- Run this against your Neon database before deploying.

ALTER TABLE users ADD COLUMN IF NOT EXISTS payfast_token VARCHAR;
CREATE INDEX IF NOT EXISTS idx_users_payfast_token ON users (payfast_token);
