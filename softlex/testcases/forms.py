from django import forms
from .models import Project, TestCase


class ProjectForm(forms.ModelForm):
    """Форма для создания/редактирования проекта"""
    
    class Meta:
        model = Project
        fields = ['name', 'description']
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
    
    def save(self, commit=True):
        project = super().save(commit=False)
        if self.user:
            project.created_by = self.user
        if commit:
            project.save()
        return project


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
        
        # Фильтруем проекты только для текущего пользователя
        if self.user:
            self.fields['project'].queryset = Project.objects.filter(created_by=self.user)
    
    def save(self, commit=True):
        test_case = super().save(commit=False)
        if self.user:
            test_case.created_by = self.user
        if commit:
            test_case.save()
        return test_case
