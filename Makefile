# Makefile для управления проектом softlex

.PHONY: help build up down logs shell migrate createsuperuser clean restart test

# Показать справку
help:
	@echo "Доступные команды:"
	@echo "  build           - Собрать Docker образы"
	@echo "  up              - Запустить все сервисы"
	@echo "  down            - Остановить все сервисы"
	@echo "  restart         - Перезапустить сервисы"
	@echo "  logs            - Показать логи всех сервисов"
	@echo "  logs-web        - Показать логи веб-сервиса"
	@echo "  logs-db         - Показать логи базы данных"
	@echo "  shell           - Подключиться к контейнеру веб-сервиса"
	@echo "  shell-db        - Подключиться к контейнеру базы данных"
	@echo "  migrate         - Выполнить миграции базы данных"
	@echo "  createsuperuser - Создать суперпользователя"
	@echo "  test            - Запустить тесты"
	@echo "  clean           - Очистить контейнеры и volumes"
	@echo "  clean-all       - Полная очистка (включая образы)"
	@echo "  status          - Показать статус сервисов"

# Собрать образы
build:
	docker-compose build

# Запустить сервисы
up:
	docker-compose up -d

# Запустить сервисы в foreground режиме
up-fg:
	docker-compose up

# Остановить сервисы
down:
	docker-compose down

# Перезапустить сервисы
restart: down up

# Показать логи всех сервисов
logs:
	docker-compose logs -f

# Показать логи веб-сервиса
logs-web:
	docker-compose logs -f web

# Показать логи базы данных
logs-db:
	docker-compose logs -f db

# Подключиться к контейнеру веб-сервиса
shell:
	docker-compose exec web bash

# Подключиться к контейнеру базы данных
shell-db:
	docker-compose exec db psql -U admin -d sftlx

# Выполнить миграции
migrate:
	docker-compose exec web uv run python softlex/manage.py migrate

# Создать суперпользователя
createsuperuser:
	docker-compose exec web uv run python softlex/manage.py createsuperuser

# Запустить тесты
test:
	docker-compose exec web uv run python softlex/manage.py test

# Показать статус сервисов
status:
	docker-compose ps

# Очистить контейнеры и volumes
clean:
	docker-compose down -v
	docker system prune -f

# Полная очистка (включая образы)
clean-all: clean
	docker-compose down --rmi all -v
	docker system prune -af

# Создать .env файл из примера
setup:
	cp env.example .env
	@echo "Файл .env создан. Отредактируйте его при необходимости."

# Быстрый старт (создать .env и запустить)
start: setup up
	@echo "Проект запущен! Доступен по адресу: http://localhost:8000"
