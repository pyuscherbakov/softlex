"""
Unit тесты для представлений пользователей
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from unittest.mock import patch

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.views
class TestLoginView:
    """Тесты для представления входа"""
    
    def test_login_view_get(self, client):
        """Тест GET запроса к странице входа"""
        response = client.get(reverse('users:login'))
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'users/login.html' in [template.name for template in response.templates]
    
    def test_login_view_authenticated_user_redirect(self, client, user):
        """Тест перенаправления аутентифицированного пользователя"""
        client.force_login(user)
        response = client.get(reverse('users:login'))
        
        assert response.status_code == 302
        assert response.url == '/'
    
    def test_login_view_valid_credentials(self, client, user):
        """Тест входа с валидными учетными данными"""
        form_data = {
            'email': user.email,
            'password': 'testpass123'
        }
        
        with patch('django.contrib.auth.authenticate') as mock_authenticate:
            mock_authenticate.return_value = user
            
            response = client.post(reverse('users:login'), data=form_data)
            
            assert response.status_code == 302
            assert response.url == '/'
            
            # Проверяем, что last_login_date обновлен
            user.refresh_from_db()
            assert user.last_login_date is not None
    
    def test_login_view_invalid_credentials(self, client):
        """Тест входа с неверными учетными данными"""
        form_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        with patch('django.contrib.auth.authenticate') as mock_authenticate:
            mock_authenticate.return_value = None
            
            response = client.post(reverse('users:login'), data=form_data)
            
            assert response.status_code == 200
            assert 'Неверный email или пароль' in str(response.content)
    
    def test_login_view_inactive_user(self, client, inactive_user):
        """Тест входа с неактивным пользователем"""
        form_data = {
            'email': inactive_user.email,
            'password': 'testpass123'
        }
        
        with patch('django.contrib.auth.authenticate') as mock_authenticate:
            mock_authenticate.return_value = inactive_user
            
            response = client.post(reverse('users:login'), data=form_data)
            
            assert response.status_code == 200
            assert 'Аккаунт заблокирован' in str(response.content)
    
    def test_login_view_blocked_user(self, client, user):
        """Тест входа с заблокированным пользователем"""
        user.is_active = False
        user.save()
        
        form_data = {
            'email': user.email,
            'password': 'testpass123'
        }
        
        with patch('django.contrib.auth.authenticate') as mock_authenticate:
            mock_authenticate.return_value = user
            
            response = client.post(reverse('users:login'), data=form_data)
            
            assert response.status_code == 200
            assert 'Аккаунт заблокирован' in str(response.content)


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.views
class TestLogoutView:
    """Тесты для представления выхода"""
    
    def test_logout_view(self, client, user):
        """Тест выхода из системы"""
        client.force_login(user)
        
        response = client.get(reverse('users:logout'))
        
        assert response.status_code == 302
        assert response.url == reverse('users:login')
        
        # Проверяем сообщение
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'Вы вышли из системы' in str(messages[0])


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.views
class TestRegisterView:
    """Тесты для представления регистрации"""
    
    def test_register_view_get_anonymous(self, client):
        """Тест GET запроса к странице регистрации для анонимного пользователя"""
        response = client.get(reverse('users:register'))
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'users/register.html' in [template.name for template in response.templates]
    
    def test_register_view_get_authenticated_user(self, client, user):
        """Тест GET запроса к странице регистрации для аутентифицированного пользователя"""
        client.force_login(user)
        response = client.get(reverse('users:register'))
        
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_register_view_get_authenticated_admin(self, client, admin):
        """Тест GET запроса к странице регистрации для администратора"""
        client.force_login(admin)
        response = client.get(reverse('users:register'))
        
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_register_view_post_anonymous_valid_data(self, client):
        """Тест POST запроса с валидными данными для анонимного пользователя"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        
        response = client.post(reverse('users:register'), data=form_data)
        
        assert response.status_code == 302
        assert response.url == '/'
        
        # Проверяем, что пользователь создан
        assert User.objects.filter(email='newuser@example.com').exists()
        
        # Проверяем сообщение
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'Регистрация прошла успешно' in str(messages[0])
    
    def test_register_view_post_anonymous_invalid_data(self, client):
        """Тест POST запроса с невалидными данными для анонимного пользователя"""
        form_data = {
            'email': 'invalid-email',
            'password1': 'short',
            'password2': 'different'
        }
        
        response = client.post(reverse('users:register'), data=form_data)
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert not response.context['form'].is_valid()
    
    def test_register_view_post_authenticated_user(self, client, user):
        """Тест POST запроса для обычного пользователя (должен быть перенаправлен)"""
        client.force_login(user)
        
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        
        response = client.post(reverse('users:register'), data=form_data)
        
        assert response.status_code == 302
        assert response.url == '/'
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'У вас нет прав для создания пользователей' in str(messages[0])
    
    def test_register_view_post_authenticated_admin(self, client, admin):
        """Тест POST запроса для администратора"""
        client.force_login(admin)
        
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        
        response = client.post(reverse('users:register'), data=form_data)
        
        assert response.status_code == 302
        assert response.url == reverse('users:user_list')
        
        # Проверяем, что пользователь создан
        assert User.objects.filter(email='newuser@example.com').exists()
        
        # Проверяем сообщение
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'Пользователь newuser@example.com успешно создан' in str(messages[0])


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.views
class TestUserListView:
    """Тесты для представления списка пользователей"""
    
    def test_user_list_view_anonymous(self, client):
        """Тест доступа к списку пользователей для анонимного пользователя"""
        response = client.get(reverse('users:user_list'))
        
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_user_list_view_authenticated_user(self, client, user):
        """Тест доступа к списку пользователей для обычного пользователя"""
        client.force_login(user)
        response = client.get(reverse('users:user_list'))
        
        assert response.status_code == 302
        assert response.url == '/'
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'У вас нет прав для просмотра списка пользователей' in str(messages[0])
    
    def test_user_list_view_admin(self, client, admin, multiple_users):
        """Тест доступа к списку пользователей для администратора"""
        client.force_login(admin)
        response = client.get(reverse('users:user_list'))
        
        assert response.status_code == 200
        assert 'page_obj' in response.context
        assert 'search' in response.context
        assert 'role_filter' in response.context
        assert 'role_choices' in response.context
        assert 'users/user_list.html' in [template.name for template in response.templates]
    
    def test_user_list_view_search(self, client, admin, multiple_users):
        """Тест поиска пользователей"""
        client.force_login(admin)
        
        response = client.get(reverse('users:user_list'), {'search': 'Пользователь1'})
        
        assert response.status_code == 200
        assert 'search' in response.context
        assert response.context['search'] == 'Пользователь1'
    
    def test_user_list_view_role_filter(self, client, admin, multiple_users):
        """Тест фильтрации по роли"""
        client.force_login(admin)
        
        response = client.get(reverse('users:user_list'), {'role': 'user'})
        
        assert response.status_code == 200
        assert 'role_filter' in response.context
        assert response.context['role_filter'] == 'user'
    
    def test_user_list_view_pagination(self, client, admin):
        """Тест пагинации списка пользователей"""
        # Создаем много пользователей для тестирования пагинации
        for i in range(25):
            User.objects.create_user(
                email=f'user{i}@example.com',
                password='testpass123'
            )
        
        client.force_login(admin)
        response = client.get(reverse('users:user_list'))
        
        assert response.status_code == 200
        assert 'page_obj' in response.context
        assert response.context['page_obj'].paginator.num_pages > 1


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.views
class TestUserDetailView:
    """Тесты для представления детальной информации о пользователе"""
    
    def test_user_detail_view_anonymous(self, client, user):
        """Тест доступа к детальной информации для анонимного пользователя"""
        response = client.get(reverse('users:user_detail', args=[user.id]))
        
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_user_detail_view_authenticated_user(self, client, user, multiple_users):
        """Тест доступа к детальной информации для обычного пользователя"""
        client.force_login(user)
        response = client.get(reverse('users:user_detail', args=[multiple_users[0].id]))
        
        assert response.status_code == 302
        assert response.url == '/'
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'У вас нет прав для просмотра информации о пользователях' in str(messages[0])
    
    def test_user_detail_view_admin(self, client, admin, user):
        """Тест доступа к детальной информации для администратора"""
        client.force_login(admin)
        response = client.get(reverse('users:user_detail', args=[user.id]))
        
        assert response.status_code == 200
        assert 'user_obj' in response.context
        assert response.context['user_obj'] == user
        assert 'users/user_detail.html' in [template.name for template in response.templates]
    
    def test_user_detail_view_nonexistent_user(self, client, admin):
        """Тест доступа к несуществующему пользователю"""
        client.force_login(admin)
        response = client.get(reverse('users:user_detail', args=[99999]))
        
        assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.views
