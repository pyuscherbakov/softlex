from django import forms
from django.contrib.auth import get_user_model
import json
from .models import Project, TestCase, ProjectMember
from .utils import get_accessible_projects

User = get_user_model()


class ProjectForm(forms.ModelForm):
    """Форма для создания/редактирования проекта"""
    
    # Поля для управления доступом
    members_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        help_text='JSON данные участников проекта'
    )
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'members_data']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название проекта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите описание проекта'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Если редактируем существующий проект, загружаем текущих участников
        if self.instance and self.instance.pk:
            self.load_members_data()
    
    def load_members_data(self):
        """Загружает данные участников проекта"""
        members = ProjectMember.objects.filter(project=self.instance).exclude(user=self.instance.created_by)
        members_data = []
        for member in members:
            members_data.append({
                'user_id': member.user.id,
                'user_email': member.user.email,
                'role': member.role
            })
        self.fields['members_data'].initial = json.dumps(members_data)
    
    def clean_members_data(self):
        """Валидация данных участников"""
        members_data = self.cleaned_data.get('members_data', '[]')
        try:
            members = json.loads(members_data)
        except (json.JSONDecodeError, TypeError):
            members = []
        
        # Валидируем каждую запись участника
        for member in members:
            if not isinstance(member, dict):
                raise forms.ValidationError('Неверный формат данных участников')
            
            required_fields = ['user_id', 'user_email', 'role']
            for field in required_fields:
                if field not in member:
                    raise forms.ValidationError(f'Отсутствует поле {field} в данных участника')
            
            # Проверяем валидность роли
            valid_roles = ['viewer', 'editor', 'admin']
            if member['role'] not in valid_roles:
                raise forms.ValidationError(f'Неверная роль: {member["role"]}')
        
        return members_data
    
    def save(self, commit=True):
        project = super().save(commit=False)
        if self.user:
            project.created_by = self.user
        if commit:
            project.save()
            self.save_members(project)
        return project
    
    def save_members(self, project):
        """Сохраняет участников проекта"""
        # Создаем или обновляем запись для создателя как администратора
        ProjectMember.objects.get_or_create(
            project=project,
            user=project.created_by,
            defaults={
                'role': 'admin',
                'added_by': self.user
            }
        )
        
        # Обрабатываем участников из формы
        members_data = self.cleaned_data.get('members_data', '[]')
        try:
            members = json.loads(members_data)
        except (json.JSONDecodeError, TypeError):
            members = []
        
        # Получаем текущих участников (кроме создателя)
        current_members = ProjectMember.objects.filter(project=project).exclude(user=project.created_by)
        current_member_ids = set(current_members.values_list('user_id', flat=True))
        
        # Получаем ID пользователей из формы
        form_member_ids = set()
        for member in members:
            if member.get('user_id'):
                form_member_ids.add(int(member['user_id']))
        
        # Удаляем участников, которых нет в форме
        members_to_remove = current_member_ids - form_member_ids
        ProjectMember.objects.filter(
            project=project,
            user_id__in=members_to_remove
        ).delete()
        
        # Добавляем или обновляем участников из формы
        for member_data in members:
            user_id = member_data.get('user_id')
            user_email = member_data.get('user_email')
            role = member_data.get('role', 'viewer')
            
            # Если user_id не указан, ищем пользователя по email
            if not user_id and user_email:
                try:
                    user = User.objects.get(email=user_email)
                    user_id = user.id
                except User.DoesNotExist:
                    continue  # Пропускаем несуществующих пользователей
            
            if user_id:
                ProjectMember.objects.update_or_create(
                    project=project,
                    user_id=user_id,
                    defaults={
                        'role': role,
                        'added_by': self.user
                    }
                )


class TestCaseForm(forms.ModelForm):
    """Форма для создания/редактирования тест-кейса"""
    
    class Meta:
        model = TestCase
        fields = ['title', 'description', 'preconditions', 'steps', 'expected_result', 'project']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название тест-кейса'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Введите описание тест-кейса'
            }),
            'preconditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Введите предусловия'
            }),
            'steps': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Введите шаги выполнения'
            }),
            'expected_result': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите ожидаемый результат'
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Фильтруем проекты по доступным для текущего пользователя
        if self.user:
            self.fields['project'].queryset = get_accessible_projects(self.user)
    
    def save(self, commit=True):
        test_case = super().save(commit=False)
        if self.user:
            test_case.created_by = self.user
        if commit:
            test_case.save()
        return test_case
