# Telegram Bot Template

Production-ready [aiogram 3](https://docs.aiogram.dev/) bot skeleton with role-based access, password-gated registration, i18n, PostgreSQL, Redis FSM, APScheduler, and structured logging — ready to clone and extend.

---

## Features

| Feature | Details |
|---|---|
| **Role system** | Admin + unlimited custom roles; in-memory ID lists for zero-latency filtering |
| **Registration flow** | Password gate → admin approval → role assignment (full FSM) |
| **i18n** | Per-user language; English base with fallback; add languages in one file |
| **PostgreSQL** | asyncpg connection pool; clean data-access layer in `db/` |
| **Redis FSM** | State persists across restarts |
| **Scheduler** | APScheduler cron jobs; injectable into handlers |
| **Logging** | Loguru; rotating files + auto-alert to admin on unhandled errors |
| **Group blocking** | Drops all group/channel updates by default (configurable whitelist) |

---

## Tech Stack

- Python 3.11–3.13
- [aiogram 3.15](https://github.com/aiogram/aiogram) — async Telegram framework
- [asyncpg](https://github.com/MagicStack/asyncpg) — PostgreSQL driver
- [Redis](https://redis.io/) — FSM state storage
- [APScheduler](https://apscheduler.readthedocs.io/) — background jobs
- [environs](https://github.com/sloria/environs) — `.env` loading
- [loguru](https://github.com/Delgan/loguru) — structured logging

---

## Architecture

```
Telegram update
  │
  ▼
GroupBlockerMiddleware   ← drop group / channel updates
  │
  ▼
LoggingMiddleware        ← log user_id + action
  │
  ▼
SchedulerMiddleware      ← inject `scheduler`
  │
  ▼
I18nMiddleware           ← inject `_()` translator bound to user's language
  │
  ▼
Role filter              ← IsAdmin / IsRoleA / IsBlocked / IsUnknown
  │
  ▼
Handler  →  Service  →  db/  →  PostgreSQL
         ←           ←
```

**Layer responsibilities:**

| Layer | Location | Does |
|---|---|---|
| Handlers | `handlers/` | Parse Telegram input, call services, send replies |
| Services | `services/` | Business logic, return typed result objects |
| Data access | `db/` | Raw SQL queries only; one file per table |
| Filters | `filters/` | Role membership checks against in-memory ID lists |
| Middlewares | `middlewares/` | Cross-cutting concerns (logging, i18n, group blocking) |

---

## Project Structure

```
BOT_Template/
├── bot/
│   ├── setup.py          # Wires all components together at startup
│   └── routers.py        # Registers all routers into the Dispatcher
├── config/
│   ├── settings.py       # Config dataclasses loaded from .env
│   ├── core.py           # Config singleton accessor
│   ├── logging.py        # Loguru sink setup
│   └── redis.py          # RedisStorage factory
├── db/
│   ├── pool.py           # asyncpg connection pool
│   ├── base.py           # Shared DB helpers
│   └── users.py          # users table queries
├── services/
│   ├── user_service.py   # Registration, password, role assignment
│   └── notification_service.py  # Broadcast and admin alerts
├── handlers/
│   ├── common/           # Error handler, blocked, registration FSM
│   └── roles/
│       ├── admin/        # Admin approval workflow
│       └── role_a/       # Template role (copy to add more roles)
├── filters/
│   ├── role_filters.py   # IsAdmin, IsRoleA, IsBlocked, IsUnknown
│   └── input_filters.py  # Input validation filters
├── middlewares/
│   ├── logging.py
│   ├── group_blocker.py
│   └── i18n.py
├── i18n/
│   ├── translator.py     # Translation engine with fallback
│   ├── en.py             # English strings (required base)
│   └── ru.py             # Russian overrides
├── keyboards/
│   ├── common.py         # create_inline_kb() factory
│   └── calendar.py       # Multi-selection and regular calendar widgets
├── functions/
│   ├── text.py           # Markdown escaping, text utils
│   └── menu.py           # Bot command menu builder
├── schedulers/
│   ├── jobs.py           # APScheduler job registrations
│   └── middleware.py     # Scheduler injection middleware
├── storage/
│   └── json_store.py     # Lightweight local JSON persistence
├── main.py               # Entry point
├── requirements.txt
├── schema.sql            # Database schema — run once at setup
├── .env.example          # Environment variable reference
└── Makefile              # Common dev commands
```

---

## Prerequisites

- Python 3.11–3.13 (**not** 3.14+ — dependencies not yet compatible)
- PostgreSQL 14+
- Redis 6+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

---

## Quick Start

### 1. Create a new bot from this template

**Via GitHub UI:** click **"Use this template"** → **"Create a new repository"** on the template repo page.

**Via GitHub CLI:**
```bash
gh repo create my-new-bot --template MirTrudMike/BOT_Template --private
git clone git@github.com:MirTrudMike/my-new-bot.git
cd my-new-bot
```

### 2. Install dependencies

```bash
make install        # creates venv/ and installs requirements.txt
```

> **Note:** if your default `python3` is 3.14+, specify a compatible interpreter:
> ```bash
> make install PYTHON3=python3.12
> # or install it first: sudo dnf install python3.12   (Fedora)
> #                       sudo apt install python3.12   (Debian/Ubuntu)
> ```

Or manually:
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
make setup          # copies .env.example → .env
```

Then open `.env` and fill in:

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | ✅ | Telegram bot token from @BotFather |
| `ADMIN_ID` | ✅ | Your Telegram numeric user ID |
| `BOT_PASSWORD` | ✅ | Password users must enter to register |
| `DB_DSN` | ✅ | `postgresql://user:pass@localhost:5432/dbname` |
| `REDIS_URL` | ✅ | `redis://localhost:6379/0` |
| `ALLOWED_GROUP_IDS` | ☐ | Comma-separated group IDs to allow (optional) |

### 4. Create the database

```bash
make db             # runs schema.sql against DB_DSN from .env
```

Or manually:
```bash
psql YOUR_DB_DSN -f schema.sql
```

### 5. Run

```bash
make run
```

---

## Customization Checklist

After creating a new bot from this template, work through these TODOs in order:

- [ ] **Rename roles** — replace `role_a` with your actual role names throughout `config/`, `filters/`, `handlers/roles/`, `db/users.py`
- [ ] **`config/settings.py`** — add fields to `Users` dataclass for each new role; add new config sections (e.g. Google Sheets, S3) to `Config`
- [ ] **`config/core.py`** — update `user_types` list with your role names
- [ ] **`db/users.py`** — update `user_types` in `fetch_all_user_ids_by_type()`; extend `INSERT`/`SELECT` columns if your schema differs
- [ ] **`schema.sql`** — extend `users` table with project-specific columns; add extra tables
- [ ] **`filters/role_filters.py`** — add `IsRoleB`, `IsRoleC`, etc. for each new role
- [ ] **`handlers/roles/admin/handlers.py`** — implement `complete_new_user()` with actual role assignment
- [ ] **`handlers/roles/role_a/`** — replace stub handlers with real features and FSM flows
- [ ] **`i18n/en.py`** — add all bot text keys
- [ ] **`i18n/ru.py`** — add Russian translations (or other languages)
- [ ] **`functions/menu.py`** — list actual bot commands
- [ ] **`services/user_service.py`** — add domain-specific business logic functions
- [ ] **`schedulers/jobs.py`** — register actual cron jobs
- [ ] **`requirements.txt`** — add project dependencies
- [ ] **`.env.example`** — add project-specific variables
- [ ] **`bot/setup.py`** — add new role ID lists to `workflow_data`

---

## How to Add a New Role

1. **Filter** — add `IsRoleB` in `filters/role_filters.py` (copy `IsRoleA` pattern)
2. **Config** — add `role_b_ids: list[int]` to `Users` dataclass in `config/settings.py`
3. **DB** — add `"role_b"` to `user_types` list in `db/users.py`
4. **Handlers** — copy `handlers/roles/role_a/` → `handlers/roles/role_b/`, apply `IsRoleB` filter
5. **Router** — register the new router in `bot/routers.py`
6. **workflow_data** — add `'role_b_ids': config.users.role_b_ids` in `bot/setup.py`
7. **Admin flow** — add the role option to admin's role-selection keyboard in `handlers/roles/admin/`

---

## How to Add a New Language

1. Create `i18n/xx.py` with `STRINGS = { ... }` (copy keys from `en.py`, override what differs)
2. In `bot/setup.py`:
   ```python
   from i18n import xx
   translator.register('xx', xx.STRINGS)
   ```

Missing keys automatically fall back to English.

---

## Logging

| File | Level | Rotation | Retention |
|---|---|---|---|
| `logging/logs.log` | INFO+ | 10 MB | 30 days |
| `logging/errors.log` | ERROR+ | 5 MB | 6 months |

Unhandled exceptions are automatically forwarded to the admin via Telegram.

---

## Publishing as a GitHub Template

1. Push the repo to GitHub
2. Go to **Settings → General → Template repository** → check the box
3. The **"Use this template"** button will appear on your repo page

From then on, every new bot starts with:
```bash
gh repo create my-bot --template MirTrudMike/BOT_Template --private
```
