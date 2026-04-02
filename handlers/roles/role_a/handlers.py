from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from filters.role_filters import IsRoleA
from handlers.roles.role_a.states import RoleAExampleFSM
from handlers.roles.role_a.keyboards import role_a_main_menu_kb, role_a_confirm_kb

router = Router()
router.message.filter(IsRoleA())        # all messages in this router require role_a
router.callback_query.filter(IsRoleA())  # same for callbacks

# ---------------------------------------------------------------------------
# /start — role_a entry point
# ---------------------------------------------------------------------------

@router.message(Command('start'), StateFilter(default_state))
async def role_a_start(message: Message, _):
    """
    Greets role_a users and shows the main menu.

    DATA FLOW:
        /start message arrives
        → IsRoleA() filter checks db (or workflow_data cache) for user role
        → this handler fires → send greeting + main-menu keyboard

    TODO: replace 'role_a_welcome' with your actual lexicon key.
    """
    await message.answer(_('role_a_welcome'), reply_markup=role_a_main_menu_kb(_))


# ---------------------------------------------------------------------------
# Example multi-step flow (RoleAExampleFSM)
# ---------------------------------------------------------------------------
# Replace this entire block with your real feature.
#
# PATTERN:
#   Each step handler:
#     1. Validates / processes the current input
#     2. Calls a service function if business logic is needed
#        (service → db layer → PostgreSQL)
#     3. Advances the FSM to the next state
#     4. Sends the next prompt / keyboard to the user
#   The final step:
#     1. Calls the service to persist the complete action
#     2. Clears the FSM
#     3. Confirms success to the user
# ---------------------------------------------------------------------------

@router.callback_query(F.data == 'role_a_action_one', StateFilter(default_state))
async def start_example_flow(callback: CallbackQuery, state: FSMContext, _):
    """
    Entry point for the example multi-step flow.

    DATA FLOW:
        user taps 'action_one' button
        → bot asks for step_one input
        → FSM advances to RoleAExampleFSM.step_one
    """
    await callback.answer()
    await callback.message.answer(_('enter_step_one_value'))
    await state.set_state(RoleAExampleFSM.step_one)


@router.message(F.text, StateFilter(RoleAExampleFSM.step_one))
async def handle_step_one(message: Message, state: FSMContext, _):
    """
    Receives and stores the step_one value.

    DATA FLOW:
        user sends text
        → validate (optional; use filters/input_filters.py for typed input)
        → store in FSM: await state.update_data(step_one=message.text)
        → advance to step_two
    """
    await state.update_data(step_one=message.text)
    await message.answer(_('enter_step_two_value'))
    await state.set_state(RoleAExampleFSM.step_two)


@router.message(F.text, StateFilter(RoleAExampleFSM.step_two))
async def handle_step_two(message: Message, state: FSMContext, _):
    """
    Receives and stores the step_two value, then asks for confirmation.

    DATA FLOW:
        user sends text
        → store in FSM: await state.update_data(step_two=message.text)
        → build a summary string from FSM data
        → send summary + confirm/cancel keyboard
        → advance to confirm state
    """
    await state.update_data(step_two=message.text)
    data = await state.get_data()

    summary = _('flow_summary', step_one=data['step_one'], step_two=data['step_two'])
    await message.answer(summary, reply_markup=role_a_confirm_kb(_))
    await state.set_state(RoleAExampleFSM.confirm)


@router.callback_query(F.data == 'role_a_confirm', StateFilter(RoleAExampleFSM.confirm))
async def handle_confirm(callback: CallbackQuery, state: FSMContext, _):
    """
    User confirmed the action.

    DATA FLOW:
        callback arrives
        → read full FSM data
        → call service function:
            service validates business rules
            → calls db layer → INSERT / UPDATE in PostgreSQL
            → returns result
        → send success message
        → clear FSM
    """
    await callback.answer()
    data = await state.get_data()

    # Example service call (implement in services/):
    # result = await some_service.save_action(
    #     user_id=callback.from_user.id,
    #     step_one=data['step_one'],
    #     step_two=data['step_two'],
    # )

    await callback.message.answer(_('action_saved'))
    await state.clear()


@router.callback_query(F.data == 'role_a_cancel', StateFilter(RoleAExampleFSM.confirm))
async def handle_cancel(callback: CallbackQuery, state: FSMContext, _):
    """
    User cancelled the action — clear FSM and return to default state.
    No DB call needed since nothing was persisted yet.
    """
    await callback.answer()
    await callback.message.answer(_('action_cancelled'))
    await state.clear()


# ---------------------------------------------------------------------------
# TODO: project-specific — add more role_a features below.
# Copy the pattern above: entry point → step handlers → confirm/cancel.
# ---------------------------------------------------------------------------
