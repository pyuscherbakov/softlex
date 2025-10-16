from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import LoginForm, RegistrationForm, UserEditForm
from .models import User


def login_view(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            from django.contrib.auth import authenticate
            user = authenticate(email=email, password=password)
            if user:
                # Обновляем дату последней авторизации
                user.last_login_date = timezone.now()
                user.save(update_fields=['last_login_date'])
                login(request, user)
                messages.success(request, 'Вы успешно вошли в систему')
                return redirect('/')
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('users:login')


def register_view(request):
    """Регистрация"""
    # Если пользователь не аутентифицирован, показываем обычную регистрацию
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно')
                return redirect('/')
        else:
            form = RegistrationForm()
        
        return render(request, 'users/register.html', {'form': form})
    
    # Если пользователь аутентифицирован, проверяем права администратора
    if not request.user.is_admin:
        messages.error(request, 'У вас нет прав для создания пользователей')
        return redirect('/')
    
    # Администратор может создавать пользователей
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Пользователь {user.email} успешно создан')
            return redirect('users:user_list')
    else:
        form = RegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


@login_required
def user_list_view(request):
    """Список всех пользователей"""
    # Проверяем права доступа
    if not request.user.is_admin:
        messages.error(request, 'У вас нет прав для просмотра списка пользователей')
        return redirect('/')
    
    # Получаем параметры поиска и фильтрации
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    # Базовый запрос
    users = User.objects.all().order_by('-date_joined')
    
    # Применяем фильтры
    if search:
        users = users.filter(
            Q(email__icontains=search) | 
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search)
        )
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Пагинация
    paginator = Paginator(users, 20)  # 20 пользователей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'role_filter': role_filter,
        'role_choices': User.ROLE_CHOICES,
    }
    
    return render(request, 'users/user_list.html', context)


@login_required
def user_detail_view(request, user_id):
    """Детальная информация о пользователе"""
    if not request.user.is_admin:
        messages.error(request, 'У вас нет прав для просмотра информации о пользователях')
        return redirect('/')
    
    user = get_object_or_404(User, id=user_id)
    
    context = {
        'user_obj': user,  # user_obj чтобы не конфликтовать с request.user
    }
    
    return render(request, 'users/user_detail.html', context)


@login_required
def user_edit_view(request, user_id):
    """Редактирование пользователя"""
    if not request.user.is_admin:
        messages.error(request, 'У вас нет прав для редактирования пользователей')
        return redirect('/')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Пользователь {user.email} успешно обновлен')
            # Перенаправляем на ту же страницу, откуда пришли
            next_url = request.POST.get('next', request.GET.get('next', 'users:user_detail'))
            if next_url == 'users:user_detail':
                return redirect('users:user_detail', user_id=user.id)
            elif next_url == 'users:user_list':
                return redirect('users:user_list')
            else:
                return redirect(next_url)
    else:
        form = UserEditForm(instance=user)
    
    context = {
        'form': form,
        'user_obj': user,
    }
    
    return render(request, 'users/user_edit.html', context)


@login_required
def profile_view(request):
    """Просмотр собственного профиля пользователя"""
    context = {
        'user_obj': request.user,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
@require_http_methods(["POST"])
def user_toggle_block_view(request, user_id):
    """Блокировка/разблокировка пользователя"""
    if not request.user.is_admin:
        messages.error(request, 'У вас нет прав для блокировки пользователей')
        return redirect('/')
    
    user = get_object_or_404(User, id=user_id)
    
    # Нельзя заблокировать самого себя
    if user == request.user:
        messages.error(request, 'Вы не можете заблокировать самого себя')
        return redirect('users:user_list')
    
    # Переключаем статус блокировки
    if user.is_active:
        user.is_active = False
        action = 'заблокирован'
    else:
        user.is_active = True
        action = 'разблокирован'
    
    user.save()
    messages.success(request, f'Пользователь {user.email} {action}')
    
    return redirect('users:user_list')