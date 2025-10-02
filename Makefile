# Makefile for OCPP Backend Project
# Provides convenient commands for development and linting

.PHONY: help install lint format type-check security test clean docker-build docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  install       Install dependencies and setup pre-commit hooks"
	@echo "  lint          Run all linting checks"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run mypy type checking"
	@echo "  security      Run bandit security checks"
	@echo "  test          Run all tests"
	@echo "  clean         Clean up cache files and temporary directories"
	@echo "  docker-build  Build Docker containers"
	@echo "  docker-up     Start Docker containers"
	@echo "  docker-down   Stop Docker containers"

# Installation and setup
install:
	pip install -r requirements.txt
	pre-commit install
	@echo "✅ Dependencies installed and pre-commit hooks setup"

# Linting commands
lint: format type-check security flake8 pylint
	@echo "✅ All linting checks completed"

format:
	@echo "🔧 Formatting code with black and isort..."
	black .
	isort .
	@echo "✅ Code formatting completed"

type-check:
	@echo "🔍 Running mypy type checking..."
	mypy .
	@echo "✅ Type checking completed"

security:
	@echo "🔒 Running bandit security checks..."
	bandit -r . -f json -o bandit-report.json || bandit -r .
	@echo "✅ Security checks completed"

flake8:
	@echo "📏 Running flake8 style checks..."
	flake8 .
	@echo "✅ Flake8 checks completed"

pylint:
	@echo "🔍 Running pylint code analysis..."
	pylint chargers/ ocpp_server/ || echo "⚠️  Pylint found issues (non-blocking)"

# Testing
test:
	@echo "🧪 Running tests..."
	pytest --cov=. --cov-report=html --cov-report=term
	@echo "✅ Tests completed"

test-async:
	@echo "🧪 Running async-specific tests..."
	pytest tests/test_async_services.py -v
	@echo "✅ Async tests completed"

# Django commands
django-check:
	@echo "🔍 Running Django system checks..."
	python manage.py check
	python manage.py makemigrations --check --dry-run
	@echo "✅ Django checks completed"

migrate:
	@echo "📊 Running database migrations..."
	python manage.py migrate
	@echo "✅ Migrations completed"

# Docker commands
docker-build:
	@echo "🐳 Building Docker containers..."
	docker-compose build
	@echo "✅ Docker build completed"

docker-up:
	@echo "🚀 Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Docker containers started"

docker-down:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down
	@echo "✅ Docker containers stopped"

docker-logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

# Cleanup
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "bandit-report.json" -delete
	@echo "✅ Cleanup completed"

# Development workflow
dev-setup: install migrate
	@echo "🎉 Development environment setup completed"

dev-check: lint django-check test
	@echo "🎉 All development checks passed"

# CI/CD simulation
ci: install lint django-check test security
	@echo "🎉 CI pipeline simulation completed"
