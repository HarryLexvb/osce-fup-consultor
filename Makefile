.PHONY: help build up down logs test test-cov format lint clean migrate shell

help:
	@echo "OSCE FUP RUC Consultor - Makefile Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build       - Build Docker containers"
	@echo "  make up          - Start services"
	@echo "  make down        - Stop services"
	@echo "  make logs        - View logs"
	@echo "  make test        - Run all tests"
	@echo "  make test-cov    - Run tests with coverage"
	@echo "  make format      - Format code with black and isort"
	@echo "  make lint        - Run linting checks"
	@echo "  make migrate     - Run database migrations"
	@echo "  make shell       - Open Django shell"
	@echo "  make clean       - Clean temporary files"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Application running at http://localhost:8000/"

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose run --rm web pytest -v

test-cov:
	docker-compose run --rm web pytest --cov=fup_consult --cov-report=html --cov-report=term

format:
	docker-compose run --rm web black .
	docker-compose run --rm web isort .

lint:
	docker-compose run --rm web flake8
	docker-compose run --rm web mypy fup_consult/

migrate:
	docker-compose run --rm web python manage.py migrate

shell:
	docker-compose run --rm web python manage.py shell

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "Cleaned temporary files"
