from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('', views.user_list_view, name='user_list'),
    path('<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('<int:user_id>/edit/', views.user_edit_view, name='user_edit'),
    path('<int:user_id>/toggle-block/', views.user_toggle_block_view, name='user_toggle_block'),
]