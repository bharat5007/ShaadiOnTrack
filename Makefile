.PHONY: setup activate run clean help lint format check

# Default Python version
PYTHON := python3.9
VENV := .venv
ACTIVATE := . $(VENV)/bin/activate

help:
	@echo "📚 Wedding Core Service - Makefile Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup     - Create virtual environment and install all requirements"
	@echo "  make activate  - Show command to activate virtual environment"
	@echo "  make run       - Run the FastAPI application"
	@echo "  make dev       - Setup + Run (convenience command)"
	@echo "  make tables    - Create database tables"
	@echo "  make test-db   - Test database connection"
	@echo "  make lint      - Run ruff linter"
	@echo "  make format    - Format code with ruff"
	@echo "  make check     - Run lint + format check"
	@echo "  make clean     - Remove virtual environment and cache files"
	@echo ""

setup:
	@echo "🔧 Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo ""
	@echo "📦 Installing requirements..."
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -r requirements.txt
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "⚠️  Next steps:"
	@echo "   1. Run 'make activate' to see activation command"
	@echo "   2. Ensure PostgreSQL is running"
	@echo "   3. Create database: createdb wedding_db"
	@echo "   4. Run 'make tables' to create tables"
	@echo "   5. Run 'make run' to start the server"
	@echo ""

activate:
	@echo "To activate the virtual environment, run:"
	@echo ""
	@echo "    source $(VENV)/bin/activate"
	@echo ""

run:
	@echo "🚀 Starting Wedding Core Service..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if [ ! -f ".env" ]; then \
		echo "❌ .env file not found. Copy .env.example to .env and configure it."; \
		exit 1; \
	fi
	@echo ""
	$(ACTIVATE) && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev: setup
	@echo ""
	@echo "🎯 Running development server..."
	@sleep 2
	@$(MAKE) run

tables:
	@echo "🔨 Creating database tables..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(ACTIVATE) && python -m app.create_tables
	@echo ""

test-db:
	@echo "🔍 Testing database connection..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(ACTIVATE) && python test_db.py || echo "⚠️  test_db.py not found or failed"
	@echo ""

lint:
	@echo "🔍 Running ruff linter..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(ACTIVATE) && ruff check app/
	@echo ""

format:
	@echo "✨ Formatting code with ruff..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(ACTIVATE) && ruff format app/
	@echo "✅ Code formatted!"
	@echo ""

check: lint
	@echo "🔍 Running format check..."
	$(ACTIVATE) && ruff format --check app/
	@echo "✅ All checks passed!"
	@echo ""

clean:
	@echo "🧹 Cleaning up..."
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Convenience commands
install: setup
	@echo "✅ Installation complete"

start: run
	@echo "Server stopped"

restart:
	@echo "🔄 Restarting server..."
	@pkill -f "uvicorn app.main:app" || true
	@sleep 1
	@$(MAKE) run