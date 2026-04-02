from keyboards.common import create_inline_kb

# ---------------------------------------------------------------------------
# Role selection keyboard
# ---------------------------------------------------------------------------
# Used when admin approves a new user and needs to assign them a role.
# Each button callback_data key must be handled in admin/handlers.py.
#
# DATA FLOW:
#   admin presses CONFIRM on new-user notification
#   → admin_handler enters AdminNewUserFSM.select_role
#   → bot sends this keyboard
#   → admin taps a role button
#   → callback_data hits the role-assignment handler in admin/handlers.py
#   → service assigns the role → DB → new user notified
# ---------------------------------------------------------------------------

def role_selection_kb(_):
    """
    Build a role-selection inline keyboard.

    :param _: bound translator function injected by I18nMiddleware
    :return: InlineKeyboardMarkup

    Buttons are built from the common factory so the layout stays consistent.
    Keys must match what the role-assignment callback handler filters on.

    TODO: project-specific — replace role_a / role_b with your actual roles.
    The text values should be lexicon keys so they translate automatically.
    """
    return create_inline_kb(
        1,                          # one button per row
        assign_role_a=_('role_a'),  # callback_data='assign_role_a'
        assign_role_b=_('role_b'),  # callback_data='assign_role_b'
    )


# ---------------------------------------------------------------------------
# Admin main-menu keyboard
# ---------------------------------------------------------------------------
# Shown after /start for admin users.
# Add more admin-specific shortcuts here as the project grows.
# ---------------------------------------------------------------------------

def admin_main_menu_kb(_):
    """
    TODO: project-specific — build the admin main-menu keyboard.

    Example:
        return create_inline_kb(
            1,
            admin_users=_('manage_users'),
            admin_broadcast=_('send_broadcast'),
        )
    """
    raise NotImplementedError("Build your admin main-menu keyboard here.")
