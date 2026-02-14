-- Use the default schema
SET search_path TO public;

-- =========================
-- USERS
-- =========================
CREATE TABLE IF NOT EXISTS users (
  id                 BIGSERIAL PRIMARY KEY,
  email              TEXT NOT NULL UNIQUE,
  name               TEXT NOT NULL,

  -- Optional: user campus / default discovery settings
  campus_lat         DOUBLE PRECISION,
  campus_lng         DOUBLE PRECISION,
  default_radius_km  DOUBLE PRECISION NOT NULL DEFAULT 10.0 CHECK (default_radius_km > 0),

  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================
-- POSTS
-- =========================
CREATE TABLE IF NOT EXISTS posts (
  id           BIGSERIAL PRIMARY KEY,
  seller_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  title        TEXT NOT NULL,
  description  TEXT,
  price_cents  INTEGER NOT NULL CHECK (price_cents >= 0),

  category     TEXT NOT NULL DEFAULT 'other',
  condition    TEXT NOT NULL DEFAULT 'good',

  -- Item location (for radius searching)
  lat          DOUBLE PRECISION,
  lng          DOUBLE PRECISION,

  -- active | archived | sold
  status       TEXT NOT NULL DEFAULT 'active'
               CHECK (status IN ('active', 'archived', 'sold')),

  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- updated_at trigger (simple + hackathon-safe)
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_posts_updated_at ON posts;
CREATE TRIGGER trg_posts_updated_at
BEFORE UPDATE ON posts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- =========================
-- TRANSACTIONS (purchase/handoff)
-- =========================
CREATE TABLE IF NOT EXISTS transactions (
  id          BIGSERIAL PRIMARY KEY,
  post_id     BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  buyer_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  seller_id   BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- pending | completed | canceled
  status      TEXT NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending', 'completed', 'canceled')),

  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT buyer_not_seller CHECK (buyer_id <> seller_id)
);

-- Optional but recommended: one active transaction per post (prevents double-buy)
-- If you want to allow multiple offers, remove this.
CREATE UNIQUE INDEX IF NOT EXISTS ux_transactions_post_id ON transactions(post_id);

-- =========================
-- RATINGS (one per completed transaction)
-- =========================
CREATE TABLE IF NOT EXISTS ratings (
  id              BIGSERIAL PRIMARY KEY,
  transaction_id  BIGINT NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,

  rater_id        BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  ratee_id        BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  stars           INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
  comment         TEXT,

  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT rater_not_ratee CHECK (rater_id <> ratee_id)
);

-- =========================
-- INDEXES (basic performance)
-- =========================
CREATE INDEX IF NOT EXISTS idx_posts_seller_id   ON posts(seller_id);
CREATE INDEX IF NOT EXISTS idx_posts_status      ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_category    ON posts(category);
CREATE INDEX IF NOT EXISTS idx_posts_created_at  ON posts(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_buyer_id  ON transactions(buyer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_seller_id ON transactions(seller_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status    ON transactions(status);

CREATE INDEX IF NOT EXISTS idx_ratings_ratee_id  ON ratings(ratee_id);
CREATE INDEX IF NOT EXISTS idx_ratings_rater_id  ON ratings(rater_id);
