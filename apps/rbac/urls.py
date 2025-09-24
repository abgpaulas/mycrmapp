from django.urls import path
from . import views

app_name = 'rbac'

urlpatterns = [
    # Role Management Views
    path('', views.role_management, name='role_management'),
    path('assign-role/', views.assign_role, name='assign_role'),
    path('revoke-role/<int:user_role_id>/', views.revoke_role, name='revoke_role'),
    path('roles/', views.role_list, name='role_list'),
    path('user/<int:user_id>/history/', views.user_role_history, name='user_role_history'),
    path('my-permissions/', views.my_permissions, name='my_permissions'),
    
    # Super Admin User Management Views
    path('super-admin/users/', views.super_admin_user_management, name='super_admin_user_management'),
    path('super-admin/users/create/', views.create_user, name='create_user'),
    path('super-admin/users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('super-admin/users/bulk-create/', views.bulk_create_users, name='bulk_create_users'),
    
    # API Endpoints
    path('api/user-roles/', views.api_user_roles, name='api_user_roles'),
    path('api/assign-role/', views.api_assign_role, name='api_assign_role'),
    path('api/revoke-role/<int:user_role_id>/', views.api_revoke_role, name='api_revoke_role'),
    path('api/roles/', views.api_roles, name='api_roles'),
    path('api/search-users/', views.search_users, name='search_users'),
    
    # Super Admin API Endpoints
    path('api/super-admin/users/', views.api_users_list, name='api_users_list'),
    path('api/super-admin/users/create/', views.api_create_user, name='api_create_user'),
    path('api/super-admin/users/<int:user_id>/edit/', views.api_edit_user, name='api_edit_user'),
    path('api/super-admin/users/<int:user_id>/delete/', views.api_delete_user, name='api_delete_user'),
]
