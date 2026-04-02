"""
i18n/ru.py — Russian strings.

Only keys that differ from en.py need to be listed here.
Any key missing here will automatically fall back to English.
"""

STRINGS: dict[str, str] = {
    # ── Registration / onboarding (unknown users) ────────────────────
    'welcome':               'Привет! Для получения доступа введи пароль, который тебе выдали:',
    'wrong_password':        'Неверный пароль. Осталось попыток: {tries}',
    'you_are_blocked':       'Слишком много неверных попыток. Ты заблокирован.',
    'waiting_confirmation':  'Верно! Подожди, пока админ подтвердит твой доступ.',
    'still_waiting':         'Всё ещё ждём подтверждения от администратора...',
    'registration_approved': 'Твоя заявка одобрена! Теперь у тебя есть доступ.',
    'registration_declined': 'Твоя заявка на регистрацию была отклонена.',

    # ── Admin panel ──────────────────────────────────────────────────
    'admin_welcome':              'Добро пожаловать, администратор.',
    'select_role_for_new_user':   'Выбери роль для нового пользователя:',
    'new_user_declined':          'Заявка пользователя отклонена.',
    'user_role_assigned':         'Роль <b>{role}</b> назначена.',

    # ── Role labels ──────────────────────────────────────────────────
    # TODO: project-specific — replace with your actual role display names
    'role_a':                'Роль А',
    'role_b':                'Роль Б',

    # ── role_a screens ───────────────────────────────────────────────
    # TODO: project-specific — replace with real screen text for role_a
    'role_a_welcome':         'Добро пожаловать! Используй меню для начала работы.',
    'action_one':             'Действие первое',
    'action_two':             'Действие второе',
    'enter_step_one_value':   'Шаг 1: введи первое значение:',
    'enter_step_two_value':   'Шаг 2: введи второе значение:',
    'flow_summary':           'Итог:\nШаг 1: {step_one}\nШаг 2: {step_two}\n\nПодтвердить?',
    'action_saved':           'Успешно сохранено.',
    'action_cancelled':       'Действие отменено.',

    # ── Common UI ────────────────────────────────────────────────────
    'cancelled':              'Операция отменена.',
    'unrecognized_input':     'Нераспознанная команда или ввод.',
    'confirm':                'Подтвердить',
    'cancel':                 'Отмена',
    'confirm_button':         'Подтвердить',
    'cancel_button':          'Отмена',
    'back_button':            'Назад',

    # ── Bot commands menu ────────────────────────────────────────────
    'cmd_help':               'Список доступных команд',
    'cmd_exit':               'Прервать текущую операцию',

    # TODO: project-specific — add Russian translations for your keys
}
