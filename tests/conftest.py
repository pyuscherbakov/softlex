"""
Pytest конфигурация и фикстуры для Softlex
"""
import pytest
import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.test.utils import setup_test_environment, teardown_test_environment
from django.conf import settings

# Добавляем корневую папку проекта в Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Настройка Django для pytest
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'softlex.test_settings')

# Инициализация Django
django.setup()

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Настройка базы данных для всех тестов"""
    with django_db_blocker.unblock():
        call_command('migrate', verbosity=0, interactive=False)


@pytest.fixture
def db_access_without_rollback_and_truncate(request, django_db_setup, django_db_blocker):
    """Фикстура для доступа к БД без отката транзакций"""
    django_db_blocker.unblock()
    request.addfinalizer(django_db_blocker.block)


@pytest.fixture
def user_data():
    """Данные для создания пользователя"""
    return {
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Тест',
        'last_name': 'Пользователь',
        'role': 'user'
    }


@pytest.fixture
def admin_data():
    """Данные для создания администратора"""
    return {
        'email': 'admin@example.com',
        'password': 'adminpass123',
        'first_name': 'Админ',
        'last_name': 'Системы',
        'role': 'admin'
    }


@pytest.fixture
def user(user_data):
    """Создает обычного пользователя"""
    return User.objects.create_user(**user_data)


@pytest.fixture
def admin(admin_data):
    """Создает администратора"""
    return User.objects.create_superuser(**admin_data)


@pytest.fixture
def inactive_user():
    """Создает неактивного пользователя"""
    return User.objects.create_user(
        email='inactive@example.com',
        password='testpass123',
        is_active=False
    )


@pytest.fixture
def project_data():
    """Данные для создания проекта"""
    return {
        'name': 'Тестовый проект',
        'description': 'Описание тестового проекта'
    }


@pytest.fixture
def project(user, project_data):
    """Создает проект"""
    from softlex.testcases.models import Project
    return Project.objects.create(
        created_by=user,
        **project_data
    )


@pytest.fixture
def testcase_data():
    """Данные для создания тест-кейса"""
    return {
        'title': 'Тестовый кейс',
        'description': 'Описание тестового кейса',
        'preconditions': 'Предусловия',
        'steps': '1. Открыть приложение\n2. Ввести данные\n3. Нажать кнопку',
        'expected_result': 'Ожидаемый результат'
    }


@pytest.fixture
def testcase(user, project, testcase_data):
    """Создает тест-кейс"""
    from softlex.testcases.models import TestCase
    return TestCase.objects.create(
        created_by=user,
        project=project,
        **testcase_data
    )


@pytest.fixture
def project_member_data():
    """Данные для создания участника проекта"""
    return {
        'role': 'editor'
    }


@pytest.fixture
def project_member(user, project, project_member_data):
    """Создает участника проекта"""
    from softlex.testcases.models import ProjectMember
    return ProjectMember.objects.create(
        project=project,
        user=user,
        added_by=user,
        **project_member_data
    )


@pytest.fixture
def section_data():
    """Данные для создания секции"""
    return {
        'name': 'Тестовая секция',
        'order': 1
    }


@pytest.fixture
def section(project, section_data):
    """Создает секцию"""
    from softlex.testcases.models import Section
    return Section.objects.create(
        project=project,
        **section_data
    )


@pytest.fixture
def multiple_users():
    """Создает несколько пользователей"""
    users = []
    for i in range(5):
        user = User.objects.create_user(
            email=f'user{i}@example.com',
            password='testpass123',
            first_name=f'Пользователь{i}',
            last_name='Тестовый'
        )
        users.append(user)
    return users


@pytest.fixture
def multiple_projects(user, multiple_users):
    """Создает несколько проектов"""
    from softlex.testcases.models import Project, ProjectMember
    projects = []
    
    for i in range(3):
        project = Project.objects.create(
            name=f'Проект {i+1}',
            description=f'Описание проекта {i+1}',
            created_by=user
        )
        
        # Добавляем участников
        for j, member_user in enumerate(multiple_users[:2]):
            ProjectMember.objects.create(
                project=project,
                user=member_user,
                role='viewer' if j == 0 else 'editor',
                added_by=user
            )
        
        projects.append(project)
    
    return projects


@pytest.fixture
def multiple_testcases(user, multiple_projects):
    """Создает несколько тест-кейсов"""
    from softlex.testcases.models import TestCase
    testcases = []
    
    for i, project in enumerate(multiple_projects):
        for j in range(2):
            testcase = TestCase.objects.create(
                title=f'Тест-кейс {i+1}-{j+1}',
                description=f'Описание тест-кейса {i+1}-{j+1}',
                preconditions='Предусловия',
                steps=f'Шаги {i+1}-{j+1}',
                expected_result=f'Ожидаемый результат {i+1}-{j+1}',
                project=project,
                created_by=user
            )
            testcases.append(testcase)
    
    return testcases


class BaseTestCase(TestCase):
    """Базовый класс для тестов"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем тестовые данные
        cls.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Тест',
            last_name='Пользователь'
        )
        
        cls.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Админ',
            last_name='Системы'
        )
    
    def setUp(self):
        """Настройка для каждого теста"""
        self.client.force_login(self.user)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.client.logout()
