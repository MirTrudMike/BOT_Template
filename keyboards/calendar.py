from aiogram.filters.callback_data import CallbackData
from datetime import datetime, timedelta

try:
    from aiogram_calendar import SimpleCalendar
except ImportError as e:
    raise ImportError(
        "aiogram_calendar is not installed. "
        "Install it from GitHub: pip install git+https://github.com/noXplode/aiogram_calendar.git"
    ) from e
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from enum import Enum


class SimpleCalAct(str, Enum):
    day = "DAY"
    prev_m = "PREV-MONTH"
    next_m = "NEXT-MONTH"
    prev_y = "PREV-YEAR"
    next_y = "NEXT-YEAR"
    today = "TODAY"
    cancel = "CANCEL"
    ignore = "IGNORE"
    confirm = "CONFIRM"


class SimpleCalendarCallback(CallbackData, prefix="simple_cal"):
    act: SimpleCalAct
    year: int
    month: int
    day: int


class MultiSelectionCalendar(SimpleCalendar):
    """
    Calendar supporting multi-date selection.
    Replaces the bottom row with a single 'Confirm' button.
    Use with ConfirmCalendarFilter from filters/input_filters.py.
    """
    async def start_calendar(
        self,
        year: int = datetime.now().year,
        month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:
        markup: InlineKeyboardMarkup = await super().start_calendar(year, month)
        markup.inline_keyboard[-1] = [
            InlineKeyboardButton(
                text="Confirm",
                callback_data=SimpleCalendarCallback(
                    act=SimpleCalAct.confirm, year=year, month=month, day=1
                ).pack()
            )
        ]
        return markup


class RegularCalendar(SimpleCalendar):
    """Standard calendar without navigation buttons in the bottom row."""
    async def start_calendar(
        self,
        year: int = datetime.now().year,
        month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:
        markup: InlineKeyboardMarkup = await super().start_calendar(year, month)
        markup.inline_keyboard.pop(-1)
        return markup


# ── Calendar factory functions ───────────────────────────────────────
# TODO: project-specific — set date ranges to match your business logic

async def set_multi_selection_calendar(
    min_date: datetime = None,
    max_date: datetime = None,
) -> MultiSelectionCalendar:
    """
    TODO: project-specific — configure min/max dates for your use case.
    """
    calendar = MultiSelectionCalendar(show_alerts=True)
    now = datetime.now()
    calendar.set_dates_range(
        min_date or now.replace(day=1),
        max_date or now,
    )
    return calendar


async def set_range_calendar(
    min_date: datetime = None,
    max_date: datetime = None,
    days: int = 30,
) -> RegularCalendar:
    """
    TODO: project-specific — replace default min_date with your project start date.

    :param days: Range length from min_date if max_date is not given
    """
    calendar = RegularCalendar(show_alerts=True)
    now = datetime.now()

    if min_date is None:
        min_date = datetime(now.year, now.month, 1)  # TODO: project-specific
    if max_date is None:
        max_date = min(min_date + timedelta(days=days - 1), now)

    calendar.set_dates_range(min_date, max_date)
    return calendar
