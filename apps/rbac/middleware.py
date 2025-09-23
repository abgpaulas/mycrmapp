from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .managers import PermissionChecker, UserRoleManager


class RBACMiddleware(MiddlewareMixin):
    """
    Middleware to automatically check permissions and add user context
    """
    
    def process_request(self, request):
        """Add user role information to request context"""
        if request.user.is_authenticated:
            # Get user's company and roles
            company = None
            if hasattr(request.user, 'company_profile'):
                company = request.user.company_profile
                request.user_company = company
            
            # Get user's active roles
            user_roles = UserRoleManager.get_user_roles(request.user, company)
            request.user_roles = [role.role.role_type for role in user_roles]
            request.user_role_objects = user_roles
            
            # Add permission checking method to user
            def has_permission(permission):
                return PermissionChecker.has_permission(request.user, permission, company)
            
            def has_role(role_type):
                return PermissionChecker.has_role(request.user, role_type, company)
            
            request.user.has_rbac_permission = has_permission
            request.user.has_rbac_role = has_role
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Check permissions for views that require specific access
        This is a basic implementation - you can extend it based on your needs
        """
        if not request.user.is_authenticated:
            return None
        
        # Skip permission checks for certain URLs
        skip_urls = [
            '/admin/',
            '/auth/',
            '/api/auth/',
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(url) for url in skip_urls):
            return None
        
        # Note: We don't add company to view_kwargs as it can cause conflicts
        # Views should access company via request.user_company instead
        
        return None


class CompanyContextMiddleware(MiddlewareMixin):
    """
    Middleware to ensure users have proper company context
    """
    
    def process_request(self, request):
        """Ensure authenticated users have company context"""
        if request.user.is_authenticated and not request.user.is_superuser:
            # Skip for certain URLs
            skip_urls = [
                '/admin/',
                '/auth/',
                '/api/auth/',
                '/static/',
                '/media/',
                '/dashboard/landing/',
            ]
            
            if any(request.path.startswith(url) for url in skip_urls):
                return None
            
            # Check if user has a company profile
            if not hasattr(request.user, 'company_profile'):
                # Redirect to company setup if no company profile
                if request.path != '/dashboard/company-profile/':
                    messages.warning(
                        request, 
                        'You need to set up your company profile to access this application.'
                    )
                    return redirect('core:company_profile')
            
            # Check if user has any active roles
            elif hasattr(request, 'user_roles') and not request.user_roles:
                # User has company but no roles - they might need to be assigned roles
                if request.path not in ['/dashboard/company-profile/', '/auth/logout/']:
                    messages.warning(
                        request,
                        'You have been registered but no roles have been assigned yet. '
                        'Please contact your administrator.'
                    )
                    return redirect('core:company_profile')
        
        return None