class TestUserEditView:
    """Тесты для представления редактирования пользователя"""
    
    def test_user_edit_view_anonymous(self, client, user):
        """Тест доступа к редактированию для анонимного пользователя"""
        response = client.get(reverse('users:user_edit', args=[user.id]))
        
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_user_edit_view_authenticated_user(self, client, user, multiple_users):
        """Тест доступа к редактированию для обычного пользователя"""
        client.force_login(user)
        response = client.get(reverse('users:user_edit', args=[multiple_users[0].id]))
        
        assert response.status_code == 302
        assert response.url == '/'
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'У вас нет прав для редактирования пользователей' in str(messages[0])
    
    def test_user_edit_view_admin_get(self, client, admin, user):
        """Тест GET запроса к редактированию для администратора"""
        client.force_login(admin)
        response = client.get(reverse('users:user_edit', args=[user.id]))
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'user_obj' in response.context
        assert response.context['user_obj'] == user
        assert 'users/user_edit.html' in [template.name for template in response.templates]
    
    def test_user_edit_view_admin_post_valid(self, client, admin, user):
        """Тест POST запроса с валидными данными для администратора"""
        client.force_login(admin)
        
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'Обновленное',
            'last_name': 'Имя',
            'role': 'admin'
        }
        
        response = client.post(reverse('users:user_edit', args=[user.id]), data=form_data)
        
        assert response.status_code == 302
        assert response.url == reverse('users:user_detail', args=[user.id])
        
        # Проверяем, что пользователь обновлен
        user.refresh_from_db()
        assert user.email == 'updated@example.com'
        assert user.first_name == 'Обновленное'
        assert user.last_name == 'Имя'
        assert user.role == 'admin'
        
        # Проверяем сообщение
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'Пользователь updated@example.com успешно обновлен' in str(messages[0])
    
    def test_user_edit_view_admin_post_invalid(self, client, admin, user):
        """Тест POST запроса с невалидными данными для администратора"""
        client.force_login(admin)
        
        form_data = {
            'email': 'invalid-email',
            'first_name': 'a' * 151,  # Превышает max_length
            'last_name': 'Имя',
            'role': 'invalid_role'
        }
        
        response = client.post(reverse('users:user_edit', args=[user.id]), data=form_data)
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert not response.context['form'].is_valid()
    
    def test_user_edit_view_redirect_to_list(self, client, admin, user):
        """Тест перенаправления на список пользователей"""
        client.force_login(admin)
        
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'Обновленное',
            'last_name': 'Имя',
            'role': 'user',
            'next': 'users:user_list'
        }
        
        response = client.post(reverse('users:user_edit', args=[user.id]), data=form_data)
        
        assert response.status_code == 302
        assert response.url == reverse('users:user_list')


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.views
class TestProfileView:
    """Тесты для представления профиля"""
    
    def test_profile_view_anonymous(self, client):
        """Тест доступа к профилю для анонимного пользователя"""
        response = client.get(reverse('users:profile'))
        
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_profile_view_authenticated_user(self, client, user):
        """Тест доступа к профилю для аутентифицированного пользователя"""
        client.force_login(user)
        response = client.get(reverse('users:profile'))
        
        assert response.status_code == 200
        assert 'user_obj' in response.context
        assert response.context['user_obj'] == user
        assert 'users/profile.html' in [template.name for template in response.templates]


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.views
class TestUserToggleBlockView:
    """Тесты для представления блокировки/разблокировки пользователя"""
    
    def test_user_toggle_block_view_anonymous(self, client, user):
        """Тест доступа к блокировке для анонимного пользователя"""
        response = client.post(reverse('users:user_toggle_block', args=[user.id]))
        
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_user_toggle_block_view_authenticated_user(self, client, user, multiple_users):
        """Тест доступа к блокировке для обычного пользователя"""
        client.force_login(user)
        response = client.post(reverse('users:user_toggle_block', args=[multiple_users[0].id]))
        
        assert response.status_code == 302
        assert response.url == '/'
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'У вас нет прав для блокировки пользователей' in str(messages[0])
    
    def test_user_toggle_block_view_admin_block_user(self, client, admin, user):
        """Тест блокировки пользователя администратором"""
        client.force_login(admin)
        
        assert user.is_active is True
        
        response = client.post(reverse('users:user_toggle_block', args=[user.id]))
        
        assert response.status_code == 302
        assert response.url == reverse('users:user_list')
        
        # Проверяем, что пользователь заблокирован
        user.refresh_from_db()
        assert user.is_active is False
        
        # Проверяем сообщение
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'Пользователь заблокирован' in str(messages[0])
    
    def test_user_toggle_block_view_admin_unblock_user(self, client, admin, inactive_user):
        """Тест разблокировки пользователя администратором"""
        client.force_login(admin)
        
        assert inactive_user.is_active is False
        
        response = client.post(reverse('users:user_toggle_block', args=[inactive_user.id]))
        
        assert response.status_code == 302
        assert response.url == reverse('users:user_list')
        
        # Проверяем, что пользователь разблокирован
        inactive_user.refresh_from_db()
        assert inactive_user.is_active is True
        
        # Проверяем сообщение
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'Пользователь разблокирован' in str(messages[0])
    
    def test_user_toggle_block_view_admin_block_self(self, client, admin):
        """Тест попытки заблокировать самого себя"""
        client.force_login(admin)
        
        response = client.post(reverse('users:user_toggle_block', args=[admin.id]))
        
        assert response.status_code == 302
        assert response.url == reverse('users:user_list')
        
        # Проверяем, что администратор не заблокирован
        admin.refresh_from_db()
        assert admin.is_active is True
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'Вы не можете заблокировать самого себя' in str(messages[0])
    
    def test_user_toggle_block_view_get_method(self, client, admin, user):
        """Тест GET запроса к блокировке (должен быть запрещен)"""
        client.force_login(admin)
        
        response = client.get(reverse('users:user_toggle_block', args=[user.id]))
        
        assert response.status_code == 405  # Method Not Allowed
