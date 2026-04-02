from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger


def create_inline_kb(width: int, *args, **kwargs: str) -> InlineKeyboardMarkup:
    """
    Universal inline keyboard builder.

    Usage:
        create_inline_kb(2, 'opt_a', 'opt_b')               # text = callback_data
        create_inline_kb(1, confirm='Confirm', cancel='Cancel')  # explicit text
        create_inline_kb(2, 'opt_a', confirm='Confirm')      # mixed

    :param width: Buttons per row
    :param args: callback_data values (button text = callback_data)
    :param kwargs: {callback_data: button_text}
    """
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    for button in args:
        buttons.append(InlineKeyboardButton(text=button, callback_data=button))

    for callback_data, text in kwargs.items():
        buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))

    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup()


def create_multi_choice_kb(width: int, *args, **kwargs) -> InlineKeyboardMarkup:
    """
    Inline keyboard with multiple-selection support.
    Selected buttons carry the '🔸 ' prefix both in text and detection.

    Handler toggle logic:
        if callback.data in currently_selected:
            remove '🔸 ' prefix, rebuild keyboard without it selected
        else:
            add '🔸 ' prefix, rebuild keyboard with it selected

    :param width: Buttons per row
    :param args: callback_data. Prefix with '🔸 ' to render as selected.
    :param kwargs: {callback_data: text} — always without selection marker
    """
    try:
        kb_builder = InlineKeyboardBuilder()
        buttons: list[InlineKeyboardButton] = []

        for button in args:
            if button.startswith('🔸 '):
                clean = button[2:]
                buttons.append(InlineKeyboardButton(text=f"🔸 {clean}", callback_data=clean))
            else:
                buttons.append(InlineKeyboardButton(text=button, callback_data=button))

        for callback_data, text in kwargs.items():
            buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))

        kb_builder.row(*buttons, width=width)
        return kb_builder.as_markup()

    except Exception as e:
        logger.error(f"Error creating multi-choice keyboard: {e}", exc_info=True)
        raise


# TODO: project-specific — add shared static keyboards below
# Example:
# confirm_cancel_kb = create_inline_kb(2, confirm='Confirm', cancel='Cancel')
