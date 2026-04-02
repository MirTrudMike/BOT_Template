# Makefile — common development commands for the Telegram bot template.
# Usage: make <target>
#
# Python 3.11–3.13 is required. If your default python3 is 3.14+, override:
#   make install PYTHON3=python3.12

.PHONY: help install setup db run clean check-python

VENV    = venv
PYTHON  = $(VENV)/bin/python
PIP     = $(VENV)/bin/pip
PYTHON3 ?= python3

# Default target — print available commands
help:
	@echo ""
	@echo "  make install   create venv and install dependencies"
	@echo "  make setup     copy .env.example to .env (edit it afterwards)"
	@echo "  make db        create database tables (reads DB_DSN from .env)"
	@echo "  make run       start the bot"
	@echo "  make clean     remove venv and compiled Python files"
	@echo ""

# Verify Python version is 3.11–3.13
check-python:
	@$(PYTHON3) -c "\
import sys; v = sys.version_info[:2]; \
ok = (3,11) <= v <= (3,13); \
print(f'Python {v[0]}.{v[1]} — ' + ('OK' if ok else 'UNSUPPORTED')); \
exit(0 if ok else 1)" || \
	(echo ""; \
	 echo "ERROR: dependencies require Python 3.11–3.13."; \
	 echo "Your default python3 is too new (or too old)."; \
	 echo ""; \
	 echo "Fix: install python3.12 (e.g. sudo dnf install python3.12)"; \
	 echo "     then run: make install PYTHON3=python3.12"; \
	 echo ""; \
	 exit 1)

# Create virtual environment and install dependencies
install: check-python
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
