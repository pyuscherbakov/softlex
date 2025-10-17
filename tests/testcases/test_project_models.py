"""
Unit тесты для моделей проектов
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestProjectModel:
    """Тесты для модели Project"""
    
    def test_create_project_success(self, user, project_data):
        """Тест успешного создания проекта"""
        from softlex.testcases.models import Project
        
        project = Project.objects.create(
            created_by=user,
            **project_data
        )
        
        assert project.name == project_data['name']
        assert project.description == project_data['description']
        assert project.created_by == user
        assert project.created_at is not None
        assert project.updated_at is not None
        assert project.created_at <= project.updated_at
    
    def test_project_str_representation(self, project):
        """Тест строкового представления проекта"""
        assert str(project) == project.name
    
    def test_project_meta_verbose_names(self, project):
        """Тест verbose_name в Meta классе"""
        assert project._meta.verbose_name == 'Проект'
        assert project._meta.verbose_name_plural == 'Проекты'
    
    def test_project_ordering(self, user):
        """Тест сортировки проектов"""
        from softlex.testcases.models import Project
        
        project1 = Project.objects.create(
            name='Проект 1',
            created_by=user
        )
        project2 = Project.objects.create(
            name='Проект 2',
            created_by=user
        )
        
        projects = Project.objects.all()
        # Сортировка по -created_at (самые новые первыми)
        assert projects[0] == project2
        assert projects[1] == project1
    
    def test_project_created_at_auto_now_add(self, user):
        """Тест автоматического заполнения created_at"""
        from softlex.testcases.models import Project
        
        before_creation = timezone.now()
        project = Project.objects.create(
            name='Тестовый проект',
            created_by=user
        )
        after_creation = timezone.now()
        
        assert before_creation <= project.created_at <= after_creation
    
    def test_project_updated_at_auto_now(self, user):
        """Тест автоматического обновления updated_at"""
        from softlex.testcases.models import Project
        
        project = Project.objects.create(
            name='Тестовый проект',
            created_by=user
        )
        
        original_updated_at = project.updated_at
        timezone.sleep(0.1)  # Небольшая задержка
        
        project.name = 'Обновленное название'
        project.save()
        
        assert project.updated_at > original_updated_at
    
    def test_project_name_max_length(self, user):
        """Тест максимальной длины названия проекта"""
        from softlex.testcases.models import Project
        
        long_name = 'a' * 201  # Превышает max_length=200
        project = Project(
            name=long_name,
            created_by=user
        )
        
        with pytest.raises(ValidationError) as exc_info:
            project.full_clean()
        
        assert 'name' in str(exc_info.value)
    
    def test_project_created_by_required(self):
        """Тест обязательности поля created_by"""
        from softlex.testcases.models import Project
        
        project = Project(name='Тестовый проект')
        
        with pytest.raises(IntegrityError):
            project.save()


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestSectionModel:
    """Тесты для модели Section"""
    
    def test_create_section_success(self, project, section_data):
        """Тест успешного создания секции"""
        from softlex.testcases.models import Section
        
        section = Section.objects.create(
            project=project,
            **section_data
        )
        
        assert section.name == section_data['name']
        assert section.project == project
        assert section.parent is None
        assert section.order == section_data['order']
        assert section.created_at is not None
    
    def test_section_str_representation(self, section):
        """Тест строкового представления секции"""
        expected = f"{section.project.name} - {section.name}"
        assert str(section) == expected
    
    def test_section_meta_verbose_names(self, section):
        """Тест verbose_name в Meta классе"""
        assert section._meta.verbose_name == 'Секция'
        assert section._meta.verbose_name_plural == 'Секции'
    
    def test_section_ordering(self, project):
        """Тест сортировки секций"""
        from softlex.testcases.models import Section
        
        section1 = Section.objects.create(
            name='Секция 1',
            project=project,
            order=2
        )
        section2 = Section.objects.create(
            name='Секция 2',
            project=project,
            order=1
        )
        
        sections = Section.objects.all()
        # Сортировка по order, затем по name
        assert sections[0] == section2
        assert sections[1] == section1
    
    def test_section_with_parent(self, project):
        """Тест создания секции с родительской секцией"""
        from softlex.testcases.models import Section
        
        parent_section = Section.objects.create(
            name='Родительская секция',
            project=project
        )
        
        child_section = Section.objects.create(
            name='Дочерняя секция',
            project=project,
            parent=parent_section
        )
        
        assert child_section.parent == parent_section
        assert child_section in parent_section.children.all()
    
    def test_section_name_max_length(self, project):
        """Тест максимальной длины названия секции"""
        from softlex.testcases.models import Section
        
        long_name = 'a' * 201  # Превышает max_length=200
        section = Section(
            name=long_name,
            project=project
        )
        
        with pytest.raises(ValidationError) as exc_info:
            section.full_clean()
        
        assert 'name' in str(exc_info.value)
    
    def test_section_project_required(self):
        """Тест обязательности поля project"""
        from softlex.testcases.models import Section
        
        section = Section(name='Тестовая секция')
        
        with pytest.raises(IntegrityError):
            section.save()
    
    def test_section_created_at_auto_now_add(self, project):
        """Тест автоматического заполнения created_at"""
        from softlex.testcases.models import Section
        
        before_creation = timezone.now()
        section = Section.objects.create(
            name='Тестовая секция',
            project=project
        )
        after_creation = timezone.now()
        
        assert before_creation <= section.created_at <= after_creation


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestTestCaseModel:
    """Тесты для модели TestCase"""
    
    def test_create_testcase_success(self, user, project, testcase_data):
        """Тест успешного создания тест-кейса"""
        from softlex.testcases.models import TestCase
        
        testcase = TestCase.objects.create(
            created_by=user,
            project=project,
            **testcase_data
        )
        
        assert testcase.title == testcase_data['title']
        assert testcase.description == testcase_data['description']
        assert testcase.preconditions == testcase_data['preconditions']
        assert testcase.steps == testcase_data['steps']
        assert testcase.expected_result == testcase_data['expected_result']
        assert testcase.project == project
        assert testcase.created_by == user
        assert testcase.section is None
        assert testcase.created_at is not None
        assert testcase.updated_at is not None
    
    def test_testcase_str_representation(self, testcase):
        """Тест строкового представления тест-кейса"""
        assert str(testcase) == testcase.title
    
    def test_testcase_meta_verbose_names(self, testcase):
        """Тест verbose_name в Meta классе"""
        assert testcase._meta.verbose_name == 'Тест-кейс'
        assert testcase._meta.verbose_name_plural == 'Тест-кейсы'
    
    def test_testcase_ordering(self, user, project):
        """Тест сортировки тест-кейсов"""
        from softlex.testcases.models import TestCase
        
        testcase1 = TestCase.objects.create(
            title='Тест-кейс 1',
            steps='Шаги 1',
            expected_result='Результат 1',
            project=project,
            created_by=user
        )
        testcase2 = TestCase.objects.create(
            title='Тест-кейс 2',
            steps='Шаги 2',
            expected_result='Результат 2',
            project=project,
            created_by=user
        )
        
        testcases = TestCase.objects.all()
        # Сортировка по -created_at (самые новые первыми)
        assert testcases[0] == testcase2
        assert testcases[1] == testcase1
    
    def test_testcase_with_section(self, user, project, section):
        """Тест создания тест-кейса с секцией"""
        from softlex.testcases.models import TestCase
        
        testcase = TestCase.objects.create(
            title='Тест-кейс с секцией',
            steps='Шаги',
            expected_result='Результат',
            project=project,
            section=section,
            created_by=user
        )
        
        assert testcase.section == section
        assert testcase in section.test_cases.all()
    
    def test_testcase_title_max_length(self, user, project):
        """Тест максимальной длины названия тест-кейса"""
        from softlex.testcases.models import TestCase
        
        long_title = 'a' * 301  # Превышает max_length=300
        testcase = TestCase(
            title=long_title,
            steps='Шаги',
            expected_result='Результат',
            project=project,
            created_by=user
        )
        
        with pytest.raises(ValidationError) as exc_info:
            testcase.full_clean()
        
        assert 'title' in str(exc_info.value)
    
    def test_testcase_steps_required(self, user, project):
        """Тест обязательности поля steps"""
        from softlex.testcases.models import TestCase
        
        testcase = TestCase(
            title='Тест-кейс без шагов',
            expected_result='Результат',
            project=project,
            created_by=user
        )
        
        with pytest.raises(ValidationError) as exc_info:
            testcase.full_clean()
        
        assert 'steps' in str(exc_info.value)
    
    def test_testcase_expected_result_required(self, user, project):
        """Тест обязательности поля expected_result"""
        from softlex.testcases.models import TestCase
        
        testcase = TestCase(
            title='Тест-кейс без результата',
            steps='Шаги',
            project=project,
            created_by=user
        )
        
        with pytest.raises(ValidationError) as exc_info:
            testcase.full_clean()
        
        assert 'expected_result' in str(exc_info.value)
    
    def test_testcase_project_required(self, user):
        """Тест обязательности поля project"""
        from softlex.testcases.models import TestCase
        
        testcase = TestCase(
            title='Тест-кейс без проекта',
            steps='Шаги',
            expected_result='Результат',
            created_by=user
        )
        
        with pytest.raises(IntegrityError):
            testcase.save()
    
    def test_testcase_created_by_required(self, project):
        """Тест обязательности поля created_by"""
        from softlex.testcases.models import TestCase
        
        testcase = TestCase(
            title='Тест-кейс без создателя',
            steps='Шаги',
            expected_result='Результат',
            project=project
        )
        
        with pytest.raises(IntegrityError):
            testcase.save()
    
    def test_testcase_created_at_auto_now_add(self, user, project):
        """Тест автоматического заполнения created_at"""
        from softlex.testcases.models import TestCase
        
        before_creation = timezone.now()
        testcase = TestCase.objects.create(
            title='Тест-кейс',
            steps='Шаги',
            expected_result='Результат',
            project=project,
            created_by=user
        )
        after_creation = timezone.now()
        
        assert before_creation <= testcase.created_at <= after_creation
    
    def test_testcase_updated_at_auto_now(self, user, project):
        """Тест автоматического обновления updated_at"""
        from softlex.testcases.models import TestCase
        
        testcase = TestCase.objects.create(
            title='Тест-кейс',
            steps='Шаги',
            expected_result='Результат',
            project=project,
            created_by=user
        )
        
        original_updated_at = testcase.updated_at
        timezone.sleep(0.1)  # Небольшая задержка
        
        testcase.title = 'Обновленное название'
        testcase.save()
        
        assert testcase.updated_at > original_updated_at


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestProjectMemberModel:
    """Тесты для модели ProjectMember"""
    
    def test_create_project_member_success(self, user, project, project_member_data):
        """Тест успешного создания участника проекта"""
        from softlex.testcases.models import ProjectMember
        
        member = ProjectMember.objects.create(
            project=project,
            user=user,
            added_by=user,
            **project_member_data
        )
        
        assert member.project == project
        assert member.user == user
        assert member.role == project_member_data['role']
        assert member.added_by == user
        assert member.added_at is not None
    
    def test_project_member_str_representation(self, project_member):
        """Тест строкового представления участника проекта"""
        expected = f"{project_member.user.email} - {project_member.project.name} ({project_member.get_role_display()})"
        assert str(project_member) == expected
    
    def test_project_member_meta_verbose_names(self, project_member):
        """Тест verbose_name в Meta классе"""
        assert project_member._meta.verbose_name == 'Участник проекта'
        assert project_member._meta.verbose_name_plural == 'Участники проектов'
    
    def test_project_member_ordering(self, user, project):
        """Тест сортировки участников проекта"""
        from softlex.testcases.models import ProjectMember
        
        member1 = ProjectMember.objects.create(
            project=project,
            user=user,
            role='viewer',
            added_by=user
        )
        member2 = ProjectMember.objects.create(
            project=project,
            user=user,
            role='editor',
            added_by=user
        )
        
        members = ProjectMember.objects.all()
        # Сортировка по -added_at (самые новые первыми)
        assert members[0] == member2
        assert members[1] == member1
    
    def test_project_member_unique_together(self, user, project):
        """Тест уникальности пары project-user"""
        from softlex.testcases.models import ProjectMember
        
        ProjectMember.objects.create(
            project=project,
            user=user,
            role='viewer',
            added_by=user
        )
        
        # Попытка создать дубликат должна вызвать ошибку
        with pytest.raises(IntegrityError):
            ProjectMember.objects.create(
                project=project,
                user=user,
                role='editor',
                added_by=user
            )
    
    def test_project_member_role_choices(self, user, project):
        """Тест выбора ролей участника проекта"""
        from softlex.testcases.models import ProjectMember
        
        valid_roles = ['viewer', 'editor', 'admin']
        
        for role in valid_roles:
            member = ProjectMember.objects.create(
                project=project,
                user=user,
                role=role,
                added_by=user
            )
            assert member.role == role
    
    def test_project_member_added_at_auto_now_add(self, user, project):
        """Тест автоматического заполнения added_at"""
        from softlex.testcases.models import ProjectMember
        
        before_creation = timezone.now()
        member = ProjectMember.objects.create(
            project=project,
            user=user,
            role='viewer',
            added_by=user
        )
        after_creation = timezone.now()
        
        assert before_creation <= member.added_at <= after_creation
    
    def test_project_member_project_required(self, user):
        """Тест обязательности поля project"""
        from softlex.testcases.models import ProjectMember
        
        member = ProjectMember(
            user=user,
            role='viewer',
            added_by=user
        )
        
        with pytest.raises(IntegrityError):
            member.save()
    
    def test_project_member_user_required(self, project, user):
        """Тест обязательности поля user"""
        from softlex.testcases.models import ProjectMember
        
        member = ProjectMember(
            project=project,
            role='viewer',
            added_by=user
        )
        
        with pytest.raises(IntegrityError):
            member.save()
    
    def test_project_member_role_required(self, user, project):
        """Тест обязательности поля role"""
        from softlex.testcases.models import ProjectMember
        
        member = ProjectMember(
            project=project,
            user=user,
            added_by=user
        )
        
        with pytest.raises(IntegrityError):
            member.save()
    
    def test_project_member_added_by_can_be_null(self, user, project):
        """Тест что поле added_by может быть null"""
        from softlex.testcases.models import ProjectMember
        
        member = ProjectMember.objects.create(
            project=project,
            user=user,
            role='viewer',
            added_by=None
        )
        
        assert member.added_by is None
        assert member.project == project
        assert member.user == user
        assert member.role == 'viewer'
