from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class IsAdmin(BaseFilter):
    """Checks whether the user is the bot administrator."""
    async def __call__(self, event: Message | CallbackQuery, admin_id: int):
        return event.from_user.id == admin_id


class IsBlocked(BaseFilter):
    """Checks whether the user is in the blocked list."""
    async def __call__(self, event: Message | CallbackQuery, blocked_ids: list):
        return event.from_user.id in blocked_ids


class IsUnknown(BaseFilter):
    """
    Returns True if the user belongs to no known role.
    Used to scope the registration/onboarding router.

    Receives all role ID lists from workflow_data as named parameters.
    When you add a new role, add its list here AND in the return statement.

    TODO: project-specific — uncomment role_a_ids / role_b_ids as you add roles.
    """
    async def __call__(
        self,
        event: Message | CallbackQuery,
        admin_id: int,
        blocked_ids: list,
        role_a_ids: list,     # injected from dp.workflow_data
        # role_b_ids: list,   # uncomment when role_b is added
    ):
        user_id = event.from_user.id
        return all([
            user_id != admin_id,
            user_id not in blocked_ids,
            user_id not in role_a_ids,
            # user_id not in role_b_ids,  # uncomment when role_b is added
        ])


class IsRoleA(BaseFilter):
    """
    Returns True if the user is registered with role 'role_a'.

    role_a_ids is a list[int] loaded from the DB at startup and kept in
    dp.workflow_data. When a new user is registered with role_a, the service
    layer appends their ID to this list so the filter works immediately.

    TODO: project-specific — rename to match your actual role name.
    Copy this pattern to add more roles; register the list in bot/setup.py.
    """
    async def __call__(self, event: Message | CallbackQuery, role_a_ids: list):
        return event.from_user.id in role_a_ids


# TODO: project-specific — copy IsRoleA for each additional role.
#
# class IsRoleB(BaseFilter):
#     async def __call__(self, event: Message | CallbackQuery, role_b_ids: list):
#         return event.from_user.id in role_b_ids
