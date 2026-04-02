from aiogram import types
from typing import Callable, Dict, Any, Awaitable


class GroupBlockerMiddleware:
    """
    Drops all events from a specific chat/group ID.
    Useful when the bot is added to a group only for sending notifications
    but must not respond to commands there.

    Usage in bot/setup.py:
        blocker = GroupBlockerMiddleware(blocked_chat_id=group_id)
        dp.message.middleware(blocker)
        dp.callback_query.middleware(blocker)
    """

    def __init__(self, blocked_chat_id: int):
        self.blocked_chat_id = blocked_chat_id

    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, types.Message):
            chat_id = event.chat.id
        elif isinstance(event, types.CallbackQuery):
            chat_id = event.message.chat.id if event.message else None
        else:
            chat_id = None

        if chat_id == self.blocked_chat_id:
            return  # Drop the event entirely

        return await handler(event, data)
