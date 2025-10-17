"""
Unit тесты для модели User
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestUserModel:
    """Тесты для модели User"""
    
    def test_create_user_success(self, user_data):
        """Тест успешного создания пользователя"""
        user = User.objects.create_user(**user_data)
        
        assert user.email == user_data['email']
        assert user.first_name == user_data['first_name']
        assert user.last_name == user_data['last_name']
        assert user.role == user_data['role']
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password(user_data['password'])
        assert user.username is None
        assert user.USERNAME_FIELD == 'email'
        assert user.REQUIRED_FIELDS == []
    
    def test_create_user_without_email_raises_error(self):
        """Тест создания пользователя без email вызывает ошибку"""
        with pytest.raises(ValueError, match='Email обязателен'):
            User.objects.create_user(email='', password='testpass123')
    
    def test_create_user_with_invalid_email_raises_error(self):
        """Тест создания пользователя с невалидным email"""
        with pytest.raises(ValidationError):
            user = User(email='invalid-email')
            user.full_clean()
    
    def test_create_superuser_success(self, admin_data):
        """Тест успешного создания суперпользователя"""
        user = User.objects.create_superuser(**admin_data)
        
        assert user.email == admin_data['email']
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.role == 'admin'
        assert user.is_active is True
    
    def test_create_superuser_without_staff_raises_error(self):
        """Тест создания суперпользователя без is_staff вызывает ошибку"""
        with pytest.raises(ValueError, match='Superuser must have is_staff=True'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
    
    def test_create_superuser_without_superuser_raises_error(self):
        """Тест создания суперпользователя без is_superuser вызывает ошибку"""
        with pytest.raises(ValueError, match='Superuser must have is_superuser=True'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )
    
    def test_email_uniqueness(self, user_data):
        """Тест уникальности email"""
        User.objects.create_user(**user_data)
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email=user_data['email'],
                password='anotherpass123'
            )
    
    def test_str_representation(self, user):
        """Тест строкового представления пользователя"""
        assert str(user) == user.email
    
    def test_is_admin_property(self, user, admin):
        """Тест свойства is_admin"""
        assert user.is_admin is False
        assert admin.is_admin is True
    
    def test_is_blocked_property(self, user, inactive_user):
        """Тест свойства is_blocked"""
        assert user.is_blocked is False
        assert inactive_user.is_blocked is True
    
    def test_full_name_property_with_both_names(self, user):
        """Тест свойства full_name с именем и фамилией"""
        user.first_name = 'Иван'
        user.last_name = 'Петров'
        user.save()
        
        assert user.full_name == 'Иван Петров'
    
    def test_full_name_property_with_first_name_only(self, user):
        """Тест свойства full_name только с именем"""
        user.first_name = 'Иван'
        user.last_name = ''
        user.save()
        
        assert user.full_name == 'Иван'
    
    def test_full_name_property_with_last_name_only(self, user):
        """Тест свойства full_name только с фамилией"""
        user.first_name = ''
        user.last_name = 'Петров'
        user.save()
        
        assert user.full_name == 'Петров'
    
    def test_full_name_property_without_names(self, user):
        """Тест свойства full_name без имени и фамилии"""
        user.first_name = ''
        user.last_name = ''
        user.save()
        
        assert user.full_name == user.email
    
    def test_role_choices(self, user):
        """Тест выбора ролей"""
        valid_roles = ['admin', 'user']
        
        for role in valid_roles:
            user.role = role
            user.save()
            user.refresh_from_db()
            assert user.role == role
    
    def test_last_login_date_update(self, user):
        """Тест обновления даты последней авторизации"""
        initial_date = user.last_login_date
        new_date = timezone.now()
        
        user.last_login_date = new_date
        user.save()
        
        user.refresh_from_db()
        assert user.last_login_date == new_date
        assert user.last_login_date != initial_date
    
    def test_user_creation_with_minimal_data(self):
        """Тест создания пользователя с минимальными данными"""
        user = User.objects.create_user(
            email='minimal@example.com',
            password='testpass123'
        )
        
        assert user.email == 'minimal@example.com'
        assert user.first_name == ''
        assert user.last_name == ''
        assert user.role == 'user'
        assert user.is_active is True
    
    def test_user_creation_with_all_fields(self):
        """Тест создания пользователя со всеми полями"""
        user = User.objects.create_user(
            email='full@example.com',
            password='testpass123',
            first_name='Полное',
            last_name='Имя',
            role='admin',
            is_active=False
        )
        
        assert user.email == 'full@example.com'
        assert user.first_name == 'Полное'
        assert user.last_name == 'Имя'
        assert user.role == 'admin'
        assert user.is_active is False
    
    def test_user_manager_create_user_method(self):
        """Тест метода create_user менеджера"""
        user = User.objects.create_user(
            email='manager@example.com',
            password='testpass123'
        )
        
        assert user.email == 'manager@example.com'
        assert user.check_password('testpass123')
        assert user.is_active is True
    
    def test_user_manager_create_superuser_method(self):
        """Тест метода create_superuser менеджера"""
        user = User.objects.create_superuser(
            email='super@example.com',
            password='testpass123'
        )
        
        assert user.email == 'super@example.com'
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.role == 'admin'
    
    def test_user_meta_verbose_names(self, user):
        """Тест verbose_name в Meta классе"""
        assert user._meta.verbose_name == 'Пользователь'
        assert user._meta.verbose_name_plural == 'Пользователи'
    
    def test_user_ordering(self):
        """Тест сортировки пользователей"""
        user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        
        users = User.objects.all()
        # По умолчанию сортировка по date_joined (самые новые первыми)
        assert users[0] == user2
        assert users[1] == user1


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestUserModelValidation:
    """Тесты валидации модели User"""
    
    def test_email_field_validation(self):
        """Тест валидации поля email"""
        user = User(email='invalid-email')
        
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        
        assert 'email' in str(exc_info.value)
    
    def test_first_name_max_length_validation(self):
        """Тест валидации максимальной длины имени"""
        user = User(
            email='test@example.com',
            first_name='a' * 151  # Превышает max_length=150
        )
        
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        
        assert 'first_name' in str(exc_info.value)
    
    def test_last_name_max_length_validation(self):
        """Тест валидации максимальной длины фамилии"""
        user = User(
            email='test@example.com',
            last_name='a' * 151  # Превышает max_length=150
        )
        
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        
        assert 'last_name' in str(exc_info.value)
    
    def test_role_choices_validation(self):
        """Тест валидации выбора роли"""
        user = User(
            email='test@example.com',
            role='invalid_role'
        )
        
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        
        assert 'role' in str(exc_info.value)
