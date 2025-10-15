from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User


class LoginForm(forms.Form):
    """Форма входа"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        label='Пароль'
    )
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Неверный email или пароль')
            if not user.is_active:
                raise forms.ValidationError('Аккаунт заблокирован')
            if user.is_blocked:
                raise forms.ValidationError('Аккаунт заблокирован')
        
        return self.cleaned_data


class RegistrationForm(UserCreationForm):
    """Форма регистрации"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        }),
        label='Email'
    )
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email


class UserEditForm(forms.ModelForm):
    """Форма редактирования пользователя"""
    
    # исключаем заблокированных пользователей
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('user', 'Пользователь'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Роль'
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'is_active': 'Активен',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Проверяем, что email уникален, исключая текущего пользователя
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email
    
