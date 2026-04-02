"""
i18n/translator.py — Lightweight translation engine.

HOW IT WORKS:
    1. At startup, Translator is created and all language dicts are registered.
    2. I18nMiddleware (middlewares/i18n.py) intercepts every update,
       reads the user's language_code from Telegram, and injects a pre-bound
       translate function '_' into data{}.
    3. Handlers declare '_' as a parameter and call _('key') to get translated text.
    4. If the user's language has no translation for a key, English is used as fallback.
    5. If English also lacks the key, the key itself is returned (safe default).

ADDING A NEW LANGUAGE:
    1. Create i18n/de.py (copy structure from i18n/en.py, translate values)
    2. In bot/setup.py, add:
           from i18n import de
           translator.register('de', de.STRINGS)

TELEGRAM LANGUAGE CODES:
    Telegram sends IETF language tags: 'en', 'ru', 'de', 'uk', 'es', etc.
    The first two characters are the ISO 639-1 code.
    Match against those when registering: translator.register('ru', ru.STRINGS)
"""


class Translator:
    def __init__(self, default_lang: str = 'en'):
        self._default = default_lang
        self._strings: dict[str, dict[str, str]] = {}

    def register(self, lang: str, strings: dict[str, str]) -> None:
        """Register a language dict. Call once at startup per language."""
        self._strings[lang] = strings

    def get(self, key: str, lang: str | None = None, **kwargs) -> str:
        """
        Returns the translated string for key in the given language.

        Resolution order:
            1. strings[lang][key]          — exact language match
            2. strings[default_lang][key]  — English fallback
            3. key                         — key itself as last resort

        :param key: Translation key (e.g. 'welcome', 'wrong_password')
        :param lang: ISO 639-1 language code (e.g. 'ru', 'en', 'de')
        :param kwargs: Format arguments, e.g. _('tries_left', tries=3)
        """
        lang = lang or self._default
        text = (
            self._strings.get(lang, {}).get(key)
            or self._strings.get(self._default, {}).get(key)
            or key
        )
        return text.format(**kwargs) if kwargs else text

    def for_lang(self, lang: str | None):
        """
        Returns a pre-bound callable: _(key, **kwargs) → str.
        This is what I18nMiddleware injects into data['_'].

        Usage in a handler:
            async def handler(message: Message, _):
                await message.answer(_('welcome'))
                await message.answer(_('tries_left', tries=2))
        """
        def translate(key: str, **kwargs) -> str:
            return self.get(key, lang, **kwargs)
        return translate
