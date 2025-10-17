# Makefile для Softlex

.PHONY: help install test test-coverage test-unit test-integration lint format collectstatic clean

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости для разработки
	uv sync --extra dev

test: ## Запустить все тесты
	uv run pytest

test-coverage: ## Запустить тесты с покрытием кода
	uv run pytest --cov=softlex --cov-report=html --cov-report=term-missing --cov-fail-under=80

test-unit: ## Запустить только unit тесты
	uv run pytest -m unit

test-integration: ## Запустить только интеграционные тесты
	uv run pytest -m integration

lint: ## Запустить линтеры
	uv run flake8 softlex/
	uv run black --check softlex/
	uv run isort --check-only softlex/

format: ## Форматировать код
	uv run black softlex/
	uv run isort softlex/

collectstatic: ## Собрать статические файлы
	uv run python softlex/manage.py collectstatic --noinput

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

check: test-coverage lint ## Запустить все проверки