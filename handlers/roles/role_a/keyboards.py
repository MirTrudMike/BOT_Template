from keyboards.common import create_inline_kb

# ---------------------------------------------------------------------------
# TODO: project-specific — replace these stubs with real keyboards for role_a.
#
# Pattern:
#   - One function per screen / interaction point
#   - Accept `_` (translator) so button labels are translated automatically
#   - Use create_inline_kb() from keyboards/common.py for consistency
#   - callback_data keys must match the filters in role_a/handlers.py
# ---------------------------------------------------------------------------


def role_a_main_menu_kb(_):
    """
    Main menu keyboard shown to role_a users after /start.

    TODO: replace keys and labels with your actual menu items.
    """
    return create_inline_kb(
        1,
        role_a_action_one=_('action_one'),
        role_a_action_two=_('action_two'),
    )


def role_a_confirm_kb(_):
    """
    Generic confirm / cancel keyboard reused across role_a flows.

    DATA FLOW:
        handler shows this keyboard when it needs the user to confirm an action
        → user taps confirm → callback_data='role_a_confirm'
        → handler in role_a/handlers.py catches it and proceeds
    """
    return create_inline_kb(
        2,                              # two buttons per row
        role_a_confirm=_('confirm'),
        role_a_cancel=_('cancel'),
    )
