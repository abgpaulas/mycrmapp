from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.core.models import CompanyProfile

User = get_user_model()


class Role(models.Model):
    """
    Defines roles within the system
    """
    ROLE_TYPES = [
        ('super_admin', 'Super Admin'),
        ('company_admin', 'Company Admin'),
        ('manager', 'Manager'),
        ('production_manager', 'Production Manager'),
        ('accountant', 'Accountant'),
        ('marketer', 'Marketer'),
        ('store_keeper', 'Store Keeper'),
        ('viewer', 'Viewer'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    role_type = models.CharField(max_length=50, choices=ROLE_TYPES, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        # Ensure role_type is unique
        if Role.objects.filter(role_type=self.role_type).exclude(pk=self.pk).exists():
            raise ValidationError(f'Role type "{self.role_type}" already exists.')


class UserRole(models.Model):
    """
    Links users to roles within specific companies
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_roles')
    assigned_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        unique_together = ['user', 'company', 'role']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.role.name} at {self.company.company_name}'
    
    def clean(self):
        # Prevent duplicate role assignments
        if UserRole.objects.filter(
            user=self.user, 
            company=self.company, 
            role=self.role,
            is_active=True
        ).exclude(pk=self.pk).exists():
            raise ValidationError('User already has this role in this company.')
    
    def is_expired(self):
        """Check if the role assignment has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class PermissionGroup(models.Model):
    """
    Groups related permissions for easier management
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Permission Group'
        verbose_name_plural = 'Permission Groups'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CompanyPermission(models.Model):
    """
    Company-specific permissions that can be granted to users
    """
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    granted_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Company Permission'
        verbose_name_plural = 'Company Permissions'
        unique_together = ['company', 'permission']
        ordering = ['permission__content_type', 'permission__codename']
    
    def __str__(self):
        return f'{self.company.company_name} - {self.permission}'