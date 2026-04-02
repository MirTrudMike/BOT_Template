import re
from loguru import logger
from datetime import datetime


MAX_BLOCK_LENGTH = 3900
CONTINUATION_NOTE = "\n... continued ..."


def escape_markdown(text: str) -> str:
    """
    Escapes all MarkdownV2 special characters.
    Apply to any user-provided data before sending with parse_mode='MarkdownV2'.
    """
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(rf"([{re.escape(escape_chars)}])", r"\\\1", text)


def is_valid_name(text: str) -> bool:
    """Returns True if the string contains no MarkdownV2 special characters."""
    return not any(char in '_*[]()~`>#+-=|{}.!' for char in text)


def split_into_blocks(text: str) -> list[str]:
    """
    Splits a long MarkdownV2 string into blocks no longer than MAX_BLOCK_LENGTH chars.
    Splits on paragraph boundaries (double newlines).

    Returns [] if any single paragraph exceeds the limit.

    Usage:
        for block in split_into_blocks(long_text):
            await bot.send_message(chat_id, block, parse_mode='MarkdownV2')
    """
    try:
        paragraphs = text.split("\n\n")
        blocks, current_block = [], ""

        for para in paragraphs:
            suffix = f"\n\n{CONTINUATION_NOTE}" if blocks else ""
            if len(current_block) + len(para) + 2 + len(suffix) <= MAX_BLOCK_LENGTH:
                current_block += para + "\n\n"
            else:
                if current_block.strip():
                    blocks.append(current_block.strip() + f"\n\n{CONTINUATION_NOTE}")
                current_block = para + "\n\n"

        if current_block.strip():
            blocks.append(current_block.strip())

        return [] if any(len(b) > MAX_BLOCK_LENGTH for b in blocks) else blocks

    except Exception as e:
        logger.exception(f"ERROR splitting text into blocks: {e}")
        return [text]


def make_day_month_date_ru(date_obj: datetime) -> str:
    """
    Returns a date string in Russian genitive form, e.g. '11 Maya' (May 11).
    Used for human-readable date labels in Russian-language bot messages.
    """
    months_ru = {
        1: "Января", 2: "Февраля", 3: "Марта", 4: "Апреля",
        5: "Мая", 6: "Июня", 7: "Июля", 8: "Августа",
        9: "Сентября", 10: "Октября", 11: "Ноября", 12: "Декабря"
    }
    return f"{date_obj.day} {months_ru[date_obj.month]}"


# TODO: project-specific — add message formatting functions here.
# Pattern: accept plain data → return a ready-to-send MarkdownV2 string.
# Keep formatting out of handlers and services.
#
# Example:
# def format_summary(records: dict, date: datetime) -> str:
#     lines = [f"📅 *{escape_markdown(date.strftime('%d.%m.%Y'))}*"]
#     for name, value in records.items():
#         lines.append(f"🔹 _{escape_markdown(name)}_: {value}")
#     return "\n".join(lines)
