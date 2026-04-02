from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerMiddleware(BaseMiddleware):
    """
    Injects the APScheduler instance into every update's data dict.
    Handlers can then add or modify jobs via data["apscheduler"].

    Usage in bot/setup.py:
        scheduler = AsyncIOScheduler()
        dp.update.middleware(SchedulerMiddleware(scheduler=scheduler))
        scheduler.start()
    """

    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["apscheduler"] = self.scheduler
        return await handler(event, data)
