"""
main.py — entry point. Keep this file thin.

All wiring lives in bot/setup.py. main.py only:
    1. Calls create_bot_and_dp() to get configured objects
    2. Starts polling
    3. Handles graceful shutdown
"""

import asyncio
from loguru import logger
from bot.setup import create_bot_and_dp


async def main() -> None:
    bot, dp = await create_bot_and_dp()
    logger.info("Bot started. Polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == '__main__':
    asyncio.run(main())
