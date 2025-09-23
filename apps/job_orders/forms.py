from django import forms
from .models import Product, Order, Receipt, Waybill, ProductStatusHistory
from apps.accounts.models import User
from .models import Leave, Customer, Store, StoreInventory, StockMovement, Invoice
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['updated_by', 'production_status', 'name', 'category']
        
        fields = [
            'job_order',           # Job Order Number
            'submission_id',       # Submission ID
            'organization_name',    # Job Name
            'address',             # Customer Name
            'contact_number',      # Contact Number (Phone)
            'print_product',       # Package Type/Product
            'colors',              # No. of Colors/Color Names
            'treatment',           # Treatment
            'cutting_length',      # Cutting Length
            'flap',                # Flap
            'printing',            # Printing
            'size',                # Thickness/Width
            'micron',              # Micron
            'job_title',           # Extrusion Quantity
            'order_info',          # Order Information
            'quantity',            # Quantity
            'price',               # Price (₦)
            'order_quantity',      # Delivery Quantity
            'estimated_delivery_date',  # Estimated Delivery Date
            'actual_delivery_date',     # Actual Delivery Date
            'approval_status',     # Approval Status (for superusers)
            'approved_by',         # Approved By (for superusers)
            'created_by',          # Created By (for superusers)
            'image', 
        ]
        
        labels = {
            'job_order': 'Job Order Number',
            'submission_id': 'Submission ID',
            'organization_name': 'Job Name',
            'address': 'Customer Name',
            'contact_number': 'Contact Number (Phone)', 
            'print_product': 'Package Type/Product',
            'colors': 'No. of Colors/Color Names',
            'treatment': 'Treatment',
            'cutting_length': 'Cutting Length',
            'flap': 'Flap',
            'printing': 'Printing',
            'size': 'Thickness/Width',
            'micron': 'Micron',
            'job_title': 'Extrusion Quantity (kg)',
            'order_info': 'Order Information',
            'quantity': 'Quantity',
            'price': 'Price (₦)',
            'order_quantity': 'Delivery Quantity (kg)',
            'estimated_delivery_date': 'Estimated Delivery Date',
            'actual_delivery_date': 'Actual Delivery Date',
            'approval_status': 'Approval Status',
            'approved_by': 'Approved By',
            'created_by': 'Created By',
            'image': 'Upload Image',
        }

        widgets = {
            'job_order': forms.TextInput(attrs={'class': 'form-control'}),
            'submission_id': forms.TextInput(attrs={'class': 'form-control'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'print_product': forms.TextInput(attrs={'class': 'form-control'}),
            'colors': forms.TextInput(attrs={'class': 'form-control'}),
            'treatment': forms.TextInput(attrs={'class': 'form-control'}),
            'cutting_length': forms.TextInput(attrs={'class': 'form-control'}),
            'flap': forms.TextInput(attrs={'class': 'form-control'}),
            'printing': forms.TextInput(attrs={'class': 'form-control'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'micron': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'order_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={
                'id': 'id_price',
                'step': '0.01',
                'class': 'form-control'
            }),
            'order_quantity': forms.NumberInput(attrs={
                'id': 'id_order_quantity',
                'class': 'form-control'
            }),
            'estimated_delivery_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'actual_delivery_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'approval_status': forms.Select(attrs={'class': 'form-control'}),
            'approved_by': forms.Select(attrs={'class': 'form-control'}),
            'created_by': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control',
                'id': 'id_image'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        
        self.fields['image'].required = False
        
        # Make certain fields optional
        self.fields['submission_id'].required = False
        self.fields['address'].required = False
        self.fields['contact_number'].required = False
        self.fields['print_product'].required = False
        self.fields['colors'].required = False
        self.fields['treatment'].required = False
        self.fields['cutting_length'].required = False
        self.fields['flap'].required = False
        self.fields['printing'].required = False
        self.fields['size'].required = False
        self.fields['micron'].required = False
        self.fields['job_title'].required = False
        self.fields['order_info'].required = False
        self.fields['quantity'].required = False
        self.fields['price'].required = False
        self.fields['order_quantity'].required = False
        self.fields['estimated_delivery_date'].required = False
        self.fields['actual_delivery_date'].required = False
        self.fields['approval_status'].required = False
        self.fields['approved_by'].required = False
        self.fields['created_by'].required = False
        
        if user and user.is_superuser:
            # Update approval status field for superusers
            self.fields['approval_status'].choices = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
            self.fields['approval_status'].initial = self.instance.approval_status if self.instance else 'pending'
            
            # Update approved_by field for superusers
            self.fields['approved_by'].queryset = User.objects.filter(is_superuser=True)
            self.fields['approved_by'].initial = self.instance.approved_by if self.instance else None
            
            # Update created_by field for superusers
            self.fields['created_by'].queryset = User.objects.all()
            self.fields['created_by'].initial = self.instance.created_by if self.instance else None
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        order_quantity = cleaned_data.get('order_quantity')
        
        # Validate price and quantity
        if price is not None and price < 0:
            raise ValidationError("Price cannot be negative.")
        
        if order_quantity is not None and order_quantity < 0:
            raise ValidationError("Order quantity cannot be negative.")
        
        # Validate delivery dates
        estimated_delivery = cleaned_data.get('estimated_delivery_date')
        actual_delivery = cleaned_data.get('actual_delivery_date')
        
        if estimated_delivery and actual_delivery:
            if actual_delivery < estimated_delivery:
                raise ValidationError("Actual delivery date cannot be before estimated delivery date.")
        
        return cleaned_data

class LeaveForm(forms.ModelForm):
    duration = forms.IntegerField(disabled=True, required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date must be after start date")
            
            # Calculate duration
            duration = (end_date - start_date).days + 1
            cleaned_data['duration'] = duration
            
            # Check maximum leave duration
            if duration > 30:
                raise forms.ValidationError("Leave duration cannot exceed 30 days")
        
        return cleaned_data
    
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class LeaveResponseForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter response message'}),
            'status': forms.Select(choices=[
                ('approved', 'Approve'),
                ('rejected', 'Reject'),
                ('pending', 'Pending')
            ])
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'location', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }

class StoreInventoryForm(forms.ModelForm):
    class Meta:
        model = StoreInventory
        fields = ['store', 'product', 'quantity', 'reorder_level']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['store', 'product', 'movement_type', 'quantity', 'reference', 'notes']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'movement_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class WaybillForm(forms.ModelForm):
    class Meta:
        model = Waybill
        fields = ['customer', 'product', 'quantity', 'origin', 'destination', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'origin': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['customer', 'product', 'amount', 'payment_method', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'payment_method': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'product', 'amount', 'tax_rate', 'due_date', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'customer', 'order_quantity', 'estimated_delivery_date', 'additional_notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'order_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'estimated_delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'additional_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ProductStatusHistoryForm(forms.ModelForm):
    class Meta:
        model = ProductStatusHistory
        fields = ['status', 'priority']
        widgets = {
            'status': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
