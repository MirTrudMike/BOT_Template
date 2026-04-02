from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    """
    Logs all incoming user events (messages and callbacks).
    Admin actions are not logged at INFO level, but admin errors are logged at ERROR.

    Usage in bot/setup.py:
        dp.message.middleware(LoggingMiddleware(admin_id=admin_id))
        dp.callback_query.middleware(LoggingMiddleware(admin_id=admin_id))
    """

    def __init__(self, admin_id: int):
        super().__init__()
        self.admin_id = admin_id

    async def __call__(self, handler, event, data):
        user_id = None
        event_description = "Unknown event"

        if isinstance(event, Message):
            user_id = event.from_user.id
            event_description = f"SENT TEXT: '{event.text}'" if event.text else "SENT NON-TEXT MESSAGE"
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            event_description = f"PUSHED BUTTON: '{event.data}'"

        if user_id != self.admin_id:
            logger.info(f"USER-{user_id} * {event_description}")

        try:
            return await handler(event, data)
        except Exception as e:
            label = "ADMIN" if user_id == self.admin_id else f"USER-{user_id or 'UNKNOWN'}"
            logger.opt(exception=e).error(f"{label} * ERROR: {e}")
            raise
