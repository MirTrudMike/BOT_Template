"""
storage/json_store.py — JSON file persistence utilities.

USE THIS FOR:
    Lightweight state that doesn't belong in PostgreSQL:
    - Sync timestamps (e.g. 'last time we pushed to Google Sheets')
    - Simple config overrides that need to survive restarts
    - Small lists (e.g. names excluded from a report)

DO NOT USE THIS FOR:
    - User data or anything relational → use db/ instead
    - Large datasets → use the DB
    - Secrets → use .env

All files live in the storage/ directory by convention.
"""

import json
import os
from datetime import datetime
from loguru import logger

STORAGE_DIR = os.path.abspath('./storage')


def _path(filename: str) -> str:
    """Resolves a filename to an absolute path inside the storage directory."""
    return os.path.join(STORAGE_DIR, filename)


def read_json(filename: str):
    """
    Reads and returns the contents of a JSON file from the storage directory.

    :param filename: Filename only, e.g. 'last_sync.json'
    """
    try:
        with open(_path(filename), mode='r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"FAILED to read '{filename}': {e}")
        raise


def write_json(filename: str, data) -> None:
    """
    Writes data to a JSON file in the storage directory.

    :param filename: Filename only, e.g. 'last_sync.json'
    :param data: Any JSON-serializable value
    """
    try:
        with open(_path(filename), mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"FAILED to write '{filename}': {e}")
        raise


def read_timestamp(filename: str) -> datetime:
    """
    Reads a datetime from {'last_update': '<ISO-8601>'} in a JSON file.
    Used for incremental sync: 'only fetch records changed since last_update'.
    """
    data = read_json(filename)
    return datetime.fromisoformat(data['last_update'])


def write_timestamp(filename: str, dt: datetime) -> None:
    """Writes a datetime into {'last_update': '<ISO-8601>'} in a JSON file."""
    try:
        data = read_json(filename)
    except Exception:
        data = {}
    data['last_update'] = dt.isoformat()
    write_json(filename, data)


# TODO: project-specific — add typed wrappers for your specific files
#
# Example:
# def read_excluded_names() -> list[str]:
#     return read_json('excluded_names.json')
#
# def update_excluded_names(names: list[str]) -> None:
#     write_json('excluded_names.json', names)
