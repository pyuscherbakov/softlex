#!/usr/bin/env python
"""
Скрипт для импорта данных из JSON файлов в PostgreSQL.

Использование:
    python import_data.py

Импортирует файлы:
    - data_fixtures.json - основные данные приложения
    - data_users.json - пользователи
"""

import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'softlex'))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'softlex.settings')
django.setup()

from django.core.management import call_command
from django.db import connection


def check_postgres_connection():
    """Проверка подключения к PostgreSQL."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Подключение к PostgreSQL успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        print("Убедитесь, что PostgreSQL запущен: make up")
        return False


def check_fixture_files():
    """Проверка существования файлов с данными."""
    files = ['data_fixtures.json', 'data_users.json']
    missing_files = []
    
    for file in files:
        if not (project_root / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Не найдены файлы: {', '.join(missing_files)}")
        print("Сначала выполните экспорт: python export_data.py")
        return False
    
    print("✅ Файлы с данными найдены")
    return True


def import_data():
    """Импорт данных в PostgreSQL."""
    
    print("Начинаем импорт данных в PostgreSQL...")
    
    try:
        # Сначала импортируем основные данные
        print("Импорт основных данных...")
        call_command('loaddata', 'data_fixtures.json')
        
        # Затем импортируем пользователей
        print("Импорт пользователей...")
        call_command('loaddata', 'data_users.json')
        
        print("✅ Импорт завершен!")
        
        # Показываем статистику
        show_import_stats()
        
    except Exception as e:
        print(f"❌ Ошибка при импорте: {e}")
        return False
    
    return True


def show_import_stats():
    """Показать статистику импортированных данных."""
    from django.contrib.auth import get_user_model
    from testcases.models import Project, TestCase
    
    User = get_user_model()
    
    print("\n📊 Статистика импортированных данных:")
    print(f"  - Пользователей: {User.objects.count()}")
    print(f"  - Проектов: {Project.objects.count()}")
    print(f"  - Тест-кейсов: {TestCase.objects.count()}")
    
    # Показываем суперпользователей
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        print(f"  - Суперпользователей: {superusers.count()}")
        for user in superusers:
            print(f"    * {user.username} ({user.email})")


def clean_fixture_files():
    """Удаление временных файлов с данными."""
    files = ['data_fixtures.json', 'data_users.json']
    
    for file in files:
        file_path = project_root / file
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️  Удален файл: {file}")


if __name__ == '__main__':
    print("=== Импорт данных в PostgreSQL ===")
    
    if not check_postgres_connection():
        sys.exit(1)
    
    if not check_fixture_files():
        sys.exit(1)
    
    if import_data():
        print("\n🎉 Импорт успешно завершен!")
        
        # Спрашиваем, нужно ли удалить временные файлы
        response = input("\nУдалить временные файлы с данными? (y/N): ").strip().lower()
        if response in ['y', 'yes', 'да']:
            clean_fixture_files()
        
        print("\nПроект готов к использованию!")
        print("Доступен по адресу: http://localhost:8000")
    else:
        print("\n❌ Импорт завершился с ошибками")
        sys.exit(1)
