from django import template
from django.contrib.auth import get_user_model
from apps.rbac.managers import PermissionChecker

User = get_user_model()
register = template.Library()


@register.simple_tag(takes_context=True)
def has_permission(context, permission):
    """Check if user has specific permission"""
    request = context['request']
    if not request.user.is_authenticated:
        return False
    
    # Super users have all permissions
    if request.user.is_superuser:
        return True
    
    company = None
    if hasattr(request.user, 'company_profile'):
        company = request.user.company_profile
    
    return PermissionChecker.has_permission(request.user, permission, company)


@register.simple_tag(takes_context=True)
def has_role(context, role_type):
    """Check if user has specific role"""
    request = context['request']
    if not request.user.is_authenticated:
        return False
    
    # Super users have all roles
    if request.user.is_superuser:
        return True
    
    company = None
    if hasattr(request.user, 'company_profile'):
        company = request.user.company_profile
    
    return PermissionChecker.has_role(request.user, role_type, company)


@register.simple_tag(takes_context=True)
def has_any_role(context, *role_types):
    """Check if user has any of the specified roles"""
    request = context['request']
    if not request.user.is_authenticated:
        return False
    
    # Super users have all roles
    if request.user.is_superuser:
        return True
    
    company = None
    if hasattr(request.user, 'company_profile'):
        company = request.user.company_profile
    
    for role_type in role_types:
        if PermissionChecker.has_role(request.user, role_type, company):
            return True
    
    return False


@register.simple_tag(takes_context=True)
def user_roles(context):
    """Get user's active roles"""
    request = context['request']
    if not request.user.is_authenticated:
        return []
    
    company = None
    if hasattr(request.user, 'company_profile'):
        company = request.user.company_profile
    
    from apps.rbac.managers import UserRoleManager
    user_roles = UserRoleManager.get_user_roles(request.user, company)
    return [role.role.role_type for role in user_roles]


@register.inclusion_tag('rbac/role_based_menu.html', takes_context=True)
def role_based_menu(context, menu_item):
    """Render menu item based on user roles and permissions"""
    request = context['request']
    
    # Check if user has required permission
    if 'permission' in menu_item:
        if not has_permission(context, menu_item['permission']):
            return {'show': False}
    
    # Check if user has required role
    if 'role' in menu_item:
        if not has_role(context, menu_item['role']):
            return {'show': False}
    
    # Check if user has any of the required roles
    if 'any_role' in menu_item:
        if not has_any_role(context, *menu_item['any_role']):
            return {'show': False}
    
    # Check if user has all required roles
    if 'all_roles' in menu_item:
        for role in menu_item['all_roles']:
            if not has_role(context, role):
                return {'show': False}
    
    return {
        'show': True,
        'menu_item': menu_item,
        'request': request
    }


@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of arg[0] with arg[1] in value.
    Usage: {{ value|replace:"old,new" }}
    """
    if not value:
        return value
    
    if ',' not in arg:
        return value
    
    old, new = arg.split(',', 1)
    return value.replace(old, new)


@register.filter
def format_permission_name(value):
    """
    Format permission name by replacing underscores with spaces and title casing
    """
    if not value:
        return value
    
    return value.replace('_', ' ').title()
