from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    """Модель проекта"""
    
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_projects',
        verbose_name='Создатель'
    )
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Section(models.Model):
    """Модель секции для группировки тест-кейсов"""
    
    name = models.CharField(max_length=200, verbose_name='Название')
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='sections',
        verbose_name='Проект'
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children',
        verbose_name='Родительская секция'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    
    class Meta:
        verbose_name = 'Секция'
        verbose_name_plural = 'Секции'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class TestCase(models.Model):
    """Модель тест-кейса"""
    
    title = models.CharField(max_length=300, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    preconditions = models.TextField(blank=True, verbose_name='Предусловия')
    steps = models.TextField(verbose_name='Шаги выполнения')
    expected_result = models.TextField(verbose_name='Ожидаемый результат')
    
    # Связи
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='test_cases',
        verbose_name='Проект'
    )
    section = models.ForeignKey(
        Section, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='test_cases',
        verbose_name='Секция'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_test_cases',
        verbose_name='Создатель'
    )
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    
    class Meta:
        verbose_name = 'Тест-кейс'
        verbose_name_plural = 'Тест-кейсы'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ProjectMember(models.Model):
    """Модель для управления доступом к проектам"""
    
    ROLE_CHOICES = [
        ('viewer', 'Наблюдатель'),
        ('editor', 'Редактор'),
        ('admin', 'Администратор'),
    ]
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='members',
        verbose_name='Проект'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='project_memberships',
        verbose_name='Пользователь'
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        verbose_name='Роль'
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')
    added_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='added_members',
        verbose_name='Добавлен пользователем'
    )
    
    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проектов'
        unique_together = ('project', 'user')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.project.name} ({self.get_role_display()})"