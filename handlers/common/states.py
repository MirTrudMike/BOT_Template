from aiogram.fsm.state import State, StatesGroup


class RegistrationFSM(StatesGroup):
    """
    Shared onboarding states used by both unknown_handler and admin_handler.
    unknown_handler sets the state; admin_handler can read it on approval.
    """
    input_pass = State()
    wait_for_confirmation = State()
