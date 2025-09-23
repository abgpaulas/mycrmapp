from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils import timezone
from apps.rbac.models import Role

User = get_user_model()


class Company(models.Model):
    """
    Model for managing companies in the system
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending Approval'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Company Name')
    email = models.EmailField(verbose_name='Company Email')
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )],
        verbose_name='Phone Number'
    )
    address = models.TextField(verbose_name='Address')
    website = models.URLField(blank=True, null=True, verbose_name='Website')
    
    # Company details
    registration_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='Registration Number')
    tax_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tax ID')
    industry = models.CharField(max_length=100, blank=True, null=True, verbose_name='Industry')
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_companies', verbose_name='Created By')
    
    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('company_management:company_detail', kwargs={'pk': self.pk})


class CompanyUser(models.Model):
    """
    Model for linking users to companies with specific roles
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_users', verbose_name='User')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_users', verbose_name='Company')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='company_users', verbose_name='Role')
    
    # Assignment details
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_company_users', verbose_name='Assigned By')
    assigned_at = models.DateTimeField(default=timezone.now, verbose_name='Assigned At')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_primary = models.BooleanField(default=False, verbose_name='Primary Contact')
    
    # Optional expiration
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Expires At')
    
    class Meta:
        verbose_name = 'Company User'
        verbose_name_plural = 'Company Users'
        unique_together = ['user', 'company']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.role.name} at {self.company.name}'
    
    def is_expired(self):
        """Check if the assignment has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class CompanySettings(models.Model):
    """
    Model for company-specific settings
    """
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='settings', verbose_name='Company')
    
    # Financial settings
    default_currency = models.CharField(max_length=3, default='USD', verbose_name='Default Currency')
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Default Tax Rate')
    
    # Business settings
    business_hours = models.JSONField(default=dict, blank=True, verbose_name='Business Hours')
    timezone = models.CharField(max_length=50, default='UTC', verbose_name='Timezone')
    
    # Feature flags
    enable_invoicing = models.BooleanField(default=True, verbose_name='Enable Invoicing')
    enable_inventory = models.BooleanField(default=True, verbose_name='Enable Inventory')
    enable_accounting = models.BooleanField(default=True, verbose_name='Enable Accounting')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'
    
    def __str__(self):
        return f'Settings for {self.company.name}'