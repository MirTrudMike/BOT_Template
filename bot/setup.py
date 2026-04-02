"""
bot/setup.py — bot and dispatcher factory.

This module is the single place where all infrastructure is wired together
at startup. main.py calls create_bot_and_dp() and gets back ready-to-run
objects. No business logic lives here — only wiring.

STARTUP SEQUENCE (called by main.py):
    1. setup_logging()     — configure loguru sinks
    2. load_config()       — read .env + load user ID lists from DB
    3. init_pool()         — open asyncpg connection pool to PostgreSQL
    4. Bot + Dispatcher    — create with RedisStorage FSM backend
    5. Translator          — register language dicts from i18n/
    6. Middlewares         — register in order (see comments below)
    7. workflow_data       — inject shared values as handler parameters
    8. Routers             — include all routers via bot/routers.py
    9. set_main_menu()     — register bot commands with Telegram
    10. set_schedulers()   — start APScheduler background jobs

DATA FLOW through middleware stack (message arrives):
    Telegram → aiogram Dispatcher
    → GroupBlockerMiddleware   blocks all group/supergroup/channel updates
    → LoggingMiddleware        logs user_id + message type
    → SchedulerMiddleware      injects `scheduler` into handler data
    → I18nMiddleware           injects `_` (bound translator) into handler data
    → role filter on router    (IsAdmin / IsRoleA / IsBlocked / IsUnknown)
    → handler function
"""

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import load_config
from config.redis import make_storage
from config.logging import setup_logging
from db.pool import init_pool
from i18n.translator import Translator
from i18n import en, ru                         # add more language modules here
from middlewares.logging import LoggingMiddleware
from middlewares.group_blocker import GroupBlockerMiddleware
from middlewares.i18n import I18nMiddleware
from schedulers.middleware import SchedulerMiddleware
from schedulers.jobs import set_schedulers
from functions.menu import set_main_menu
from bot.routers import register_routers


async def create_bot_and_dp() -> tuple[Bot, Dispatcher]:
    """
    Build and configure the Bot and Dispatcher.

    Returns (bot, dp) ready for dp.start_polling(bot).
    All side effects (DB pool, scheduler) are started here.
    """
    # ------------------------------------------------------------------
    # 1. Logging
    # ------------------------------------------------------------------
    setup_logging()

    # ------------------------------------------------------------------
    # 2. Config (reads .env, loads user ID lists from DB synchronously)
    # ------------------------------------------------------------------
    # load_config() calls db/users.py → fetch_all_user_ids_by_type() via
    # asyncio.run() to populate Config.users before the event loop starts.
    config = load_config()

    # ------------------------------------------------------------------
    # 3. Database pool
    # ------------------------------------------------------------------
    # Opens persistent connections to PostgreSQL.
    # Every db/* function calls get_pool() to borrow a connection.
    # DSN comes from DB_DSN env var → config.db.dsn.
    await init_pool(dsn=config.db.dsn, min_size=2, max_size=10)

    # ------------------------------------------------------------------
    # 4. Bot + Dispatcher
    # ------------------------------------------------------------------
    # RedisStorage keeps FSM state across restarts.
    # make_storage() reads REDIS_URL from config.redis.url.
    storage = make_storage(config.redis)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    # ------------------------------------------------------------------
    # 5. Translator
    # ------------------------------------------------------------------
    # English (en) is the required base — every key used anywhere must exist there.
    # Other languages override only the keys that differ.
    # Missing keys fall back to English; missing English keys return the key itself.
    #
    # To add a new language:
    #   1. Create i18n/de.py with STRINGS = {...}
    #   2. Add:  from i18n import de
    #            translator.register('de', de.STRINGS)
    translator = Translator(default_lang='en')
    translator.register('en', en.STRINGS)
    translator.register('ru', ru.STRINGS)

    # ------------------------------------------------------------------
    # 6. Middlewares (ORDER MATTERS — outer-to-inner)
    # ------------------------------------------------------------------
    # GroupBlockerMiddleware: MUST be first. Drops group/channel updates before
    # anything else processes them (avoids leaking private features to groups).
    dp.update.outer_middleware(GroupBlockerMiddleware())

    # LoggingMiddleware: logs every user action for debugging and audit.
    dp.message.middleware(LoggingMiddleware(admin_id=config.tg_bot.admin_id))
    dp.callback_query.middleware(LoggingMiddleware(admin_id=config.tg_bot.admin_id))

    # SchedulerMiddleware: injects `scheduler` so handlers can add/remove jobs.
    scheduler = set_schedulers(bot, config)
    dp.update.middleware(SchedulerMiddleware(scheduler))

    # I18nMiddleware: MUST come after logging (relies on from_user being accessible).
    # Injects `_` (bound translate function) into every handler's data dict.
    dp.update.middleware(I18nMiddleware(translator))

    # ------------------------------------------------------------------
    # 7. workflow_data — shared values injected as handler parameters
    # ------------------------------------------------------------------
    # Any key added here becomes an optional named parameter in handlers.
    # Role ID lists are mutable — services append to them directly so
    # role filters (filters/role_filters.py) see new users immediately.
    #
    # Example handler signature:
    #   async def my_handler(message: Message, admin_id: int, role_a_ids: list, _):
    dp.workflow_data.update({
        'admin_id':      config.tg_bot.admin_id,
        'bot_password':  config.tg_bot.bot_password,
        'blocked_ids':   config.users.blocked_ids,   # list[int], mutated on block
        'role_a_ids':    config.users.role_a_ids,    # list[int], mutated on approval
        # TODO: project-specific — add more role lists and shared values
        # 'role_b_ids':  config.users.role_b_ids,
        # 'google_sheet_id': config.google.sheet_id,
    })

    # ------------------------------------------------------------------
    # 8. Routers
    # ------------------------------------------------------------------
    register_routers(dp)

    # ------------------------------------------------------------------
    # 9. Bot commands menu
    # ------------------------------------------------------------------
    await set_main_menu(bot, translator)

    return bot, dp
