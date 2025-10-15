#!/bin/bash

# Выход при любой ошибке
set -e

echo "Ожидание запуска базы данных..."

# Ожидание готовности PostgreSQL
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  echo "PostgreSQL не готов - ожидание..."
  sleep 2
done

echo "PostgreSQL готов!"

# Выполнение миграций
echo "Выполнение миграций..."
uv run python softlex/manage.py migrate --noinput

# Сбор статических файлов
echo "Сбор статических файлов..."
uv run python softlex/manage.py collectstatic --noinput

# Создание суперпользователя, если не существует
echo "Проверка суперпользователя..."
uv run python softlex/manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Создание суперпользователя...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Суперпользователь создан: admin/admin')
else:
    print('Суперпользователь уже существует')
"

echo "Запуск сервера..."

# Выполнение команды, переданной в аргументах
exec "$@"
