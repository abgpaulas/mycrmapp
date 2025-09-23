from django.apps import AppConfig


class RbacConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rbac'
    verbose_name = 'Role-Based Access Control'
    
    def ready(self):
        """Initialize RBAC when the app is ready"""
        # Import signal handlers
        from . import signals