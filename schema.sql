-- schema.sql — Initial database schema for the bot.
--
-- Run once at project setup:
--   psql YOUR_DB_DSN -f schema.sql
--   or: make db  (reads DB_DSN from .env automatically)
--
-- TODO: project-specific — extend users table with your columns,
--       add extra tables below the users table definition.

-- ---------------------------------------------------------------------------
-- Users table
-- ---------------------------------------------------------------------------
-- id          — Telegram numeric user ID (primary key)
-- type        — role name: 'role_a', 'blocked', etc.  (project-specific)
-- first_name  — Telegram first name at registration time
-- last_name   — Telegram last name at registration time (may be empty)
-- tg_nickname — Telegram @username at registration time (may be empty)
-- language    — Telegram language_code sent by the client (e.g. 'en', 'ru')
-- date_joined — date the admin approved the user

CREATE TABLE IF NOT EXISTS users (
    id          BIGINT       PRIMARY KEY,
    type        VARCHAR(50)  NOT NULL,
    first_name  VARCHAR(255) NOT NULL DEFAULT '',
    last_name   VARCHAR(255) NOT NULL DEFAULT '',
    tg_nickname VARCHAR(255) NOT NULL DEFAULT '',
    language    VARCHAR(10)  NOT NULL DEFAULT 'en',
    date_joined DATE         NOT NULL
);

-- Index for role-based lookups (used at startup to load ID lists by type)
CREATE INDEX IF NOT EXISTS idx_users_type ON users (type);

-- ---------------------------------------------------------------------------
-- TODO: project-specific — add your tables below
-- ---------------------------------------------------------------------------
-- Example:
--
-- CREATE TABLE IF NOT EXISTS orders (
--     id         SERIAL      PRIMARY KEY,
--     user_id    BIGINT      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     status     VARCHAR(50) NOT NULL DEFAULT 'pending',
--     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
-- );
