from aiogram import Bot
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# TODO: project-specific — import your scheduled task functions
# from services.notification_service import broadcast
# from services.your_service import your_task_function


def set_schedulers(bot: Bot, config) -> AsyncIOScheduler:
    """
    Creates an AsyncIOScheduler, registers all periodic cron jobs, starts it,
    and returns the running scheduler instance.

    Called once at startup from bot/setup.py.
    The returned scheduler is passed to SchedulerMiddleware so handlers can
    also add/remove jobs at runtime if needed.

    Each job registration is wrapped in its own try/except so one broken
    registration does not prevent the others from being scheduled.

    PATTERN per job:
        try:
            scheduler.add_job(
                your_async_function,       # must be async
                trigger='cron',
                hour="9", minute="0",      # UTC by default — set timezone if needed
                kwargs={                   # arguments forwarded to the function
                    'bot': bot,
                    # 'admin_id': config.tg_bot.admin_id,
                }
            )
            logger.info("Scheduled: job_name at HH:MM")
        except Exception as e:
            logger.error(f"FAILED to schedule job_name: {e}")

    :param bot: Aiogram Bot instance (passed into job kwargs as needed)
    :param config: Full Config object from config/settings.py
    :returns: Started AsyncIOScheduler instance
    """
    scheduler = AsyncIOScheduler()

    # TODO: project-specific — add your real jobs below.

    # Example: daily job at 09:00 UTC
    # try:
    #     scheduler.add_job(
    #         your_task_function,
    #         trigger='cron',
    #         hour="9",
    #         minute="0",
    #         kwargs={'bot': bot, 'admin_id': config.tg_bot.admin_id}
    #     )
    #     logger.info("Scheduled: your_task_function at 09:00")
    # except Exception as e:
    #     logger.error(f"FAILED to schedule your_task_function: {e}")

    # Example: job every 30 minutes
    # try:
    #     scheduler.add_job(
    #         another_task,
    #         trigger='cron',
    #         minute="0,30",
    #         kwargs={'bot': bot}
    #     )
    #     logger.info("Scheduled: another_task every 30 minutes")
    # except Exception as e:
    #     logger.error(f"FAILED to schedule another_task: {e}")

    scheduler.start()
    logger.info("Scheduler started")
    return scheduler
