from aiogram.fsm.state import State, StatesGroup


class AdminNewUserFSM(StatesGroup):
    """
    States used during the new-user approval flow.

    FLOW:
        1. Unknown user enters the correct password
           → unknown_handler sets RegistrationFSM.wait_for_confirmation
           → admin receives a notification with CONFIRM / DECLINE buttons

        2. Admin presses CONFIRM
           → admin_handler reads this state, asks which role to assign

        3. Admin selects a role
           → service creates the DB record, bot notifies the new user

    These states live in the admin package because only the admin handler
    drives this part of the flow (unknown_handler only sends the request).
    """

    select_role = State()  # waiting for admin to pick a role for the candidate


# TODO: project-specific — add more admin FSM groups below as needed
# Example:
# class AdminBroadcastFSM(StatesGroup):
#     input_text = State()
#     confirm = State()
