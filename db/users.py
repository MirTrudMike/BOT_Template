"""
db/users.py — All database queries related to the users table.

RESPONSIBILITY:
    This file owns exactly one thing: SQL queries against the users table.
    It knows nothing about Telegram, business rules, or message formatting.
    It receives plain Python values and returns plain Python values (dicts, lists, etc.).

DATA FLOW:
    Handler  →  Service  →  db/users.py  →  PostgreSQL
                         ←               ←
    Handler receives a Telegram event, calls a service function.
    Service applies business logic and calls a DB function here.
    DB function executes SQL and returns raw data.
    Service transforms the data if needed and returns it to the handler.
    Handler formats the result and sends a Telegram message.

NEVER in this file:
    - Business logic (role checks, date calculations, etc.)
    - Sending Telegram messages
    - Calling other services
"""

import asyncio
from datetime import date
from loguru import logger
import asyncpg
from db.pool import get_pool


# ── Read queries ─────────────────────────────────────────────────────

async def fetch_user_by_id(user_id: int) -> asyncpg.Record | None:
    """
    Returns a single user row by Telegram ID, or None if not found.

    TODO: project-specific — extend SELECT columns to match your schema.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT id, type, first_name, last_name, tg_nickname FROM users WHERE id = $1",
            user_id
        )


async def fetch_all_user_ids_by_type() -> dict[str, list[int]]:
    """
    Loads all user IDs from the DB grouped by their role type.
    Called synchronously at bot startup via get_user_ids_grouped_by_type() below.

    Returns: {'role_a_ids': [111, 222], 'blocked_ids': [333], ...}

    TODO: project-specific — replace user_types with your actual role names.
    """
    # TODO: project-specific — list your role names
    user_types = [
        # "role_a",
        # "role_b",
        # "blocked",
    ]

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, type FROM users;")

    result = {f"{t}_ids": [] for t in user_types}
    for row in rows:
        key = f"{row['type']}_ids"
        if key in result:
            result[key].append(row['id'])

    return result


# ── Write queries ────────────────────────────────────────────────────

async def insert_user(
    user_id: int,
    user_type: str,
    first_name: str,
    last_name: str,
    tg_nickname: str,
    language: str,
    # TODO: project-specific — add extra columns from your schema
) -> bool:
    """
    Inserts a new user. Returns True on success, False if user already exists.

    TODO: project-specific — adapt the INSERT statement to your users table schema.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        try:
            await conn.execute(
                """
                INSERT INTO users (id, type, first_name, last_name, tg_nickname, language, date_joined)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (id) DO NOTHING;
                """,
                user_id, user_type, first_name, last_name, tg_nickname, language, date.today()
            )
            logger.info(f"INSERTED user id={user_id} type={user_type}")
            return True
        except asyncpg.UniqueViolationError:
            logger.warning(f"USER {user_id} already exists — skipped")
            return False
        except Exception as e:
            logger.error(f"FAILED to insert user {user_id}: {e}")
            raise


# ── Sync wrapper for startup ─────────────────────────────────────────

def get_user_ids_grouped_by_type() -> dict[str, list[int]]:
    """
    Synchronous wrapper used only at bot startup (before the event loop is running).
    Called from config/settings.py → load_config() to populate Config.users.

    After startup, always use the async fetch_all_user_ids_by_type() directly.
    """
    return asyncio.run(fetch_all_user_ids_by_type())


# ── TODO: project-specific — add more query functions for your tables ─
#
# PATTERN for every new query:
#
#   async def fetch_something(param: type) -> return_type:
#       pool = await get_pool()
#       async with pool.acquire() as conn:
#           result = await conn.fetch("SELECT ...", param)
#       logger.info(f"FETCHED ... for {param}")
#       return result
#
# Keep each function focused on ONE query.
# Transformations and business logic belong in services/, not here.
