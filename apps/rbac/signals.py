from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from .models import Role, UserRole
from .managers import RoleManager

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_roles_on_user_creation(sender, instance, created, **kwargs):
    """Create default roles when the first user is created"""
    # Temporarily disabled to fix Render deployment issue
    # TODO: Re-enable after fixing database permissions
    return
    
    if created and User.objects.count() == 1:
        # Only create default roles for the first user (superuser)
        try:
            RoleManager.create_default_roles()
        except Exception as e:
            # Log the error but don't prevent user creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating default roles: {e}")
            # Continue with user creation even if role creation fails


@receiver(post_save, sender=UserRole)
def log_role_assignment(sender, instance, created, **kwargs):
    """Log role assignments for audit purposes"""
    if created:
        # You can add logging or notifications here
        pass


@receiver(post_delete, sender=UserRole)
def log_role_revocation(sender, instance, **kwargs):
    """Log role revocations for audit purposes"""
    # You can add logging or notifications here
    pass
