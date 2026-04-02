from concurrent.futures import ThreadPoolExecutor
from config.settings import load_config, Config

# Config singleton — import anywhere as: from config.core import config
config: Config = load_config()

# ThreadPoolExecutor for running sync operations in async context (e.g. Google Sheets API)
executor = ThreadPoolExecutor(max_workers=5)

# TODO: project-specific — list all user role type strings for your bot.
# Used when loading IDs from DB and in admin user-management handlers.
user_types: list[str] = [
    # "role_a",
    # "role_b",
    # "blocked",
]
