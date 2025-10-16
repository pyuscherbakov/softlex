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
        label='Email',
        error_messages={
            'required': 'Поле email обязательно для заполнения',
            'invalid': 'Введите корректный email адрес'
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        label='Пароль',
        error_messages={
            'required': 'Поле пароль обязательно для заполнения'
        }
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
        label='Email',
        error_messages={
            'required': 'Поле email обязательно для заполнения',
            'invalid': 'Введите корректный email адрес'
        }
    )
    
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя'
        }),
        label='Имя',
        required=False,
        error_messages={
            'max_length': 'Имя не должно превышать 30 символов'
        }
    )
    
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию'
        }),
        label='Фамилия',
        required=False,
        error_messages={
            'max_length': 'Фамилия не должна превышать 30 символов'
        }
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
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
        
        # Русские сообщения для полей пароля
        self.fields['password1'].error_messages.update({
            'required': 'Поле пароль обязательно для заполнения',
            'min_length': 'Пароль должен содержать минимум 8 символов',
            'password_too_common': 'Пароль слишком простой',
            'password_entirely_numeric': 'Пароль не может состоять только из цифр'
        })
        
        self.fields['password2'].error_messages.update({
            'required': 'Поле подтверждения пароля обязательно для заполнения'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2


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
        label='Роль',
        error_messages={
            'required': 'Поле роль обязательно для заполнения',
            'invalid_choice': 'Выберите корректную роль'
        }
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']
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
        }
        labels = {
            'email': 'Email',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        error_messages = {
            'email': {
                'required': 'Поле email обязательно для заполнения',
                'invalid': 'Введите корректный email адрес'
            },
            'first_name': {
                'max_length': 'Имя не должно превышать 30 символов'
            },
            'last_name': {
                'max_length': 'Фамилия не должна превышать 30 символов'
            }
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Проверяем, что email уникален, исключая текущего пользователя
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email
    
