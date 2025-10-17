from django.db.models import Q
from .models import Project, ProjectMember


def has_project_access(user, project, min_role=None):
    """
    Проверяет, есть ли у пользователя доступ к проекту
    
    Args:
        user: Пользователь
        project: Проект
        min_role: Минимальная требуемая роль ('viewer', 'editor', 'admin')
    
    Returns:
        bool: True если есть доступ, False иначе
    """
    # Системные администраторы имеют полный доступ ко всем проектам
    if user.is_admin:
        return True
    
    # Проверяем, есть ли пользователь в участниках проекта
    try:
        membership = ProjectMember.objects.get(project=project, user=user)
        
        if min_role is None:
            return True
        
        # Проверяем уровень доступа
        role_hierarchy = {'viewer': 1, 'editor': 2, 'admin': 3}
        user_level = role_hierarchy.get(membership.role, 0)
        required_level = role_hierarchy.get(min_role, 0)
        
        return user_level >= required_level
        
    except ProjectMember.DoesNotExist:
        return False


def get_user_project_role(user, project):
    """
    Получает роль пользователя в проекте
    
    Args:
        user: Пользователь
        project: Проект
    
    Returns:
        str: Роль пользователя или None если нет доступа
    """
    # Системные администраторы имеют роль администратора во всех проектах
    if user.is_admin:
        return 'admin'
    
    try:
        membership = ProjectMember.objects.get(project=project, user=user)
        return membership.role
    except ProjectMember.DoesNotExist:
        return None


def get_accessible_projects(user):
    """
    Получает все проекты, к которым у пользователя есть доступ
    
    Args:
        user: Пользователь
    
    Returns:
        QuerySet: Проекты, доступные пользователю
    """
    # Системные администраторы видят все проекты
    if user.is_admin:
        return Project.objects.all()
    
    # Получаем проекты, где пользователь является участником
    return Project.objects.filter(members__user=user).distinct()


def can_edit_project(user, project):
    """
    Проверяет, может ли пользователь редактировать проект
    
    Args:
        user: Пользователь
        project: Проект
    
    Returns:
        bool: True если может редактировать, False иначе
    """
    return has_project_access(user, project, min_role='admin')


def can_edit_testcase(user, testcase):
    """
    Проверяет, может ли пользователь редактировать тест-кейс
    
    Args:
        user: Пользователь
        testcase: Тест-кейс
    
    Returns:
        bool: True если может редактировать, False иначе
    """
    return has_project_access(user, testcase.project, min_role='editor')


def can_view_project(user, project):
    """
    Проверяет, может ли пользователь просматривать проект
    
    Args:
        user: Пользователь
        project: Проект
    
    Returns:
        bool: True если может просматривать, False иначе
    """
    return has_project_access(user, project, min_role='viewer')
