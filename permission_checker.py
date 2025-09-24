
class PermissionChecker:
    """
    Utility class for checking user permissions
    """
    
    @staticmethod
    def has_permission(user, permission, company=None):
        """Check if user has a specific permission"""
        # Super users have all permissions
        if user.is_superuser:
            return True
        
        # Check Django's built-in permissions
        if user.has_perm(permission):
            return True
        
        # Check company-specific permissions
        if company:
            user_roles = UserRoleManager.get_user_roles(user, company)
            for user_role in user_roles:
                if user_role.is_expired():
                    continue
                if user_role.role.permissions.filter(codename=permission.split('.')[-1]).exists():
                    return True
        
        return False
    
    @staticmethod
    def has_role(user, role_type, company=None):
        """Check if user has a specific role"""
        # Super users have all roles
        if user.is_superuser:
            return True
        
        return UserRoleManager.has_role(user, role_type, company)
    
    @staticmethod
    def get_user_permissions(user, company=None):
        """Get all permissions for a user"""
        permissions = set()
        
        # Super users have all permissions
        if user.is_superuser:
            from django.contrib.auth.models import Permission
            permissions.update(Permission.objects.values_list('codename', flat=True))
            return permissions
        
        # Add Django built-in permissions
        permissions.update(user.get_all_permissions())
        
        # Add role-based permissions
        if company:
            user_roles = UserRoleManager.get_user_roles(user, company)
            for user_role in user_roles:
                if not user_role.is_expired():
                    permissions.update(user_role.role.permissions.values_list('codename', flat=True))
        
        return permissions
