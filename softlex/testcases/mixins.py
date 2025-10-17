from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class UserPermissionMixin(LoginRequiredMixin):
    """Миксин для проверки прав доступа пользователя"""
    
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь не заблокирован
        if request.user.is_blocked:
            raise PermissionDenied("Ваш аккаунт заблокирован")
        
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    """Миксин для проверки прав администратора"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            raise PermissionDenied("Недостаточно прав для выполнения этого действия")
        
        return super().dispatch(request, *args, **kwargs)
