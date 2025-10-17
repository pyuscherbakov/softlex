"""
Unit тесты для форм пользователей
"""
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django import forms
from softlex.users.forms import LoginForm, RegistrationForm, UserEditForm

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.forms
class TestLoginForm:
    """Тесты для формы LoginForm"""
    
    def test_login_form_valid_data(self, user):
        """Тест формы входа с валидными данными"""
        form_data = {
            'email': user.email,
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        
        assert form.is_valid()
        assert form.cleaned_data['email'] == user.email
        assert form.cleaned_data['password'] == 'testpass123'
    
    def test_login_form_invalid_email(self):
        """Тест формы входа с невалидным email"""
        form_data = {
            'email': 'invalid-email',
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_login_form_missing_email(self):
        """Тест формы входа без email"""
        form_data = {
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_login_form_missing_password(self, user):
        """Тест формы входа без пароля"""
        form_data = {
            'email': user.email
        }
        form = LoginForm(data=form_data)
        
        assert not form.is_valid()
        assert 'password' in form.errors
    
    def test_login_form_wrong_credentials(self):
        """Тест формы входа с неверными учетными данными"""
        form_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        form = LoginForm(data=form_data)
        
        assert not form.is_valid()
        assert 'Неверный email или пароль' in str(form.errors)
    
    def test_login_form_inactive_user(self, inactive_user):
        """Тест формы входа с неактивным пользователем"""
        form_data = {
            'email': inactive_user.email,
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        
        assert not form.is_valid()
        assert 'Аккаунт заблокирован' in str(form.errors)
    
    def test_login_form_widget_attrs(self):
        """Тест атрибутов виджетов формы входа"""
        form = LoginForm()
        
        email_widget = form.fields['email'].widget
        password_widget = form.fields['password'].widget
        
        assert 'form-control' in email_widget.attrs['class']
        assert 'placeholder' in email_widget.attrs
        assert 'form-control' in password_widget.attrs['class']
        assert 'placeholder' in password_widget.attrs
    
    def test_login_form_labels(self):
        """Тест меток полей формы входа"""
        form = LoginForm()
        
        assert form.fields['email'].label == 'Email'
        assert form.fields['password'].label == 'Пароль'
    
    def test_login_form_error_messages(self):
        """Тест сообщений об ошибках формы входа"""
        form = LoginForm()
        
        email_errors = form.fields['email'].error_messages
        password_errors = form.fields['password'].error_messages
        
        assert 'required' in email_errors
        assert 'invalid' in email_errors
        assert 'required' in password_errors


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.forms
class TestRegistrationForm:
    """Тесты для формы RegistrationForm"""
    
    def test_registration_form_valid_data(self):
        """Тест формы регистрации с валидными данными"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = RegistrationForm(data=form_data)
        
        assert form.is_valid()
        assert form.cleaned_data['email'] == 'newuser@example.com'
        assert form.cleaned_data['first_name'] == 'Новый'
        assert form.cleaned_data['last_name'] == 'Пользователь'
    
    def test_registration_form_save(self):
        """Тест сохранения формы регистрации"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = RegistrationForm(data=form_data)
        
        assert form.is_valid()
        user = form.save()
        
        assert user.email == 'newuser@example.com'
        assert user.first_name == 'Новый'
        assert user.last_name == 'Пользователь'
        assert user.check_password('newpass123')
        assert user.is_active is True
        assert user.role == 'user'
    
    def test_registration_form_duplicate_email(self, user):
        """Тест формы регистрации с существующим email"""
        form_data = {
            'email': user.email,
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = RegistrationForm(data=form_data)
        
        assert not form.is_valid()
        assert 'Пользователь с таким email уже существует' in str(form.errors)
    
    def test_registration_form_password_mismatch(self):
        """Тест формы регистрации с несовпадающими паролями"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'differentpass123'
        }
        form = RegistrationForm(data=form_data)
        
        assert not form.is_valid()
        assert 'Пароли не совпадают' in str(form.errors)
    
    def test_registration_form_short_password(self):
        """Тест формы регистрации с коротким паролем"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': '123',
            'password2': '123'
        }
        form = RegistrationForm(data=form_data)
        
        assert not form.is_valid()
        assert 'password1' in form.errors
    
    def test_registration_form_invalid_email(self):
        """Тест формы регистрации с невалидным email"""
        form_data = {
            'email': 'invalid-email',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = RegistrationForm(data=form_data)
        
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_registration_form_long_first_name(self):
        """Тест формы регистрации с длинным именем"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'a' * 31,  # Превышает max_length=30
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = RegistrationForm(data=form_data)
        
        assert not form.is_valid()
        assert 'first_name' in form.errors
    
    def test_registration_form_long_last_name(self):
        """Тест формы регистрации с длинной фамилией"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'a' * 31,  # Превышает max_length=30
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = RegistrationForm(data=form_data)
        
        assert not form.is_valid()
        assert 'last_name' in form.errors
    
    def test_registration_form_empty_first_name(self):
        """Тест формы регистрации с пустым именем (должно быть валидно)"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': '',
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = RegistrationForm(data=form_data)
        
        assert form.is_valid()
        user = form.save()
        assert user.first_name == ''
    
    def test_registration_form_empty_last_name(self):
        """Тест формы регистрации с пустой фамилией (должно быть валидно)"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': '',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = RegistrationForm(data=form_data)
        
        assert form.is_valid()
        user = form.save()
        assert user.last_name == ''
    
    def test_registration_form_widget_attrs(self):
        """Тест атрибутов виджетов формы регистрации"""
        form = RegistrationForm()
        
        email_widget = form.fields['email'].widget
        first_name_widget = form.fields['first_name'].widget
        last_name_widget = form.fields['last_name'].widget
        password1_widget = form.fields['password1'].widget
        password2_widget = form.fields['password2'].widget
        
        assert 'form-control' in email_widget.attrs['class']
        assert 'form-control' in first_name_widget.attrs['class']
        assert 'form-control' in last_name_widget.attrs['class']
        assert 'form-control' in password1_widget.attrs['class']
        assert 'form-control' in password2_widget.attrs['class']
    
    def test_registration_form_labels(self):
        """Тест меток полей формы регистрации"""
        form = RegistrationForm()
        
        assert form.fields['email'].label == 'Email'
        assert form.fields['first_name'].label == 'Имя'
        assert form.fields['last_name'].label == 'Фамилия'
        assert form.fields['password1'].label == 'Пароль'
        assert form.fields['password2'].label == 'Подтверждение пароля'
    
    def test_registration_form_meta_fields(self):
        """Тест полей в Meta классе формы регистрации"""
        form = RegistrationForm()
        
        expected_fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
        assert form.Meta.fields == expected_fields
        assert form.Meta.model == User


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.forms
class TestUserEditForm:
    """Тесты для формы UserEditForm"""
    
    def test_user_edit_form_valid_data(self, user):
        """Тест формы редактирования с валидными данными"""
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'Обновленное',
            'last_name': 'Имя',
            'role': 'admin'
        }
        form = UserEditForm(data=form_data, instance=user)
        
        assert form.is_valid()
        assert form.cleaned_data['email'] == 'updated@example.com'
        assert form.cleaned_data['first_name'] == 'Обновленное'
        assert form.cleaned_data['last_name'] == 'Имя'
        assert form.cleaned_data['role'] == 'admin'
    
    def test_user_edit_form_save(self, user):
        """Тест сохранения формы редактирования"""
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'Обновленное',
            'last_name': 'Имя',
            'role': 'admin'
        }
        form = UserEditForm(data=form_data, instance=user)
        
        assert form.is_valid()
        updated_user = form.save()
        
        assert updated_user.email == 'updated@example.com'
        assert updated_user.first_name == 'Обновленное'
        assert updated_user.last_name == 'Имя'
        assert updated_user.role == 'admin'
    
    def test_user_edit_form_duplicate_email(self, user):
        """Тест формы редактирования с существующим email другого пользователя"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        
        form_data = {
            'email': other_user.email,  # Используем email другого пользователя
            'first_name': 'Обновленное',
            'last_name': 'Имя',
            'role': 'user'
        }
        form = UserEditForm(data=form_data, instance=user)
        
        assert not form.is_valid()
        assert 'Пользователь с таким email уже существует' in str(form.errors)
    
    def test_user_edit_form_same_email(self, user):
        """Тест формы редактирования с тем же email (должно быть валидно)"""
        form_data = {
            'email': user.email,  # Тот же email
            'first_name': 'Обновленное',
            'last_name': 'Имя',
            'role': 'user'
        }
        form = UserEditForm(data=form_data, instance=user)
        
        assert form.is_valid()
    
    def test_user_edit_form_invalid_email(self, user):
        """Тест формы редактирования с невалидным email"""
        form_data = {
            'email': 'invalid-email',
            'first_name': 'Обновленное',
            'last_name': 'Имя',
            'role': 'user'
        }
        form = UserEditForm(data=form_data, instance=user)
        
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_user_edit_form_long_first_name(self, user):
        """Тест формы редактирования с длинным именем"""
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'a' * 151,  # Превышает max_length=150
            'last_name': 'Имя',
            'role': 'user'
        }
        form = UserEditForm(data=form_data, instance=user)
        
        assert not form.is_valid()
        assert 'first_name' in form.errors
    
    def test_user_edit_form_long_last_name(self, user):
        """Тест формы редактирования с длинной фамилией"""
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'Обновленное',
            'last_name': 'a' * 151,  # Превышает max_length=150
            'role': 'user'
        }
        form = UserEditForm(data=form_data, instance=user)
        
        assert not form.is_valid()
        assert 'last_name' in form.errors
    
    def test_user_edit_form_invalid_role(self, user):
        """Тест формы редактирования с невалидной ролью"""
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'Обновленное',
            'last_name': 'Имя',
            'role': 'invalid_role'
        }
        form = UserEditForm(data=form_data, instance=user)
        
        assert not form.is_valid()
        assert 'role' in form.errors
    
    def test_user_edit_form_widget_attrs(self, user):
        """Тест атрибутов виджетов формы редактирования"""
        form = UserEditForm(instance=user)
        
        email_widget = form.fields['email'].widget
        first_name_widget = form.fields['first_name'].widget
        last_name_widget = form.fields['last_name'].widget
        role_widget = form.fields['role'].widget
        
        assert 'form-control' in email_widget.attrs['class']
        assert 'form-control' in first_name_widget.attrs['class']
        assert 'form-control' in last_name_widget.attrs['class']
        assert 'form-control' in role_widget.attrs['class']
    
    def test_user_edit_form_labels(self, user):
        """Тест меток полей формы редактирования"""
        form = UserEditForm(instance=user)
        
        assert form.fields['email'].label == 'Email'
        assert form.fields['first_name'].label == 'Имя'
        assert form.fields['last_name'].label == 'Фамилия'
        assert form.fields['role'].label == 'Роль'
    
    def test_user_edit_form_meta_fields(self, user):
        """Тест полей в Meta классе формы редактирования"""
        form = UserEditForm(instance=user)
        
        expected_fields = ['email', 'first_name', 'last_name', 'role']
        assert form.Meta.fields == expected_fields
        assert form.Meta.model == User
    
    def test_user_edit_form_role_choices(self, user):
        """Тест выбора ролей в форме редактирования"""
        form = UserEditForm(instance=user)
        
        role_choices = form.fields['role'].choices
        expected_choices = [('admin', 'Администратор'), ('user', 'Пользователь')]
        assert list(role_choices) == expected_choices
