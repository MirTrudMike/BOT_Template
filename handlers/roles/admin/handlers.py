from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from filters.role_filters import IsAdmin
from handlers.common.states import RegistrationFSM
from handlers.roles.admin.states import AdminNewUserFSM
from handlers.roles.admin.keyboards import role_selection_kb
from services.user_service import register_new_user  # TODO: implement in services/user_service.py

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

# ---------------------------------------------------------------------------
# /start — admin entry point
# ---------------------------------------------------------------------------

@router.message(Command('start'), StateFilter(default_state))
async def admin_start(message: Message, _):
    """
    Greets the admin and shows the main menu.

    DATA FLOW:
        message arrives → IsAdmin() filter passes → this handler fires
        → send greeting + main-menu keyboard

    TODO: project-specific — replace text key and keyboard with your own.
    """
    await message.answer(_('admin_welcome'))
    # await message.answer(_('admin_welcome'), reply_markup=admin_main_menu_kb(_))


# ---------------------------------------------------------------------------
# New-user approval flow
# ---------------------------------------------------------------------------
# Triggered when the admin taps CONFIRM or DECLINE on the notification sent
# by unknown_handler after a successful password entry.
#
# FULL FLOW:
#   1. Unknown user enters the correct password
#      → unknown_handler sends admin a notification with two inline buttons:
#        callback_data='start_new_user'  (CONFIRM)
#        callback_data='decline_new_user' (DECLINE)
#
#   2. Admin taps CONFIRM
#      → confirm_new_user() below fires
#      → bot reads the candidate's user_id from the callback message
#      → bot asks admin to pick a role (AdminNewUserFSM.select_role)
#
#   3. Admin taps a role button
#      → assign_role() fires
#      → service.register_new_user() creates the DB record
#      → bot notifies the candidate that they've been accepted
#      → FSM cleared
#
#   4. Admin taps DECLINE
#      → decline_new_user() fires
#      → candidate notified they were declined
#      → no DB record created
# ---------------------------------------------------------------------------

@router.callback_query(F.data == 'start_new_user', StateFilter(default_state))
async def confirm_new_user(callback: CallbackQuery, state: FSMContext, _):
    """
    Admin pressed CONFIRM on the new-user notification.

    DATA FLOW:
        callback.message contains the original notification text with
        the candidate's user_id embedded in it (sent by unknown_handler).

        We store the candidate's data in FSM so the next step (role selection)
        can access it without re-reading the message text.

    TODO: adapt the data extraction to match how unknown_handler formats
    the notification message (or switch to storing candidate data in Redis
    via FSM.storage directly, keyed by candidate user_id).
    """
    await callback.answer()
    # Example: extract candidate_id from callback message text
    # candidate_id = int(re.search(r'ID: (\d+)', callback.message.text).group(1))
    # await state.update_data(candidate_id=candidate_id)

    await callback.message.answer(_('select_role_for_new_user'), reply_markup=role_selection_kb(_))
    await state.set_state(AdminNewUserFSM.select_role)


@router.callback_query(F.data == 'decline_new_user', StateFilter(default_state))
async def decline_new_user(callback: CallbackQuery, bot: Bot, _):
    """
    Admin pressed DECLINE on the new-user notification.

    DATA FLOW:
        Extract candidate_id from message text
        → bot.send_message(candidate_id, 'you_were_declined')
        → edit original notification to show 'declined' status (optional)

    TODO: implement candidate_id extraction + send decline message.
    """
    await callback.answer()
    # candidate_id = ...
    # await bot.send_message(candidate_id, _('registration_declined'))
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(_('new_user_declined'))


@router.callback_query(F.data.startswith('assign_role_'), StateFilter(AdminNewUserFSM.select_role))
async def assign_role(callback: CallbackQuery, state: FSMContext, bot: Bot, _):
    """
    Admin selected a role for the new user.

    DATA FLOW:
        callback.data == 'assign_role_a' or 'assign_role_b' (etc.)
        → parse role from callback.data suffix
        → read candidate_id from FSM data (stored in confirm_new_user)
        → call service.register_new_user(candidate_id, role)
            service → db/users.py → INSERT INTO users
        → bot.send_message(candidate_id, 'registration_approved')
        → clear FSM

    TODO: implement register_new_user in services/user_service.py and
    update this handler once you know the exact role values.
    """
    await callback.answer()

    data = await state.get_data()
    candidate_id = data.get('candidate_id')
    role = callback.data.removeprefix('assign_role_')  # e.g. 'a', 'b'

    # await register_new_user(candidate_id, role)
    # await bot.send_message(candidate_id, _('registration_approved'))

    await callback.message.answer(_('user_role_assigned', role=role))
    await state.clear()


# ---------------------------------------------------------------------------
# Candidate is still waiting — admin may have sent them into wait_for_confirmation
# but the admin router also needs to handle admin's own messages in that state.
# Usually not needed unless admin is also a test user. Add if required.
# ---------------------------------------------------------------------------

# TODO: project-specific — add admin-specific commands and handlers below.
# Keep each feature group in its own section with a clear DATA FLOW comment.
