from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from .managers import PermissionChecker


def require_permission(permission, company_required=True):
    """
    Decorator to require specific permission for a view
    
    Args:
        permission (str): The permission codename (e.g., 'inventory.view_product')
        company_required (bool): Whether the user must be associated with a company
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                return redirect('accounts:login')
            
            # Super users bypass all permission checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Get company from request (could be from URL, session, or user's company)
            company = None
            if company_required:
                # Try to get company from various sources
                if hasattr(request.user, 'company_profile'):
                    company = request.user.company_profile
                elif 'company_id' in kwargs:
                    from apps.core.models import CompanyProfile
                    try:
                        company = CompanyProfile.objects.get(pk=kwargs['company_id'])
                    except CompanyProfile.DoesNotExist:
                        pass
                
                if not company:
                    if request.headers.get('Accept') == 'application/json':
                        return JsonResponse({'error': 'Company context required'}, status=403)
                    messages.error(request, 'Company context is required for this action.')
                    return redirect('core:dashboard')
            
            # Check permission
            if not PermissionChecker.has_permission(request.user, permission, company):
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                messages.error(request, 'You do not have permission to perform this action.')
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_role(role_type, company_required=True):
    """
    Decorator to require specific role for a view
    
    Args:
        role_type (str): The role type (e.g., 'manager', 'accountant')
        company_required (bool): Whether the user must be associated with a company
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                return redirect('accounts:login')
            
            # Super users bypass all role checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Get company from request
            company = None
            if company_required:
                if hasattr(request.user, 'company_profile'):
                    company = request.user.company_profile
                elif 'company_id' in kwargs:
                    from apps.core.models import CompanyProfile
                    try:
                        company = CompanyProfile.objects.get(pk=kwargs['company_id'])
                    except CompanyProfile.DoesNotExist:
                        pass
                
                if not company:
                    if request.headers.get('Accept') == 'application/json':
                        return JsonResponse({'error': 'Company context required'}, status=403)
                    messages.error(request, 'Company context is required for this action.')
                    return redirect('core:dashboard')
            
            # Check role
            if not PermissionChecker.has_role(request.user, role_type, company):
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({'error': 'Insufficient role'}, status=403)
                messages.error(request, f'You need {role_type.replace("_", " ").title()} role to access this page.')
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_company_admin(view_func):
    """Decorator to require company admin role"""
    return require_role('company_admin')(view_func)


def require_manager(view_func):
    """Decorator to require manager role or higher"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Super users bypass all checks
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Get company
        company = None
        if hasattr(request.user, 'company_profile'):
            company = request.user.company_profile
        
        if not company:
            messages.error(request, 'Company context is required for this action.')
            return redirect('core:dashboard')
        
        # Check for manager or higher roles
        from .managers import UserRoleManager
        user_roles = UserRoleManager.get_user_roles(request.user, company)
        role_types = [role.role.role_type for role in user_roles]
        
        # Define role hierarchy (higher roles have more permissions)
        role_hierarchy = {
            'super_admin': 7,
            'company_admin': 6,
            'manager': 5,
            'production_manager': 4,
            'accountant': 3,
            'marketer': 2,
            'store_keeper': 1,
        }
        
        user_max_role = max([role_hierarchy.get(role_type, 0) for role_type in role_types], default=0)
        manager_level = role_hierarchy.get('manager', 0)
        
        if user_max_role < manager_level:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'error': 'Manager role required'}, status=403)
            messages.error(request, 'Manager role or higher is required to access this page.')
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper


def api_permission_required(permission):
    """
    API-specific permission decorator that returns JSON responses
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            # Super users bypass all permission checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            company = None
            if hasattr(request.user, 'company_profile'):
                company = request.user.company_profile
            
            if not PermissionChecker.has_permission(request.user, permission, company):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
