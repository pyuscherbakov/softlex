# Тесты Softlex

Эта папка содержит все тесты для проекта Softlex, организованные по объектам тестирования.

## Структура

```
tests/
├── conftest.py              # Pytest конфигурация и фикстуры
├── pytest.ini              # Настройки pytest
├── users/                   # Тесты пользователей
│   ├── test_user_models.py  # Тесты модели User
│   ├── test_user_forms.py   # Тесты форм пользователей
│   └── test_user_views.py   # Тесты представлений пользователей
├── testcases/               # Тесты тест-кейсов
│   ├── test_project_models.py # Тесты моделей проектов
│   ├── test_project_forms.py  # Тесты форм проектов
│   ├── test_project_views.py  # Тесты представлений проектов
│   └── test_utils.py        # Тесты утилит
├── integration/             # Интеграционные тесты
│   └── test_workflows.py    # Тесты пользовательских сценариев
└── utils/                   # Вспомогательные тесты
    └── test_mixins.py       # Тесты миксинов
```

## Запуск тестов

```bash
# Все тесты
make test

# С покрытием кода
make test-coverage

# Только unit тесты
make test-unit

# Только интеграционные тесты
make test-integration

# Линтеры
make lint

# Форматирование кода
make format
```

## Установка зависимостей

```bash
# Установка через UV
make install

# Или напрямую
uv sync --extra dev
```
