"""
db/pool.py — Connection pool singleton.

WHY A POOL INSTEAD OF PER-CALL CONNECT:
    Opening a new TCP connection on every DB call is slow (~5-15ms overhead)
    and limits concurrency. A pool keeps N connections open and reuses them.
    Under load (many users simultaneously) this is the difference between
    200ms and 2000ms response times.

USAGE PATTERN — call get_pool() in every query function:

    from db.pool import get_pool

    async def some_query(user_id: int):
        pool = await get_pool()
        async with pool.acquire() as conn:       # borrows a connection from the pool
            row = await conn.fetchrow(            # returns it automatically on exit
                "SELECT * FROM users WHERE id = $1", user_id
            )
        return row                               # connection is back in pool here

INITIALIZATION:
    Call init_pool() once at bot startup (in bot/setup.py) before polling starts.
    Call close_pool() on shutdown if needed.
"""

import asyncpg
from loguru import logger

_pool: asyncpg.Pool | None = None


async def init_pool(dsn: str, min_size: int = 2, max_size: int = 10) -> None:
    """
    Creates the connection pool. Call once at startup in bot/setup.py.

    :param dsn: asyncpg DSN, e.g. 'postgresql://user:pass@localhost:5432/dbname'
                Read from config.db.dsn (loaded from DB_DSN env var).
    :param min_size: Minimum number of connections to keep open at all times.
    :param max_size: Upper limit; pool creates new connections on demand up to this.

    After this returns, every db/* query function can call get_pool() safely.
    """
    global _pool
    _pool = await asyncpg.create_pool(dsn=dsn, min_size=min_size, max_size=max_size)
    logger.info(f"DB pool initialized (min={min_size}, max={max_size})")


async def get_pool() -> asyncpg.Pool:
    """
    Returns the active connection pool.
    Raises RuntimeError if init_pool() was not called first.
    """
    if _pool is None:
        raise RuntimeError("DB pool is not initialized. Call init_pool() at startup.")
    return _pool


async def close_pool() -> None:
    """Gracefully closes all pool connections. Call on bot shutdown if needed."""
    global _pool
    if _pool:
        await _pool.close()
        logger.info("DB pool closed")
        _pool = None
