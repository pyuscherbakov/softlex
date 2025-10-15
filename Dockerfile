# Используем официальный Python образ
FROM python:3.13-slim

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем uv для управления зависимостями
RUN pip install uv

# Устанавливаем зависимости Python
RUN uv sync --frozen

# Копируем исходный код
COPY . .

# Создаем пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Создаем директории для статических файлов и медиа
RUN mkdir -p /app/staticfiles /app/media

# Делаем entrypoint исполняемым
RUN chmod +x /app/entrypoint.sh

# Открываем порт
EXPOSE 8000

# Устанавливаем entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Команда по умолчанию
CMD ["uv", "run", "python", "softlex/manage.py", "runserver", "0.0.0.0:8000"]
