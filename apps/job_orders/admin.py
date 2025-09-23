from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.accounts.models import User
from .models import Product, Order, Leave, ProductStatusHistory, Customer, Store, StoreInventory, StockMovement, Waybill, Receipt, Invoice
from django.utils.html import format_html
from django.contrib.auth.models import Group, Permission

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('job_order', 'organization_name', 'created_by', 'date_created')
    list_filter = ('created_by', 'date_created')
    search_fields = ('job_order', 'organization_name', 'created_by__username')
    readonly_fields = ('created_by',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by')
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = ('employee__username', 'leave_type')
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductStatusHistory)
class ProductStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'status', 'created_at', 'updated_by', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_by']
    search_fields = ['product__job_order', 'status']
    ordering = ['-created_at']
               
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(StoreInventory)
class StoreInventoryAdmin(admin.ModelAdmin):
    list_display = ['store', 'product', 'quantity', 'reorder_level', 'is_low_stock']
    list_filter = ['store', 'product__category']
    search_fields = ['store__name', 'product__job_order']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['store', 'product', 'movement_type', 'quantity', 'created_at', 'created_by']
    list_filter = ['movement_type', 'created_at', 'created_by']
    search_fields = ['store__name', 'product__job_order', 'reference']
    readonly_fields = ['created_at']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'manager', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'location', 'manager__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = [
        'receipt_number', 
        'customer', 
        'product', 
        'amount',
        'payment_method',
        'status', 
        'created_by',
        'created_at'
    ]
    
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['receipt_number', 'customer__name', 'product__job_order']
    readonly_fields = ['receipt_number', 'created_at', 'updated_at', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Waybill)
class WaybillAdmin(admin.ModelAdmin):
    list_display = [
        'waybill_number',
        'customer',
        'product', 
        'quantity',
        'origin',
        'destination',
        'status',
        'created_by',
        'created_at'
    ]
   
    list_filter = ['status', 'created_at']
    search_fields = ['waybill_number', 'customer__name', 'product__job_order']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
   
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number',
        'customer',
        'product',
        'amount',
        'total_amount',
        'due_date',
        'status',
        'created_by',
        'created_at'
    ]
    
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'customer__name', 'product__job_order']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Create groups - moved to function to avoid database access during import
def create_groups():
    try:
        product_manager_group, created = Group.objects.get_or_create(name='Product Managers')
        product_viewer_group, created = Group.objects.get_or_create(name='Product Viewers')
        product_approver_group, created = Group.objects.get_or_create(name='Product Approvers')
        return product_manager_group, product_viewer_group, product_approver_group
    except Exception:
        # Database not ready yet, return None
        return None, None, None

product_manager_permissions = [
    'can_view_all_jobs',
    'can_export_jobs',
    'can_manage_production',
    'can_approve_jobs'
]

product_viewer_permissions = [
    'can_view_all_jobs',
    'can_export_jobs'
]

product_approver_permissions = [
    'can_view_all_jobs',
    'can_approve_jobs'
]

admin.site.register(Order)
