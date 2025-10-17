from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели User"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с email-аутентификацией"""
    
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('user', 'Пользователь'),
    ]
    
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Фамилия')
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='user',
        verbose_name='Роль'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    last_login_date = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='Дата последней авторизации'
    )
    
    # Убираем username, используем email
    username = None
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_blocked(self):
        return not self.is_active
    
    @property
    def full_name(self):
        """Возвращает полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email
