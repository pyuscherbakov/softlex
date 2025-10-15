#!/usr/bin/env python
"""
Скрипт для экспорта данных из SQLite в JSON файлы для последующего импорта в PostgreSQL.

Использование:
    python export_data.py

Создаст файлы:
    - data_fixtures.json - основные данные приложения
    - data_users.json - пользователи (отдельно для безопасности)
"""

import os
import sys
import django
import json
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'softlex'))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'softlex.settings')
django.setup()

from django.core.management import call_command
from django.core import serializers
from io import StringIO


def export_data():
    """Экспорт данных из SQLite в JSON файлы."""
    
    print("Начинаем экспорт данных из SQLite...")
    
    # Временно переключаемся на SQLite для экспорта
    from django.conf import settings
    original_databases = settings.DATABASES.copy()
    
    # Устанавливаем SQLite для экспорта
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': project_root / 'softlex' / 'db.sqlite3',
        }
    }
    
    try:
        # Экспорт всех данных приложения (кроме пользователей)
        print("Экспорт данных приложения...")
        call_command('dumpdata', 
                    'testcases', 
                    'contenttypes', 
                    'sessions',
                    'admin',
                    'auth.permission',
                    'auth.group',
                    output='data_fixtures.json',
                    indent=2)
        
        # Экспорт пользователей отдельно
        print("Экспорт пользователей...")
        call_command('dumpdata', 
                    'users.user',
                    'auth.user',
                    output='data_users.json',
                    indent=2)
        
        print("✅ Экспорт завершен!")
        print("Созданы файлы:")
        print("  - data_fixtures.json - основные данные приложения")
        print("  - data_users.json - пользователи")
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
        return False
    
    finally:
        # Восстанавливаем оригинальные настройки БД
        settings.DATABASES = original_databases
    
    return True


def check_sqlite_exists():
    """Проверка существования SQLite файла."""
    sqlite_path = project_root / 'softlex' / 'db.sqlite3'
    if not sqlite_path.exists():
        print(f"❌ Файл SQLite не найден: {sqlite_path}")
        print("Убедитесь, что у вас есть данные в SQLite для экспорта.")
        return False
    return True


if __name__ == '__main__':
    print("=== Экспорт данных из SQLite в PostgreSQL ===")
    
    if not check_sqlite_exists():
        sys.exit(1)
    
    if export_data():
        print("\n🎉 Экспорт успешно завершен!")
        print("\nСледующие шаги:")
        print("1. Запустите PostgreSQL: make up")
        print("2. Импортируйте данные: python import_data.py")
    else:
        print("\n❌ Экспорт завершился с ошибками")
        sys.exit(1)
