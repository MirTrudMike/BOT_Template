from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllGroupChats
from loguru import logger
from i18n.translator import Translator


async def set_main_menu(bot: Bot, translator: Translator) -> None:
    """
    Sets the bot command menu for private chats and clears it for all groups.
    Call once at startup in bot/setup.py before polling.

    Commands are taken from the translator using 'cmd_<command>' keys
    so they appear in the user's language automatically.

    TODO: project-specific — add your commands to i18n/en.py with 'cmd_' prefix.
    """
    # TODO: project-specific — list all bot commands
    command_keys: list[tuple[str, str]] = [
        ('help', 'cmd_help'),
        ('exit', 'cmd_exit'),
        # ('your_command', 'cmd_your_command'),
    ]

    try:
        await bot.set_my_commands(
            commands=[
                BotCommand(command=cmd, description=translator.get(key))
                for cmd, key in command_keys
            ],
            scope=BotCommandScopeDefault()
        )
        await bot.delete_my_commands(scope=BotCommandScopeAllGroupChats())
        logger.info("Bot command menu set for private chats, cleared for groups")

    except Exception as e:
        logger.error(f"FAILED to set bot command menu: {e}")
        raise
