from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from .models import Project, TestCase
from .forms import ProjectForm, TestCaseForm
from .mixins import UserPermissionMixin


def home_view(request):
    """Главная страница"""
    return render(request, 'home.html')


@login_required
def project_list(request):
    """Список проектов"""
    # Проверяем права доступа
    if request.user.is_blocked:
        messages.error(request, 'Ваш аккаунт заблокирован')
        return redirect('users:login')
    
    projects = Project.objects.filter(created_by=request.user)
    
    # Обработка создания проекта
    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Проект "{project.name}" успешно создан!')
            return redirect('testcases:project_list')
        else:
            messages.error(request, 'Ошибка при создании проекта. Проверьте данные.')
    else:
        form = ProjectForm(user=request.user)
    
    return render(request, 'testcases/project_list.html', {
        'projects': projects,
        'form': form
    })


@login_required
def project_detail(request, pk):
    """Детальная страница проекта"""
    # Проверяем права доступа
    if request.user.is_blocked:
        messages.error(request, 'Ваш аккаунт заблокирован')
        return redirect('users:login')
    
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    test_cases = TestCase.objects.filter(project=project)
    
    # Обработка создания тест-кейса
    if request.method == 'POST':
        form = TestCaseForm(request.POST, user=request.user)
        if form.is_valid():
            test_case = form.save()
            messages.success(request, f'Тест-кейс "{test_case.title}" успешно создан!')
            return redirect('testcases:project_detail', pk=project.pk)
        else:
            messages.error(request, 'Ошибка при создании тест-кейса. Проверьте данные.')
    else:
        form = TestCaseForm(user=request.user, initial={'project': project})
    
    return render(request, 'testcases/project_detail.html', {
        'project': project,
        'test_cases': test_cases,
        'form': form
    })


@login_required
def project_edit(request, pk):
    """Редактирование проекта"""
    # Проверяем права доступа
    if request.user.is_blocked:
        messages.error(request, 'Ваш аккаунт заблокирован')
        return redirect('users:login')
    
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Проект "{project.name}" успешно обновлен!')
            return redirect('testcases:project_detail', pk=project.pk)
        else:
            messages.error(request, 'Ошибка при обновлении проекта. Проверьте данные.')
    else:
        form = ProjectForm(instance=project, user=request.user)
    
    return render(request, 'testcases/project_edit.html', {
        'form': form,
        'project': project
    })


@login_required
def project_delete(request, pk):
    """Удаление проекта"""
    # Проверяем права доступа
    if request.user.is_blocked:
        messages.error(request, 'Ваш аккаунт заблокирован')
        return redirect('users:login')
    
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Проект "{project_name}" успешно удален!')
        return redirect('testcases:project_list')
    
    return render(request, 'testcases/project_confirm_delete.html', {
        'project': project
    })


@login_required
def testcase_list(request):
    """Список тест-кейсов"""
    # Проверяем права доступа
    if request.user.is_blocked:
        messages.error(request, 'Ваш аккаунт заблокирован')
        return redirect('users:login')
    
    test_cases = TestCase.objects.filter(created_by=request.user)
    
    # Обработка создания тест-кейса
    if request.method == 'POST':
        form = TestCaseForm(request.POST, user=request.user)
        if form.is_valid():
            test_case = form.save()
            messages.success(request, f'Тест-кейс "{test_case.title}" успешно создан!')
            return redirect('testcases:testcase_list')
        else:
            messages.error(request, 'Ошибка при создании тест-кейса. Проверьте данные.')
    else:
        form = TestCaseForm(user=request.user)
    
    return render(request, 'testcases/testcase_list.html', {
        'test_cases': test_cases,
        'form': form
    })


@login_required
def testcase_detail(request, pk):
    """Детальная страница тест-кейса"""
    # Проверяем права доступа
    if request.user.is_blocked:
        messages.error(request, 'Ваш аккаунт заблокирован')
        return redirect('users:login')
    
    test_case = get_object_or_404(TestCase, pk=pk, created_by=request.user)
    return render(request, 'testcases/testcase_detail.html', {
        'test_case': test_case
    })


@login_required
def testcase_edit(request, pk):
    """Редактирование тест-кейса"""
    # Проверяем права доступа
    if request.user.is_blocked:
        messages.error(request, 'Ваш аккаунт заблокирован')
        return redirect('users:login')
    
    test_case = get_object_or_404(TestCase, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = TestCaseForm(request.POST, instance=test_case, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Тест-кейс "{test_case.title}" успешно обновлен!')
            return redirect('testcases:testcase_detail', pk=test_case.pk)
        else:
            messages.error(request, 'Ошибка при обновлении тест-кейса. Проверьте данные.')
    else:
        form = TestCaseForm(instance=test_case, user=request.user)
    
    return render(request, 'testcases/testcase_edit.html', {
        'form': form,
        'test_case': test_case
    })


@login_required
def testcase_delete(request, pk):
    """Удаление тест-кейса"""
    # Проверяем права доступа
    if request.user.is_blocked:
        messages.error(request, 'Ваш аккаунт заблокирован')
        return redirect('users:login')
    
    test_case = get_object_or_404(TestCase, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        test_case_title = test_case.title
        project_pk = test_case.project.pk
        test_case.delete()
        messages.success(request, f'Тест-кейс "{test_case_title}" успешно удален!')
        return redirect('testcases:project_detail', pk=project_pk)
    
    return render(request, 'testcases/testcase_confirm_delete.html', {
        'test_case': test_case
    })