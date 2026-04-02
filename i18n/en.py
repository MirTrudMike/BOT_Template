"""
i18n/en.py — English strings (base / fallback language).

RULES:
    - This file MUST be complete. Every key used anywhere in the bot must exist here.
    - Other language files (ru.py, de.py, ...) only need to contain keys they translate.
      Missing keys automatically fall back to English.
    - Use {placeholder} syntax for dynamic values (Python str.format style).

TODO: project-specific — add all text keys your bot uses.
"""

STRINGS: dict[str, str] = {
    # ── Registration / onboarding (unknown users) ────────────────────
    'welcome':               'Hello! To get access, please enter the password provided to you:',
    'wrong_password':        'Wrong password. Attempts left: {tries}',
    'you_are_blocked':       'Too many wrong attempts. You are blocked.',
    'waiting_confirmation':  'Correct! Please wait while the admin confirms your access.',
    'still_waiting':         'Still waiting for admin approval...',
    'registration_approved': 'Your request has been approved! You now have access.',
    'registration_declined': 'Your registration request was declined.',

    # ── Admin panel ──────────────────────────────────────────────────
    'admin_welcome':              'Welcome, admin. Use the menu below.',
    'new_user_request':           (
        'NEW USER REGISTRATION REQUEST\n\n'
        'id: {user_id}\n'
        'tg_nick: @{tg_nickname}\n'
        'name: {first_name} {last_name}\n'
        'lang: {language}'
    ),
    'select_role_for_new_user':   'Select a role for the new user:',
    'new_user_declined':          'User request was declined.',
    'user_role_assigned':         'Role <b>{role}</b> has been assigned.',

    # ── Role labels (used as button text in role_selection_kb) ───────
    # These are the display names shown on the buttons.
    # The callback_data suffix is the role's internal name (e.g. 'role_a').
    # TODO: project-specific — replace with your actual role display names
    'role_a':                'Role A',
    'role_b':                'Role B',

    # ── role_a screens ───────────────────────────────────────────────
    # TODO: project-specific — replace with real screen text for role_a
    'role_a_welcome':         'Welcome! Use the menu to get started.',
    'action_one':             'Action One',
    'action_two':             'Action Two',
    'enter_step_one_value':   'Step 1: please enter the first value:',
    'enter_step_two_value':   'Step 2: please enter the second value:',
    'flow_summary':           'Summary:\nStep 1: {step_one}\nStep 2: {step_two}\n\nConfirm?',
    'action_saved':           'Saved successfully.',
    'action_cancelled':       'Action cancelled.',

    # ── Common UI ────────────────────────────────────────────────────
    'cancelled':              'Operation cancelled.',
    'unrecognized_input':     'Unrecognized command or input.',
    'confirm':                'Confirm',
    'cancel':                 'Cancel',
    'confirm_button':         'Confirm',
    'cancel_button':          'Cancel',
    'back_button':            'Back',

    # ── Bot commands menu ────────────────────────────────────────────
    'cmd_help':               'List of available commands',
    'cmd_exit':               'Cancel current operation',

    # TODO: project-specific — add keys for all your bot's messages
}
