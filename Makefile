# Makefile — common development commands for the Telegram bot template.
# Usage: make <target>

.PHONY: help install setup db run clean

VENV   = venv
PYTHON = $(VENV)/bin/python
PIP    = $(VENV)/bin/pip

# Auto-detect a compatible Python (3.11–3.13). Tries python3.12, python3.13,
# python3.11, then python3. Fails with a clear message if none qualify.
PYTHON3 := $(shell \
  for cmd in python3.12 python3.13 python3.11 python3; do \
    bin=$$(command -v $$cmd 2>/dev/null) || continue; \
    ok=$$($$bin -c "import sys; v=sys.version_info[:2]; print('ok' if (3,11)<=v<=(3,13) else '')" 2>/dev/null); \
    [ "$$ok" = "ok" ] && echo $$bin && break; \
  done)

# Default target — print available commands
help:
	@echo ""
	@echo "  make install   create venv and install dependencies"
	@echo "  make setup     copy .env.example to .env (edit it afterwards)"
	@echo "  make db        create database tables (reads DB_DSN from .env)"
	@echo "  make run       start the bot"
	@echo "  make clean     remove venv and compiled Python files"
	@echo ""

# Create virtual environment and install dependencies
install:
	@if [ -z "$(PYTHON3)" ]; then \
	  echo ""; \
	  echo "ERROR: no compatible Python found (need 3.11–3.13)."; \
	  echo "Install one, e.g.:  sudo dnf install python3.12"; \
	  echo ""; \
	  exit 1; \
	fi
	@echo "Using $(PYTHON3)"
	$(PYTHON3) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Copy .env.example to .env if it does not exist yet
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env created — open it and fill in your values"; \
	else \
		echo ".env already exists — skipping"; \
	fi

# Apply schema.sql to the database (reads DB_DSN from .env)
db:
	@if [ ! -f .env ]; then echo "Error: .env not found. Run 'make setup' first."; exit 1; fi
	@export $$(grep -v '^[[:space:]]*#' .env | grep -v '^[[:space:]]*$$' | xargs) && \
		psql "$$DB_DSN" -f schema.sql && \
		echo "schema.sql applied successfully"

# Run the bot
run:
	$(PYTHON) main.py

# Remove venv and compiled Python files
clean:
	rm -rf $(VENV) __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
