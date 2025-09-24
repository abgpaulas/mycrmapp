from django.contrib import admin
from django.utils.html import format_html
from .models import Company, CompanyUser, CompanySettings


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'status', 'is_active', 'created_at', 'created_by']
    list_filter = ['status', 'is_active', 'industry', 'created_at']
    search_fields = ['name', 'email', 'phone', 'registration_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'address', 'website')
        }),
        ('Company Details', {
            'fields': ('registration_number', 'tax_id', 'industry')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'role', 'is_active', 'is_primary', 'assigned_at', 'assigned_by']
    list_filter = ['is_active', 'is_primary', 'role', 'assigned_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'company__name']
    readonly_fields = ['assigned_at']
    
    fieldsets = (
        ('Assignment', {
            'fields': ('user', 'company', 'role')
        }),
        ('Status', {
            'fields': ('is_active', 'is_primary')
        }),
        ('Expiration', {
            'fields': ('expires_at',)
        }),
        ('Metadata', {
            'fields': ('assigned_at', 'assigned_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ['company', 'default_currency', 'default_tax_rate', 'enable_invoicing', 'enable_inventory']
    list_filter = ['default_currency', 'enable_invoicing', 'enable_inventory', 'enable_accounting']
    search_fields = ['company__name']
    
    fieldsets = (
        ('Financial Settings', {
            'fields': ('default_currency', 'default_tax_rate')
        }),
        ('Business Settings', {
            'fields': ('business_hours', 'timezone')
        }),
        ('Feature Flags', {
            'fields': ('enable_invoicing', 'enable_inventory', 'enable_accounting')
        }),
    )