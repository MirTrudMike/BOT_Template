"""
services/user_service.py — Business logic for user management.

RESPONSIBILITY:
    This layer sits between handlers and the DB.
    It owns the RULES — what is allowed, what should happen, what to return.
    The DB layer (db/users.py) owns the SQL.
    The handler layer (handlers/) owns the Telegram interaction.

DATA FLOW — Registration example:

    unknown_handler.py (handlers/common/unknown.py)
        │
        │  receives: Message with password attempt
        │  calls:    user_service.handle_password_attempt(user_id, password, ...)
        ▼
    user_service.py  (HERE)
        │
        │  checks:   is the password correct?
        │  checks:   how many attempts are left?
        │  decides:  block the user OR approve OR decrement counter
        │  calls:    db/users.py → insert_user(user_id, 'blocked', ...)
        │  returns:  PasswordResult(status='blocked'|'wrong'|'correct', tries_left=N)
        ▼
    unknown_handler.py
        │
        │  receives: PasswordResult
        │  sends:    the appropriate Telegram message to the user
        ▼
    User sees the response

WHY THIS SEPARATION:
    - Handler stays thin: parse input → call service → send reply. Nothing else.
    - Service is testable without Telegram (just call the function with plain values).
    - DB functions are reusable across multiple services without duplication.
    - When business rules change, you edit ONE place (the service), not every handler.
"""

from dataclasses import dataclass
from loguru import logger
from db.users import insert_user, fetch_user_by_id
from db.base import row_exists


# ── Result objects ────────────────────────────────────────────────────
# Services return structured result objects, not raw strings.
# This makes handler code readable and avoids string-matching on results.

@dataclass
class PasswordResult:
    status: str          # 'correct' | 'wrong' | 'blocked'
    tries_left: int = 0


@dataclass
class RegistrationResult:
    success: bool
    user_type: str | None = None


# ── Service functions ─────────────────────────────────────────────────

async def handle_password_attempt(
    password_input: str,
    correct_password: str,
    tries_left: int,
    user_id: int,
    first_name: str,
    last_name: str,
    tg_nickname: str,
    language: str,
    blocked_ids: list[int],
) -> PasswordResult:
    """
    Validates a password attempt during user onboarding.

    Rules:
        - tries_left reaches 0 → block the user (insert into DB, add to runtime list)
        - password is wrong but tries remain → decrement counter
        - password is correct → return 'correct', admin will confirm the role

    Called from: handlers/common/unknown.py → check_password()
    After return: handler sends the appropriate Telegram reply based on result.status
    """
    tries_left -= 1

    if tries_left < 1:
        # Block user: persist to DB and add to the in-memory list so filters work immediately
        await insert_user(
            user_id=user_id,
            user_type='blocked',
            first_name=first_name,
            last_name=last_name,
            tg_nickname=tg_nickname,
            language=language,
        )
        blocked_ids.append(user_id)
        logger.info(f"USER-{user_id} BLOCKED after exhausting password attempts")
        return PasswordResult(status='blocked')

    if password_input.strip() != correct_password:
        return PasswordResult(status='wrong', tries_left=tries_left)

    return PasswordResult(status='correct')


async def register_new_user(
    user_id: int,
    user_type: str,
    first_name: str,
    last_name: str,
    tg_nickname: str,
    language: str,
    role_lists: dict[str, list[int]],
) -> RegistrationResult:
    """
    Completes user registration after admin approval.

    Inserts the user into the DB and adds their ID to the correct in-memory role list
    so role filters (filters/role_filters.py) work immediately without a restart.

    Called from: handlers/roles/admin/handlers.py → complete_new_user()
    After return: handler sends a welcome message with the role's help text.

    :param role_lists: Dict of in-memory role lists from workflow_data,
                       e.g. {'role_a_ids': [...], 'role_b_ids': [...]}
    """
    success = await insert_user(
        user_id=user_id,
        user_type=user_type,
        first_name=first_name,
        last_name=last_name,
        tg_nickname=tg_nickname,
        language=language,
    )

    if success:
        # Add to the in-memory list for the correct role
        role_key = f"{user_type}_ids"
        if role_key in role_lists:
            role_lists[role_key].append(user_id)
            logger.info(f"USER-{user_id} added to in-memory {role_key}")

    return RegistrationResult(success=success, user_type=user_type if success else None)


# ── TODO: project-specific — add service functions for your domain ────
#
# PATTERN for a new service function:
#
#   async def do_something(input_data, ...) -> SomeResult:
#       # 1. Apply business rules / validation
#       # 2. Call one or more db/* functions
#       # 3. Return a result object (not a string, not a Telegram message)
#
# WHAT BELONGS HERE vs. IN DB:
#   db/   → "Give me rows WHERE x = y"   (pure SQL, no rules)
#   here  → "Should x be allowed to do y? If yes, update z and notify w"
