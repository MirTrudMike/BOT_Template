from dataclasses import dataclass, field
from environs import Env
from loguru import logger


@dataclass
class TgBot:
    token: str
    admin_id: int
    bot_password: str
    # TODO: project-specific — add extra bot-level settings here
    # group_id: int


@dataclass
class Redis:
    url: str        # e.g. 'redis://localhost:6379/0'


@dataclass
class Database:
    dsn: str        # asyncpg DSN: 'postgresql://user:pass@host:port/dbname'


@dataclass
class Users:
    """
    In-memory role ID lists loaded from the DB at startup.

    WHY IN-MEMORY:
        Checking "is user X in role Y?" happens on every single message.
        Hitting the DB every time would be slow and noisy.
        Instead, we load all IDs once at startup into plain Python lists.
        When a user's role changes (e.g. admin approves registration),
        the service layer updates both the DB and these in-memory lists,
        so filters see the change immediately without a restart.

    TODO: project-specific — add a field for each role in your bot.
    Keep field names in the form <role_name>_ids for consistency with
    the DB query in db/users.py → fetch_all_user_ids_by_type().
    """
    blocked_ids: list[int] = field(default_factory=list)
    role_a_ids: list[int] = field(default_factory=list)
    # role_b_ids: list[int] = field(default_factory=list)


@dataclass
class Config:
    tg_bot: TgBot
    redis: Redis
    db: Database
    users: Users
    # TODO: project-specific — add extra config sections (Google Sheets, S3, etc.)


def load_config() -> Config:
    """
    Reads environment variables from .env and builds the Config object.
    Also loads user ID lists from the DB into Config.users.

    Called ONCE at startup from bot/setup.py before polling starts.
    The .env file must exist at the project root.

    STARTUP DATA FLOW:
        .env → environs → Config dataclasses
        PostgreSQL users table → db/users.py → Config.users lists
    """
    env = Env()
    try:
        env.read_env('.env')

        # Load user ID lists from DB so role filters work from message #1.
        # This is a synchronous call — acceptable here because the event loop
        # is not yet running when load_config() is called.
        from db.users import get_user_ids_grouped_by_type
        user_ids = get_user_ids_grouped_by_type()

        config = Config(
            tg_bot=TgBot(
                token=env('BOT_TOKEN'),
                bot_password=env('BOT_PASSWORD'),
                admin_id=int(env('ADMIN_ID')),
                # TODO: project-specific — read extra env vars here
                # group_id=int(env('SOME_GROUP_ID')),
            ),
            redis=Redis(
                url=env('REDIS_URL', 'redis://localhost:6379/0'),
            ),
            db=Database(
                dsn=env('DB_DSN'),
            ),
            users=Users(
                blocked_ids=user_ids.get('blocked_ids', []),
                role_a_ids=user_ids.get('role_a_ids', []),
                # role_b_ids=user_ids.get('role_b_ids', []),
            ),
        )
        logger.info("CONFIG loaded")
        return config

    except Exception as e:
        logger.error(f"FAILED to load CONFIG: {e}")
        raise
