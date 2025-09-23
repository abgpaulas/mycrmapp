from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from .models import Role, UserRole
from apps.core.models import CompanyProfile

User = get_user_model()


class UserRoleAssignmentForm(forms.Form):
    """Form for assigning roles to users"""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='User'
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Role'
    )
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Expires At (Optional)',
        help_text='Leave blank for permanent assignment'
    )
    
    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if company:
            self.company = company
            # Get users who don't already have roles in this company
            users_with_roles = User.objects.filter(
                user_roles__company=company,
                user_roles__is_active=True
            ).distinct()
            
            # Get users who have company profiles (potential employees)
            available_users = User.objects.filter(
                models.Q(company_profile__isnull=True) |  # Users without company profiles
                models.Q(user_roles__company=company, user_roles__is_active=False)  # Users with inactive roles
            ).distinct().exclude(id__in=users_with_roles)
            
            self.fields['user'].queryset = available_users
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        role = cleaned_data.get('role')
        
        if user and role and hasattr(self, 'company'):
            # Check if user already has this role in this company
            if UserRole.objects.filter(
                user=user,
                company=self.company,
                role=role,
                is_active=True
            ).exists():
                raise ValidationError(f'{user.get_full_name()} already has the {role.name} role.')
        
        return cleaned_data


class RoleForm(forms.ModelForm):
    """Form for creating/editing roles"""
    
    class Meta:
        model = Role
        fields = ['name', 'role_type', 'description', 'permissions', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'role_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permissions': forms.CheckboxSelectMultiple(),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Group permissions by app
        permissions = self.fields['permissions'].queryset.select_related('content_type')
        grouped_permissions = {}
        
        for permission in permissions:
            app_label = permission.content_type.app_label
            if app_label not in grouped_permissions:
                grouped_permissions[app_label] = []
            grouped_permissions[app_label].append(permission)
        
        self.fields['permissions'].queryset = permissions


class PermissionGroupForm(forms.Form):
    """Form for filtering permissions by group"""
    
    app_label = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Filter by App'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get all app labels from permissions
        from django.contrib.auth.models import Permission
        app_labels = Permission.objects.values_list('content_type__app_label', flat=True).distinct().order_by()
        
        choices = [('', 'All Apps')] + [(label, label.title()) for label in app_labels]
        self.fields['app_label'].choices = choices


class UserSearchForm(forms.Form):
    """Form for searching users"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or email...'
        }),
        label='Search Users'
    )
    
    role_filter = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Filter by Role'
    )


class BulkRoleAssignmentForm(forms.Form):
    """Form for bulk role assignment"""
    
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        label='Select Users'
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Role to Assign'
    )
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Expires At (Optional)'
    )
    
    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if company:
            # Get users who don't have active roles in this company
            users_with_roles = User.objects.filter(
                user_roles__company=company,
                user_roles__is_active=True
            ).distinct()
            
            available_users = User.objects.exclude(id__in=users_with_roles)
            self.fields['users'].queryset = available_users


class RolePermissionForm(forms.Form):
    """Form for managing role permissions"""
    
    permissions = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(),
        label='Permissions'
    )
    
    def __init__(self, *args, role=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if role:
            from django.contrib.auth.models import Permission
            self.fields['permissions'].queryset = Permission.objects.all()
            self.fields['permissions'].initial = role.permissions.all()


class UserRoleFilterForm(forms.Form):
    """Form for filtering user roles"""
    
    role_type = forms.ChoiceField(
        choices=[('', 'All Roles')] + Role.ROLE_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Filter by Role Type'
    )
    
    is_active = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('true', 'Active'),
            ('false', 'Inactive'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Filter by Status'
    )
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by user name or email...'
        }),
        label='Search'
    )


class SuperAdminUserCreationForm(UserCreationForm):
    """Form for super admin to create new users with role assignment"""
    
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        }),
        label='First Name'
    )
    
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        }),
        label='Last Name'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        }),
        label='Email Address'
    )
    
    phone = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        }),
        label='Phone Number'
    )
    
    company = forms.ModelChoiceField(
        queryset=CompanyProfile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Company',
        help_text='Select the company this user will belong to'
    )
    
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Role',
        help_text='Select the role to assign to this user'
    )
    
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Role Expires At (Optional)',
        help_text='Leave blank for permanent role assignment'
    )
    
    is_staff = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Staff Status',
        help_text='Designates whether the user can log into the admin site'
    )
    
    is_active = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Active',
        help_text='Designates whether this user should be treated as active'
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize password field widgets
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data.get('is_staff', False)
        user.is_active = self.cleaned_data.get('is_active', True)
        
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """Form for editing existing users"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'is_staff', 'is_active')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('A user with this email already exists.')
        return email


class BulkUserCreationForm(forms.Form):
    """Form for bulk user creation"""
    
    users_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Enter user data in CSV format:\nfirst_name,last_name,email,phone,role_type\nJohn,Doe,john@example.com,+1234567890,manager'
        }),
        label='User Data (CSV Format)',
        help_text='Enter user data in CSV format. First line should be headers: first_name,last_name,email,phone,role_type'
    )
    
    company = forms.ModelChoiceField(
        queryset=CompanyProfile.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Company',
        help_text='All users will be assigned to this company'
    )
    
    default_password = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter default password for all users'
        }),
        label='Default Password',
        help_text='This password will be used for all created users'
    )
    
    send_welcome_email = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Send Welcome Email',
        help_text='Send welcome email with login credentials to new users'
    )
