.PHONY: help setup setup-dev clean test test-cov lint fmt type-check security build dev migrate migrate-auto seed docker-build docker-up docker-down deploy

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup and Installation
setup: ## Install production dependencies using uv
	@echo "🔧 Installing production dependencies with uv..."
	uv pip install -e .

setup-dev: ## Install all dependencies including development tools
	@echo "🔧 Installing all dependencies with uv..."
	uv pip install -e ".[dev,lint,security]"

clean: ## Clean up cache and temporary files
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/

# Development
dev: ## Start development server
	@echo "🚀 Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-debug: ## Start development server with debug logging
	@echo "🐛 Starting development server with debug logging..."
	DEBUG=true uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# Testing
test: ## Run tests
	@echo "🧪 Running tests..."
	pytest

test-cov: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	pytest --cov=app --cov-report=html --cov-report=term-missing

test-fast: ## Run tests excluding slow tests
	@echo "⚡ Running fast tests..."
	pytest -m "not slow"

test-integration: ## Run only integration tests
	@echo "🔧 Running integration tests..."
	pytest -m integration

test-unit: ## Run only unit tests
	@echo "🎯 Running unit tests..."
	pytest -m unit

# Code Quality
lint: ## Run all linting tools
	@echo "🔍 Running linting tools..."
	ruff check .
	black --check .
	mypy .

fmt: ## Format code
	@echo "🎨 Formatting code..."
	black .
	ruff check . --fix

type-check: ## Run type checking
	@echo "🔍 Running type check..."
	mypy .

security: ## Run security checks
	@echo "🔒 Running security checks..."
	safety check
	bandit -r app/ -f json

# Database
migrate: ## Run database migrations
	@echo "📊 Running database migrations..."
	alembic upgrade head

migrate-auto: ## Generate automatic migration
	@echo "📊 Generating automatic migration..."
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

migrate-create: ## Create empty migration
	@echo "📊 Creating empty migration..."
	@read -p "Enter migration message: " message; \
	alembic revision -m "$$message"

migrate-history: ## Show migration history
	@echo "📊 Migration history..."
	alembic history

migrate-current: ## Show current migration
	@echo "📊 Current migration..."
	alembic current

migrate-rollback: ## Rollback one migration
	@echo "📊 Rolling back one migration..."
	alembic downgrade -1

seed: ## Seed database with initial data
	@echo "🌱 Seeding database..."
	python -m scripts.seed_data

# Docker
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t fastapi-ddd-template .

docker-up: ## Start services with docker-compose
	@echo "🐳 Starting services..."
	docker-compose up -d

docker-down: ## Stop services with docker-compose
	@echo "🐳 Stopping services..."
	docker-compose down

docker-logs: ## Show docker-compose logs
	@echo "📋 Showing logs..."
	docker-compose logs -f

docker-shell: ## Get shell in running container
	@echo "🐚 Opening shell in container..."
	docker-compose exec app bash

# Production
build: ## Build production assets
	@echo "🏗️ Building production assets..."
	docker build -t fastapi-ddd-template:latest .

deploy: ## Deploy to production (placeholder)
	@echo "🚀 Deploying to production..."
	@echo "Implement your deployment logic here"

# Utilities
install-uv: ## Install uv package manager
	@echo "📦 Installing uv..."
	curl -LsSf https://astral.sh/uv/install.sh | sh

check-env: ## Check if required environment variables are set
	@echo "🔍 Checking environment variables..."
	@python -c "from app.core.config import settings; print('✅ Environment configuration is valid')"

generate-secret: ## Generate a new secret key
	@echo "🔑 Generating secret key..."
	@python -c "import secrets; print(f'SECRET_KEY={secrets.token_urlsafe(32)}')"

# CI/CD helpers
ci-setup: ## Setup for CI environment
	pip install uv
	make setup-dev

ci-test: ## Run tests in CI environment
	make lint
	make security
	make test-cov

# Local development helpers
dev-db: ## Start only database service
	@echo "🗄️ Starting database..."
	docker-compose up -d postgres redis

dev-stop: ## Stop development services
	@echo "🛑 Stopping development services..."
	docker-compose down

reset-db: ## Reset database (WARNING: destructive)
	@echo "⚠️ Resetting database..."
	@read -p "Are you sure? This will delete all data. (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		sleep 5; \
		make migrate; \
		make seed; \
	else \
		echo "Cancelled."; \
	fi