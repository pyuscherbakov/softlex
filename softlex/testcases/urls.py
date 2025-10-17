from django.urls import path
from . import views

app_name = 'testcases'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('testcases/', views.testcase_list, name='testcase_list'),
    path('testcases/<int:pk>/', views.testcase_detail, name='testcase_detail'),
    path('testcases/<int:pk>/edit/', views.testcase_edit, name='testcase_edit'),
    path('testcases/<int:pk>/delete/', views.testcase_delete, name='testcase_delete'),
]
