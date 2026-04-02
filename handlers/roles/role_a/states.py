from aiogram.fsm.state import State, StatesGroup


# TODO: project-specific — rename RoleAFSM and its states to match your domain.
#
# Naming convention:
#   <RoleName><FeatureName>FSM
#   e.g. StaffOrderFSM, ManagerReportFSM, ClientCheckoutFSM
#
# Each StatesGroup should represent ONE distinct user flow, not everything
# the role can do. Create multiple groups if the role has multiple flows.

class RoleAExampleFSM(StatesGroup):
    """
    Example multi-step FSM for role_a users.

    FLOW (replace with your own):
        step_one  — user provides first input
        step_two  — user provides second input
        confirm   — user reviews and confirms the action
    """
    step_one = State()
    step_two = State()
    confirm = State()
