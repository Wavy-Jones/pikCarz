-- Migration: referral system
-- Run once against your Neon PostgreSQL database

-- Add referral fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code        VARCHAR(20)  UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by          INTEGER REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_count       INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_founding_dealer   BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_ambassador        BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS priority_search_until TIMESTAMPTZ;

-- Referrals tracking table
CREATE TABLE IF NOT EXISTS referrals (
  id            SERIAL PRIMARY KEY,
  referrer_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  referred_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(referred_id)   -- a user can only be referred once
);

CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id);

-- Backfill referral codes for existing users (random 8-char codes)
UPDATE users
SET referral_code = UPPER(SUBSTRING(MD5(id::text || 'pikcarz_salt') FOR 8))
WHERE referral_code IS NULL;
