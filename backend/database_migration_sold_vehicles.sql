-- "Mark as Sold" feature: ribbon for 7 days, then auto-removed.
-- Run this against your Neon database before deploying.

ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS sold_at TIMESTAMPTZ;

CREATE TABLE IF NOT EXISTS sold_vehicles (
    id         SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL,
    owner_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    make       VARCHAR NOT NULL,
    model      VARCHAR NOT NULL,
    year       INTEGER,
    price      NUMERIC(12,2),
    sold_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sold_vehicles_sold_at ON sold_vehicles(sold_at);
