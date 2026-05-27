-- Migration: add dealer_address to users table
-- Run once against your Neon PostgreSQL database

ALTER TABLE users ADD COLUMN IF NOT EXISTS dealer_address TEXT;
