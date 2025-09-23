from django import forms
from django.contrib.auth import get_user_model
from .models import Company, CompanyUser, CompanySettings
from apps.rbac.models import Role

User = get_user_model()


class CompanyForm(forms.ModelForm):
    """Form for creating and editing companies"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'email', 'phone', 'address', 'website',
            'registration_number', 'tax_id', 'industry', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter company address'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter website URL (optional)'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter registration number (optional)'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tax ID (optional)'
            }),
            'industry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter industry (optional)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class CompanyUserForm(forms.ModelForm):
    """Form for assigning users to companies with roles"""
    
    class Meta:
        model = CompanyUser
        fields = ['user', 'company', 'role', 'is_primary', 'expires_at']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-control',
                'id': 'user-select'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control',
                'id': 'company-select'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control',
                'id': 'role-select'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users who are not already assigned to the selected company
        if 'company' in self.data:
            try:
                company_id = int(self.data.get('company'))
                self.fields['user'].queryset = User.objects.exclude(
                    company_users__company_id=company_id,
                    company_users__is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['user'].queryset = User.objects.exclude(
                company_users__company=self.instance.company,
                company_users__is_active=True
            ).exclude(id=self.instance.user.id)


class CompanySettingsForm(forms.ModelForm):
    """Form for company settings"""
    
    class Meta:
        model = CompanySettings
        fields = [
            'default_currency', 'default_tax_rate', 'timezone',
            'enable_invoicing', 'enable_inventory', 'enable_accounting'
        ]
        widgets = {
            'default_currency': forms.Select(attrs={
                'class': 'form-control'
            }),
            'default_tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'timezone': forms.Select(attrs={
                'class': 'form-control'
            }),
            'enable_invoicing': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'enable_inventory': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'enable_accounting': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class CompanySearchForm(forms.Form):
    """Form for searching companies"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search companies...',
            'id': 'company-search'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Company.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'status-filter'
        })
    )
    industry = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by industry...',
            'id': 'industry-filter'
        })
    )
