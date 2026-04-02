from aiogram.types import ErrorEvent
from aiogram import Router, Bot
from loguru import logger
import traceback
from functions.text import escape_markdown

router = Router()


@router.errors()
async def global_error_handler(error: ErrorEvent, bot: Bot, admin_id: int):
    """
    Catches all unhandled exceptions across every handler.
    Logs the error and sends an alert to the admin (with traceback) for user-triggered errors.
    Returns True to tell aiogram the error has been handled.
    """
    user_id = None
    if error.update.message:
        user_id = error.update.message.from_user.id
    elif error.update.callback_query:
        user_id = error.update.callback_query.from_user.id

    is_admin = user_id == admin_id
    user_display = 'ADMIN' if is_admin else user_id or 'UNKNOWN'

    logger.error(f"USER-{user_display} * UNHANDLED ERROR: {error.exception}")

    if not is_admin:
        exc_summary = f"{type(error.exception).__name__}: {error.exception}"
        tb = ''.join(traceback.format_exception(
            type(error.exception), error.exception, error.exception.__traceback__
        ))
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=(
                    f"⚠️ *ERROR ALERT*\n\n"
                    f"👤 User: `{user_display}`\n"
                    f"💥 Exception: `{escape_markdown(exc_summary)}`\n\n"
                    f"🧵 Traceback:\n```{escape_markdown(tb[-1000:])}```"
                ),
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            logger.error(f"FAILED to notify admin: {e}")

    return True
