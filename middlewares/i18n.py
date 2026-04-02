from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable
from i18n.translator import Translator


class I18nMiddleware(BaseMiddleware):
    """
    Injects a pre-bound translation function '_' into every handler's data dict.

    How it works:
        1. Reads user's language_code from the incoming event.
        2. Creates a translate callable bound to that language: _(key) → str
        3. Injects it as data['_'] so any handler can declare it as a parameter.

    Usage in main.py / bot/setup.py:
        dp.message.middleware(I18nMiddleware(translator))
        dp.callback_query.middleware(I18nMiddleware(translator))

    Usage in any handler:
        async def my_handler(message: Message, _):
            await message.answer(_('welcome'))
            await message.answer(_('wrong_password', tries=3))
    """

    def __init__(self, translator: Translator):
        self.translator = translator

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        lang = None

        if isinstance(event, Message) and event.from_user:
            lang = event.from_user.language_code
        elif isinstance(event, CallbackQuery) and event.from_user:
            lang = event.from_user.language_code

        # Normalize: Telegram sends 'ru', 'en', 'uk', etc. (already ISO 639-1)
        # Some clients may send 'en-US' — take only the first part
        if lang and '-' in lang:
            lang = lang.split('-')[0]

        data['_'] = self.translator.for_lang(lang)
        return await handler(event, data)
