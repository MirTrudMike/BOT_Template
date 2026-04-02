from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from keyboards.common import create_inline_kb
from filters.role_filters import IsUnknown
from handlers.common.states import RegistrationFSM
from services.user_service import handle_password_attempt

router = Router()
router.message.filter(IsUnknown())
router.callback_query.filter(IsUnknown())


@router.message(Command('start'), StateFilter(default_state))
async def unknown_start(message: Message, state: FSMContext, _):
    """
    Entry point for unregistered users.
    Sets FSM state and asks for the access password.
    """
    await message.answer(_('welcome'))
    await state.set_state(RegistrationFSM.input_pass)
    await state.update_data(tries=4)


@router.message(F.text, StateFilter(RegistrationFSM.input_pass))
async def check_password(
    message: Message,
    state: FSMContext,
    admin_id: int,
    blocked_ids: list,
    bot_password: str,
    bot: Bot,
    _,
):
    """
    Delegates password validation to user_service.handle_password_attempt().

    DATA FLOW:
        1. Read FSM data (tries counter)
        2. Call service with all raw values → get a PasswordResult
        3. Based on result.status, send the appropriate reply
        4. Update FSM state accordingly

    The handler knows NOTHING about the rules — that's the service's job.
    """
    data = await state.get_data()
    user = message.from_user

    result = await handle_password_attempt(
        password_input=message.text,
        correct_password=bot_password,
        tries_left=data['tries'],
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name or '',
        tg_nickname=user.username or '',
        language=user.language_code or 'en',
        blocked_ids=blocked_ids,
    )

    if result.status == 'blocked':
        await message.answer(_('you_are_blocked'))
        await state.clear()

    elif result.status == 'wrong':
        await message.answer(_('wrong_password', tries=result.tries_left))
        await state.update_data(tries=result.tries_left)

    else:  # 'correct'
        await message.answer(_('waiting_confirmation'))
        await bot.send_message(
            chat_id=admin_id,
            text=_('new_user_request',
                   user_id=user.id,
                   tg_nickname=user.username or '',
                   first_name=user.first_name,
                   last_name=user.last_name or '',
                   language=user.language_code or '?'),
            reply_markup=create_inline_kb(
                1,
                start_new_user="CONFIRM",
                decline_new_user="DECLINE",
            )
        )
        await state.clear()
        await state.set_state(RegistrationFSM.wait_for_confirmation)


@router.message(StateFilter(RegistrationFSM.wait_for_confirmation))
async def still_waiting(message: Message, _):
    await message.answer(_('still_waiting'))
