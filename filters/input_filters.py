from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter


def is_float(message: Message) -> bool:
    """Returns True if the message text is a valid float number."""
    try:
        float(message.text.strip())
        return True
    except ValueError:
        return False


def is_int(message: Message) -> bool:
    """Returns True if the message text is a valid integer."""
    try:
        int(message.text.strip())
        return True
    except ValueError:
        return False


class ConfirmCalendarFilter(Filter):
    """
    Matches the confirm callback from MultiSelectionCalendar.
    Use together with keyboards/calendar.py.
    """
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.startswith('simple_cal:CONFIRM')


# TODO: project-specific — add DB-backed button filters following this pattern:
#
# class SomeEntityFilter(Filter):
#     async def __call__(self, callback: CallbackQuery) -> bool:
#         entities = await fetch_something_from_db()
#         return callback.data in entities
