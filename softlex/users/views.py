from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, RegistrationForm


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
    if request.user.is_authenticated:
        return redirect('/')
    
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