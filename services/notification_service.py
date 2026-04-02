"""
services/notification_service.py — Sending notifications and alerts.

RESPONSIBILITY:
    Anything that broadcasts messages to multiple users or sends admin alerts.
    Handlers call these functions when they need to notify someone other than
    the user who triggered the event.

DATA FLOW — Admin error alert example:

    errors.py (handlers/common/errors.py)
        │
        │  catches: unhandled exception
        │  calls:   notification_service.alert_admin(exception, location, bot, admin_id)
        ▼
    notification_service.py  (HERE)
        │
        │  formats: error message with escaped MarkdownV2
        │  sends:   bot.send_message(admin_id, ...)
        │  logs:    result
        ▼
    Admin receives a Telegram alert

DATA FLOW — Broadcast to a role group example:

    some_scheduled_job (schedulers/jobs.py)
        │
        │  calls: notification_service.broadcast(user_ids, text, bot)
        ▼
    notification_service.py  (HERE)
        │
        │  iterates over user_ids
        │  sends: bot.send_message per user (with error isolation per user)
        │  logs:  success / skip / failure counts
        ▼
    Each user receives the message independently
"""

import traceback
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, TelegramObject
from loguru import logger
from functions.text import escape_markdown


async def alert_admin(
    exception: Exception,
    location: str,
    bot: Bot,
    admin_id: int,
    traceback_length: int = 1000,
) -> None:
    """
    Sends a formatted error alert to the admin via Telegram.
    Call this in except blocks of scheduled tasks and critical paths.

    :param exception: The caught exception
    :param location: Human-readable description of where the error occurred
    :param bot: Bot instance
    :param admin_id: Admin Telegram user ID
    :param traceback_length: Max traceback characters to include
    """
    try:
        exc_summary = f"{type(exception).__name__}: {str(exception)}"
        tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        tb_short = tb[-traceback_length:]

        text = (
            f"⚠️ *ERROR ALERT*\n\n"
            f"📍 Location: `{escape_markdown(location)}`\n"
            f"💥 Exception: `{escape_markdown(exc_summary)}`\n\n"
            f"🧵 Traceback:\n```{escape_markdown(tb_short)}```"
        )
        await bot.send_message(chat_id=admin_id, text=text, parse_mode="MarkdownV2")

    except Exception as send_error:
        logger.error(f"FAILED to send admin alert: {send_error}")


async def broadcast(
    user_ids: list[int],
    text: str,
    bot: Bot,
    parse_mode: str | None = None,
    reply_markup=None,
) -> dict[str, int]:
    """
    Sends a message to a list of users.
    Each user is handled independently — a failure for one does not stop the others.

    Returns a stats dict: {'success': N, 'failed': N}

    Called from: schedulers/jobs.py for scheduled notifications,
                 or from handlers when notifying a group after an action.
    """
    success, failed = 0, 0

    for user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            success += 1
            logger.info(f"BROADCAST sent to USER-{user_id}")
        except Exception as e:
            failed += 1
            logger.error(f"BROADCAST FAILED for USER-{user_id}: {e}")

    logger.info(f"BROADCAST complete | success={success} failed={failed}")
    return {'success': success, 'failed': failed}


def get_message_from_event(event: TelegramObject) -> Message:
    """
    Extracts the Message object from either a Message or a CallbackQuery.
    Utility used in handlers that accept both event types.
    """
    if isinstance(event, CallbackQuery):
        return event.message
    elif isinstance(event, Message):
        return event
    raise TypeError(f"Unsupported event type: {type(event)}")


# TODO: project-specific — add domain-specific notification functions
#
# PATTERN:
#   async def notify_role_about_something(role_ids: list[int], data: ..., bot: Bot):
#       text = format_something_message(data)   # formatting lives in functions/text.py
#       await broadcast(role_ids, text, bot, parse_mode='MarkdownV2')
