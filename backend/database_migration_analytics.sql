-- Migration: create page_views table for Option 2 analytics
-- Run once against your Neon PostgreSQL database

CREATE TABLE IF NOT EXISTS page_views (
  id           SERIAL PRIMARY KEY,
  page_url     TEXT NOT NULL,
  page_title   VARCHAR(255),
  referrer     TEXT,
  device_type  VARCHAR(20),
  session_id   VARCHAR(64),
  user_id      INTEGER REFERENCES users(id) ON DELETE SET NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_page_views_created_at ON page_views(created_at);
CREATE INDEX IF NOT EXISTS idx_page_views_session_id ON page_views(session_id);
CREATE INDEX IF NOT EXISTS idx_page_views_page_url   ON page_views(page_url);
