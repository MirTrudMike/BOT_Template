"""
db/base.py — Generic, reusable DB helpers.

USE THIS FILE FOR:
    - Helpers that work across multiple tables (e.g. check-if-exists, soft-delete pattern)
    - Shared type aliases and constants

DO NOT PUT HERE:
    - Table-specific queries (those go in their own file: db/users.py, db/orders.py, etc.)
    - Business logic

ADDING A NEW TABLE:
    Create a new file: db/<table_name>.py
    Follow the same pattern as db/users.py — one file per table, only SQL inside.
"""

from db.pool import get_pool
from loguru import logger


async def row_exists(table: str, column: str, value) -> bool:
    """
    Generic existence check. Returns True if at least one row matches.

    Example:
        exists = await row_exists('users', 'id', user_id)
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            f"SELECT EXISTS(SELECT 1 FROM {table} WHERE {column} = $1)",
            value
        )
    return bool(result)


# TODO: project-specific — add shared query helpers used across multiple tables
