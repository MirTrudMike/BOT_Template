"""
bot/routers.py — centralized router registration.

WHY THIS FILE EXISTS:
    Keeping all include_router() calls in one place makes it easy to see
    the full handler priority order at a glance and to add / remove routers
    without touching bot/setup.py or main.py.

REGISTRATION ORDER RULES:
    1. Error handler — must be first so it catches exceptions from all others.
    2. Common handlers (blocked, unknown) — role-scoped to specific user types,
       so they can be registered early without stealing updates from role routers.
    3. Role-specific routers — registered last.
       Within each role group, more-specific handlers must come before catch-alls.

    aiogram tries routers in registration order and stops at the first match.
    A router with router.message.filter(IsAdmin()) will only process messages
    where IsAdmin() returns True, so role routers don't interfere with each other.
"""

from aiogram import Dispatcher

from handlers.common.errors import router as errors_router
from handlers.common.blocked import router as blocked_router
from handlers.common.unknown import router as unknown_router
from handlers.roles.admin.handlers import router as admin_router
from handlers.roles.role_a.handlers import router as role_a_router
# TODO: project-specific — import additional role routers here


def register_routers(dp: Dispatcher) -> None:
    """
    Include all routers into the dispatcher in priority order.

    Call this once from bot/setup.py during startup.
    """
    dp.include_router(errors_router)   # catches unhandled exceptions from all routers below
    dp.include_router(blocked_router)  # IsBlocked() — blocked users see only this
    dp.include_router(unknown_router)  # IsUnknown() — unregistered users, password flow
    dp.include_router(admin_router)    # IsAdmin()
    dp.include_router(role_a_router)   # IsRoleA()
    # TODO: project-specific — add more role routers in priority order
    # dp.include_router(role_b_router)
