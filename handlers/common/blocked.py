from aiogram import Router
from aiogram.types import Message
from filters.role_filters import IsBlocked

router = Router()
router.message.filter(IsBlocked())
router.callback_query.filter(IsBlocked())


@router.message()
async def blocked_user_message(message: Message, _):
    # TODO: project-specific — replace key with your lexicon key if needed
    await message.answer(text=_('you_are_blocked'))
