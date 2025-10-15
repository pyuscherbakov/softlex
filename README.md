# softlex
A simple and reliable open source test management system.

## Требования

- Docker и Docker Compose
- Python 3.13+ (для локальной разработки)
- PostgreSQL 16 (если не используете Docker)

## Запуск проекта

### Docker Compose (рекомендуется)

#### Быстрый старт
```bash
# Клонировать репозиторий
git clone <repository-url>
cd softlex

# Настроить переменные окружения
cp env.example .env

# Запустить проект
make up
```

Проект будет доступен по адресу: http://localhost:8000

#### Доступные команды
```bash
make help          # Показать все доступные команды
make build         # Собрать Docker образы
make up            # Запустить все сервисы
make down          # Остановить все сервисы
make restart       # Перезапустить сервисы
make logs          # Показать логи всех сервисов
make logs-web      # Показать логи веб-сервиса
make logs-db       # Показать логи базы данных
make shell         # Подключиться к контейнеру веб-сервиса
make shell-db      # Подключиться к контейнеру базы данных
make migrate       # Выполнить миграции
make createsuperuser # Создать суперпользователя
make test          # Запустить тесты
make clean         # Очистить контейнеры и volumes
make status        # Показать статус сервисов
```

#### Структура Docker Compose
- **web** - Django приложение (порт 8000)
- **db** - PostgreSQL 16 база данных (порт 5432)

#### Переменные окружения
Скопируйте `env.example` в `.env` и настройте под свои нужды:
```bash
cp env.example .env
```

Основные переменные:
- `DEBUG` - режим отладки (True/False)
- `SECRET_KEY` - секретный ключ Django
- `POSTGRES_DB` - имя базы данных
- `POSTGRES_USER` - пользователь базы данных
- `POSTGRES_PASSWORD` - пароль базы данных
- `ALLOWED_HOSTS` - разрешенные хосты

### Локальная разработка

Если вы хотите запускать проект локально без Docker:

```bash
# Установить зависимости
uv sync

# Настроить переменные окружения
cp env.example .env
# Отредактируйте .env для подключения к локальной PostgreSQL

# Выполнить миграции
uv run python softlex/manage.py migrate

# Создать суперпользователя
uv run python softlex/manage.py createsuperuser

# Запустить сервер
uv run python softlex/manage.py runserver
```

## Миграция данных из SQLite в PostgreSQL

Если у вас есть существующие данные в SQLite, вы можете перенести их в PostgreSQL:

### 1. Экспорт данных из SQLite
```bash
python export_data.py
```

Это создаст файлы:
- `data_fixtures.json` - основные данные приложения
- `data_users.json` - пользователи

### 2. Запуск PostgreSQL
```bash
make up
```

### 3. Импорт данных в PostgreSQL
```bash
python import_data.py
```

Скрипт автоматически:
- Проверит подключение к PostgreSQL
- Импортирует все данные
- Покажет статистику импортированных данных
- Предложит удалить временные файлы

## Разработка

### Структура проекта
```
softlex/
├── Dockerfile              # Docker образ для приложения
├── docker-compose.yml      # Конфигурация Docker Compose
├── Makefile               # Команды для управления проектом
├── entrypoint.sh          # Скрипт запуска контейнера
├── export_data.py         # Экспорт данных из SQLite
├── import_data.py         # Импорт данных в PostgreSQL
├── env.example            # Пример переменных окружения
├── softlex/               # Django проект
│   ├── manage.py
│   ├── softlex/          # Настройки Django
│   ├── users/            # Приложение пользователей
│   ├── testcases/        # Приложение тест-кейсов
│   ├── templates/        # HTML шаблоны
│   └── static/           # Статические файлы
└── README.md
```

### Полезные команды для разработки

```bash
# Просмотр логов в реальном времени
make logs

# Подключение к контейнеру для отладки
make shell

# Выполнение Django команд
make shell
# Внутри контейнера:
uv run python softlex/manage.py shell
uv run python softlex/manage.py dbshell

# Перезапуск после изменений в коде
make restart

# Очистка и пересборка
make clean
make build
make up
```

## Стек технологий

1. **Backend**: Django 5.2.6
2. **База данных**: PostgreSQL 16
3. **Контейнеризация**: Docker, Docker Compose
4. **Управление зависимостями**: uv
5. **Frontend**: HTML, CSS, HTMX
6. **ORM**: Django ORM

# Функциональность
1. Авторизация
2. Регистрация
3. Права доступа
   1. Администратор
   2. Пользователь
   3. Заблокированный пользователь
4. Библиотека тест-кейсов
   1. Разделение на секции/папки
   2. Создание тест-кейсов
   3. Удаление тест-кейсов
   4. Обновление тест-кейсов
   5. Перемещение тест-кейсов
   6. Экспорт всех тест-кейсов в exel
5. Проекты. Сущность, к которой привязываются тест-кейсы.
   1. Создание
   2. Обновление
   3. Удаление