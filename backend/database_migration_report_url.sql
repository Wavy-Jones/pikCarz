-- Migration: add report_url to vehicles table
-- Run once against your Neon PostgreSQL database

ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS report_url TEXT;
