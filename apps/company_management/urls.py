from django.urls import path
from . import views

app_name = 'company_management'

urlpatterns = [
    # Company management views
    path('', views.company_list, name='company_list'),
    path('create/', views.company_create, name='company_create'),
    path('<int:pk>/', views.company_detail, name='company_detail'),
    path('<int:pk>/edit/', views.company_edit, name='company_edit'),
    
    # Company user management
    path('users/assign/', views.company_user_assign, name='company_user_assign'),
    path('users/<int:pk>/remove/', views.company_user_remove, name='company_user_remove'),
    
    # AJAX endpoints
    path('ajax/companies/', views.ajax_company_list, name='ajax_company_list'),
    path('ajax/companies/create/', views.ajax_company_create, name='ajax_company_create'),
    path('ajax/users/assign/', views.ajax_company_user_assign, name='ajax_company_user_assign'),
    path('ajax/users/', views.ajax_get_users, name='ajax_get_users'),
    path('ajax/roles/', views.ajax_get_roles, name='ajax_get_roles'),
]
