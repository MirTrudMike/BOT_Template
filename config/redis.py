from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config.settings import Redis as RedisConfig


def make_storage(redis_config: RedisConfig) -> RedisStorage:
    """
    Creates and returns a RedisStorage instance for aiogram FSM.

    Accepts the Redis dataclass from config/settings.py.
    The URL (REDIS_URL) is read from .env → config.redis.url.

    WHY REDIS FOR FSM:
        The default MemoryStorage loses all FSM state on restart.
        RedisStorage persists state, so a user mid-flow (e.g. filling out
        a form) does not lose their progress when the bot is redeployed.

    :param redis_config: Redis config dataclass with a `url` field.
    """
    redis = Redis.from_url(redis_config.url)
    return RedisStorage(redis)
