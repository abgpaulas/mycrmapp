from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Role, UserRole, PermissionGroup, CompanyPermission
from .managers import RoleManager, UserRoleManager

User = get_user_model()


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'role_type', 'permissions_count', 'is_active', 'created_at']
    list_filter = ['role_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'role_type', 'description', 'is_active')
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def permissions_count(self, obj):
        return obj.permissions.count()
    permissions_count.short_description = 'Permissions Count'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('permissions')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'company_name', 'role_name', 'assigned_by_name', 'assigned_at', 'status', 'expires_at']
    list_filter = ['role__role_type', 'is_active', 'assigned_at', 'expires_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'company__company_name', 'role__name']
    readonly_fields = ['assigned_at']
    autocomplete_fields = ['user', 'assigned_by']
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('user', 'company', 'role', 'assigned_by')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at', 'assigned_at')
        }),
    )
    
    def user_name(self, obj):
        return obj.user.get_full_name()
    user_name.short_description = 'User'
    user_name.admin_order_field = 'user__first_name'
    
    def company_name(self, obj):
        return obj.company.company_name
    company_name.short_description = 'Company'
    company_name.admin_order_field = 'company__company_name'
    
    def role_name(self, obj):
        return obj.role.name
    role_name.short_description = 'Role'
    role_name.admin_order_field = 'role__name'
    
    def assigned_by_name(self, obj):
        if obj.assigned_by:
            return obj.assigned_by.get_full_name()
        return 'System'
    assigned_by_name.short_description = 'Assigned By'
    assigned_by_name.admin_order_field = 'assigned_by__first_name'
    
    def status(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        elif not obj.is_active:
            return format_html('<span style="color: orange;">Inactive</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')
    status.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'company', 'role', 'assigned_by')


@admin.register(PermissionGroup)
class PermissionGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'permissions_count', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']
    readonly_fields = ['created_at']
    
    def permissions_count(self, obj):
        return obj.permissions.count()
    permissions_count.short_description = 'Permissions Count'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('permissions')


@admin.register(CompanyPermission)
class CompanyPermissionAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'permission_name', 'granted_by_name', 'granted_at', 'is_active']
    list_filter = ['is_active', 'granted_at', 'permission__content_type']
    search_fields = ['company__company_name', 'permission__name', 'permission__codename']
    readonly_fields = ['granted_at']
    autocomplete_fields = ['granted_by']
    
    def company_name(self, obj):
        return obj.company.company_name
    company_name.short_description = 'Company'
    company_name.admin_order_field = 'company__company_name'
    
    def permission_name(self, obj):
        return f"{obj.permission.content_type.app_label}.{obj.permission.codename}"
    permission_name.short_description = 'Permission'
    permission_name.admin_order_field = 'permission__codename'
    
    def granted_by_name(self, obj):
        if obj.granted_by:
            return obj.granted_by.get_full_name()
        return 'System'
    granted_by_name.short_description = 'Granted By'
    granted_by_name.admin_order_field = 'granted_by__first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'permission', 'granted_by')


# Custom admin actions
@admin.action(description='Create default roles')
def create_default_roles(modeladmin, request, queryset):
    """Admin action to create default roles"""
    try:
        created_roles = RoleManager.create_default_roles()
        modeladmin.message_user(
            request,
            f'Successfully created {len(created_roles)} default roles.',
            level='SUCCESS'
        )
    except Exception as e:
        modeladmin.message_user(
            request,
            f'Error creating default roles: {str(e)}',
            level='ERROR'
        )


@admin.action(description='Assign Company Admin role to selected users')
def assign_company_admin_role(modeladmin, request, queryset):
    """Admin action to assign company admin role to users"""
    if not request.user.is_superuser:
        modeladmin.message_user(
            request,
            'Only super users can assign company admin roles.',
            level='ERROR'
        )
        return
    
    assigned_count = 0
    for user in queryset:
        try:
            # Get user's company profile
            if hasattr(user, 'company_profile'):
                user_role, created = UserRoleManager.assign_role(
                    user=user,
                    company=user.company_profile,
                    role_type='company_admin',
                    assigned_by=request.user
                )
                if created:
                    assigned_count += 1
            else:
                modeladmin.message_user(
                    request,
                    f'User {user.get_full_name()} does not have a company profile.',
                    level='WARNING'
                )
        except Exception as e:
            modeladmin.message_user(
                request,
                f'Error assigning role to {user.get_full_name()}: {str(e)}',
                level='ERROR'
            )
    
    modeladmin.message_user(
        request,
        f'Successfully assigned company admin role to {assigned_count} users.',
        level='SUCCESS'
    )


# Add the actions to the User admin
admin.site.add_action(assign_company_admin_role, name='assign_company_admin_role')