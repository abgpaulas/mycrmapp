import random
import string
from django.db import models
from apps.accounts.models import User
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

CATEGORY = (
    ('Stationary', 'Stationary'),
    ('Electronics', 'Electronics'),
    ('Food', 'Food'),
    ('BOPP', 'BOPP'),
)

DEPARTMENT_CHOICES = [
    ('IT', 'Information Technology'),
    ('HR', 'Human Resources'),
    ('FIN', 'Finance'),
    ('OPS', 'Operations'),
    ('MKT', 'Marketing')
]

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other')
)

MARITAL_STATUS = (
    ('S', 'Single'),
    ('M', 'Married'),
    ('D', 'Divorced'),
    ('W', 'Widowed')
)

def generate_submission_id():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))

def generate_job_order():
    prefix = 'JO'
    random_number = random.randint(1000, 9999)
    year = timezone.now().strftime('%y')
    return f"{prefix}-{random_number}-{year}"

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_employee_profile')
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    date_of_employment = models.DateField()
    qualifications = models.TextField()
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS)
    reference_name = models.CharField(max_length=100)
    reference_number = models.CharField(max_length=50)
    reference_address = models.TextField()

    class Meta:
        verbose_name = 'Employee Profile'
        verbose_name_plural = 'Employee Profiles'
        ordering = ['user__email']

    def __str__(self):
        return f"{self.user.email}'s Employee Profile"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_profile')
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['user__email']
        
    def __str__(self):
        return f"{self.user.email}'s Profile"

class Product(models.Model):
    # Basic Information
    name = models.CharField(max_length=100, null=True)
    category = models.CharField(choices=CATEGORY, max_length=50, null=True)
    job_order = models.CharField(max_length=50, unique=True, default=generate_job_order)
    submission_id = models.CharField(max_length=50, null=True, blank=True, default=generate_submission_id)
    
    # Customer Information
    organization_name = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Add these new fields under Product Details section
    treatment = models.CharField(max_length=100, null=True, blank=True)
    cutting_length = models.CharField(max_length=50, null=True, blank=True)
    flap = models.CharField(max_length=50, null=True, blank=True)
    printing = models.CharField(max_length=50, null=True, blank=True)
    
    # Product Details
    print_product = models.CharField(max_length=100, null=True, blank=True)
    colors = models.CharField(max_length=100, null=True, blank=True)
    order_info = models.TextField(null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    micron = models.CharField(max_length=50, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    
    # Pricing and Quantity
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.CharField(max_length=100, null=True, blank=True)
    order_quantity = models.PositiveIntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Dates and Timeline
    date_created = models.DateTimeField(default=timezone.now)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    cycle_time = models.DurationField(null=True, blank=True)
    production_status_date = models.DateTimeField(auto_now=True)
    
    # Status and Tracking
    APPROVAL_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')
    production_status = models.TextField(null=True, blank=True)
    
    # User Relations
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_products')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_products')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='product_updates')

    class Meta:
        ordering = ['-date_created']
        permissions = [
            ("can_approve_jobs", "Can approve job orders"),
            ("can_view_all_jobs", "Can view all job orders"),
            ("can_export_jobs", "Can export job orders"),
            ("can_manage_production", "Can manage production status"),
            ("view_dashboard", "Can view dashboard"),
            ("manage_leave", "Can manage leave requests"),
            ("can_export_products", "Can export products"),
            ("can_export_leaves", "Can export leaves"),
        ]
        
    def is_overdue(self):
        if self.estimated_delivery_date and not self.actual_delivery_date:
            return timezone.now().date() > self.estimated_delivery_date
        return False

    def get_status_display(self):
        return dict(self.APPROVAL_CHOICES)[self.approval_status]

    def days_until_delivery(self):
        if self.estimated_delivery_date:
            return (self.estimated_delivery_date - timezone.now().date()).days
        return None  
    
    def __str__(self):
        return f"{self.job_order} - {self.organization_name}"

    def save(self, *args, **kwargs):
        if not self.submission_id:
            self.submission_id = generate_submission_id()
        if not self.job_order:
            self.job_order = generate_job_order()
        self.calculate_total()
        self.calculate_cycle_time()
        super().save(*args, **kwargs)

    def calculate_total(self):
        if self.price is not None and self.order_quantity is not None:
            self.total = self.price * self.order_quantity

    def calculate_cycle_time(self):
        if self.estimated_delivery_date and self.actual_delivery_date:
            self.cycle_time = self.actual_delivery_date - self.estimated_delivery_date
        else:
            self.cycle_time = None

    def formatted_price(self):
        currency_symbol = self.get_currency_symbol()
        return f"{currency_symbol}{intcomma('{:.2f}'.format(self.price))}" if self.price else ''

    def formatted_total(self):
        currency_symbol = self.get_currency_symbol()
        return f"{currency_symbol}{intcomma('{:.2f}'.format(self.total))}" if self.total else ''
    
    def get_currency_symbol(self):
        """Get currency symbol from company profile"""
        try:
            if self.created_by and hasattr(self.created_by, 'company_profile'):
                return self.created_by.company_profile.currency_symbol
        except:
            pass
        return '₦'  # Default fallback

class ProductStatusHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='status_history')
    status = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Production Status History'
        verbose_name_plural = 'Production Status Histories'
        indexes = [
            models.Index(fields=['created_at', 'is_active']),
        ]
        
    def __str__(self):
        return f"Status update for {self.product.job_order} at {self.created_at}"
    
    def get_priority_display(self):
        """Return the human-readable priority level"""
        priority_map = {
            0: 'Low',
            1: 'Normal', 
            2: 'High',
            3: 'Urgent'
        }
        return priority_map.get(self.priority, 'Normal')
    
    def save(self, *args, **kwargs):
        # Update the parent product's status
        if self.is_active:
            self.product.production_status = self.status
            self.product.production_status_date = self.created_at
            self.product.updated_by = self.updated_by
            self.product.save()
        super().save(*args, **kwargs)

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order_quantity = models.PositiveIntegerField(null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    estimated_delivery_date = models.DateField(null=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    cycle_time = models.DurationField(null=True, blank=True)
    order_status = models.CharField(max_length=50, null=True)
    additional_notes = models.TextField(blank=True)
    
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS, default='pending')

    def is_completed(self):
        return self.order_status == 'delivered'

    def can_be_cancelled(self):
        return self.order_status in ['pending', 'processing']
    
    def __str__(self):
        return f'{self.date_created} - {self.customer} - {self.product.job_order}'

    def save(self, *args, **kwargs):
        if self.product and self.order_quantity:
            self.total_price = self.product.price * self.order_quantity
        if self.estimated_delivery_date and self.actual_delivery_date:
            self.cycle_time = self.actual_delivery_date - self.estimated_delivery_date
        super().save(*args, **kwargs)

    def formatted_total_price(self):
        currency_symbol = self.get_currency_symbol()
        return f"{currency_symbol}{intcomma('{:.2f}'.format(self.total_price))}" if self.total_price else ''
    
    def get_currency_symbol(self):
        """Get currency symbol from company profile"""
        try:
            if self.customer and hasattr(self.customer, 'company_profile'):
                return self.customer.company_profile.currency_symbol
        except:
            pass
        return '₦'  # Default fallback

class Leave(models.Model):
    LEAVE_TYPES = (
        ('Annual', 'Annual Leave'),
        ('Sick', 'Sick Leave'),
        ('Personal', 'Personal Leave'),
        ('Maternity', 'Maternity Leave'),
        ('Paternity', 'Paternity Leave'),
        ('Parental', 'Parental Leave'),
        ('Bereavement', 'Bereavement Leave'),
        ('Study', 'Study Leave'),
        ('Unpaid', 'Unpaid Leave'),
        ('Other', 'Other'),
    )
    
    LEAVE_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
    
    def __str__(self):
        return f"{self.employee.email} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def get_duration(self):
        return (self.end_date - self.start_date).days + 1
    
    def is_approved(self):
        return self.status == 'approved'
    
    def is_pending(self):
        return self.status == 'pending'
    
    def can_be_approved(self):
        return self.status == 'pending'
    
    def can_be_rejected(self):
        return self.status == 'pending'
    
    def can_be_cancelled(self):
        return self.status in ['pending', 'approved']

class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'
    
    def __str__(self):
        return self.name

class StoreInventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_inventory')
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['store', 'product']
        verbose_name = 'Store Inventory'
        verbose_name_plural = 'Store Inventory'
    
    def __str__(self):
        return f"{self.store.name} - {self.product.job_order} ({self.quantity})"
    
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
    )
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='stock_movements')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
    
    def __str__(self):
        return f"{self.movement_type} - {self.product.job_order} ({self.quantity}) at {self.store.name}"

class Waybill(models.Model):
    WAYBILL_STATUS = (
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    waybill_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='waybills')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='waybills')
    quantity = models.PositiveIntegerField()
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=WAYBILL_STATUS, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_waybills')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Waybill'
        verbose_name_plural = 'Waybills'
    
    def __str__(self):
        return f"Waybill {self.waybill_number} - {self.customer.name}"

class Receipt(models.Model):
    RECEIPT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    receipt_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='receipts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='receipts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=RECEIPT_STATUS, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_receipts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Receipt'
        verbose_name_plural = 'Receipts'
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.customer.name}"

class Invoice(models.Model):
    INVOICE_STATUS = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.name}"
    
    def calculate_total(self):
        tax_amount = (self.amount * self.tax_rate) / 100
        self.total_amount = self.amount + tax_amount
        return self.total_amount
    
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status not in ['paid', 'cancelled']
