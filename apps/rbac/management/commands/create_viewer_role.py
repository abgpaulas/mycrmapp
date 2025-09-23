from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, ContentType
from apps.rbac.models import Role, PermissionGroup
from apps.core.models import CompanyProfile
from apps.accounts.models import User
from apps.inventory.models import InventoryItem, InventoryCategory, InventoryProduct
from apps.invoices.models import Invoice
from apps.receipts.models import Receipt
from apps.waybills.models import Waybill
from apps.job_orders.models import Order, Product, Customer
from apps.quotations.models import Quotation
from apps.clients.models import Client
from apps.accounting.models import Transaction


class Command(BaseCommand):
    help = 'Create a Viewer role with read-only permissions'

    def handle(self, *args, **options):
        self.stdout.write('Creating Viewer role...')
        
        # First, add 'viewer' to the ROLE_TYPES choices if not already present
        # We'll need to update the model migration for this, but for now let's create it directly
        
        # Create the Viewer role
        viewer_role, created = Role.objects.get_or_create(
            role_type='viewer',
            defaults={
                'name': 'Viewer',
                'description': 'Read-only access to view, comment, and export data. Cannot create, edit, or delete records.',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created Viewer role')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Viewer role already exists')
            )
        
        # Define models that viewers can view
        models_to_view = [
            (InventoryItem, 'inventory'),
            (InventoryCategory, 'inventory'),
            (InventoryProduct, 'inventory'),
            (Invoice, 'invoices'),
            (Receipt, 'receipts'),
            (Waybill, 'waybills'),
            (Order, 'job_orders'),
            (Product, 'job_orders'),
            (Customer, 'job_orders'),
            (Quotation, 'quotations'),
            (Client, 'clients'),
            (Transaction, 'accounting'),
            (CompanyProfile, 'core'),
            (User, 'accounts'),
        ]
        
        # Get existing permissions for viewing
        view_permissions = []
        
        for model, app_label in models_to_view:
            content_type = ContentType.objects.get_for_model(model)
            
            # Try to get existing view permission
            try:
                view_permission = Permission.objects.get(
                    codename=f'view_{model._meta.model_name}',
                    content_type=content_type,
                )
                view_permissions.append(view_permission)
                self.stdout.write(f'Found view permission for {model._meta.verbose_name}')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'No view permission found for {model._meta.verbose_name}')
                )
        
        # Add general Django permissions that viewers might need
        general_permissions = [
            'view_permission',
            'view_group',
            'view_user',
        ]
        
        for perm_codename in general_permissions:
            try:
                permission = Permission.objects.get(codename=perm_codename)
                view_permissions.append(permission)
                self.stdout.write(f'Added general permission: {perm_codename}')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {perm_codename} not found')
                )
        
        # Assign permissions to the viewer role
        viewer_role.permissions.set(view_permissions)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully assigned {len(view_permissions)} permissions to Viewer role')
        )
        
        # Create a PermissionGroup for Viewer permissions
        viewer_group, created = PermissionGroup.objects.get_or_create(
            name='Viewer Permissions',
            description='Permissions for read-only access across the system',
        )
        
        if created:
            viewer_group.permissions.set(view_permissions)
            self.stdout.write(
                self.style.SUCCESS(f'Created Viewer PermissionGroup with {len(view_permissions)} permissions')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Viewer PermissionGroup already exists')
            )
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('VIEWER ROLE SUMMARY')
        self.stdout.write('='*50)
        self.stdout.write(f'Role Name: {viewer_role.name}')
        self.stdout.write(f'Role Type: {viewer_role.role_type}')
        self.stdout.write(f'Description: {viewer_role.description}')
        self.stdout.write(f'Permissions Count: {viewer_role.permissions.count()}')
        self.stdout.write('\nPermissions:')
        
        for permission in viewer_role.permissions.all():
            self.stdout.write(f'  - {permission.name} ({permission.codename})')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('Viewer role created successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('Users with this role can view, comment, and export data but cannot create, edit, or delete records.')
        )
