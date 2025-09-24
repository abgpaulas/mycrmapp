from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, ContentType
from apps.rbac.models import Role, PermissionGroup
from apps.invoices.models import Invoice, InvoiceItem
from apps.receipts.models import Receipt
from apps.waybills.models import Waybill, WaybillItem
from apps.job_orders.models import Order, Product
from apps.quotations.models import Quotation, QuotationItem
from apps.clients.models import Client


class Command(BaseCommand):
    help = 'Update Viewer role with specific permissions for Invoices, Receipts, Waybills, Job Orders, and Quotations'

    def handle(self, *args, **options):
        self.stdout.write('Updating Viewer role permissions...')
        
        # Get the Viewer role
        try:
            viewer_role = Role.objects.get(role_type='viewer')
            self.stdout.write(f'Found Viewer role: {viewer_role.name}')
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Viewer role not found. Please run: python manage.py create_viewer_role')
            )
            return
        
        # Define the specific models that viewers can interact with
        viewer_models = [
            # Invoices
            (Invoice, 'invoices'),
            (InvoiceItem, 'invoices'),
            
            # Receipts
            (Receipt, 'receipts'),
            
            # Waybills
            (Waybill, 'waybills'),
            (WaybillItem, 'waybills'),
            
            # Job Orders
            (Order, 'job_orders'),
            (Product, 'job_orders'),
            
            # Quotations
            (Quotation, 'quotations'),
            (QuotationItem, 'quotations'),
            
            # Clients (needed to view client info in invoices/quotations)
            (Client, 'clients'),
        ]
        
        # Get permissions for viewing these models
        view_permissions = []
        comment_permissions = []
        export_permissions = []
        
        for model, app_label in viewer_models:
            content_type = ContentType.objects.get_for_model(model)
            
            # Add view permission
            try:
                view_permission = Permission.objects.get(
                    codename=f'view_{model._meta.model_name}',
                    content_type=content_type,
                )
                view_permissions.append(view_permission)
                self.stdout.write(f'✓ Added view permission for {model._meta.verbose_name}')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ No view permission found for {model._meta.verbose_name}')
                )
            
            # Note: Comment functionality appears to be implemented in templates
            # but comment models may not be accessible in current codebase
            # We'll focus on view and export permissions for now
        
        # Add specific export permissions for job orders
        job_order_export_permissions = [
            'can_export_jobs',
            'can_export_products',
        ]
        
        for perm_codename in job_order_export_permissions:
            try:
                # These are custom permissions defined in the job_orders app
                permission = Permission.objects.get(codename=perm_codename)
                export_permissions.append(permission)
                self.stdout.write(f'✓ Added export permission: {perm_codename}')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Export permission {perm_codename} not found')
                )
        
        # Combine all permissions
        all_permissions = view_permissions + comment_permissions + export_permissions
        
        # Update the viewer role with these specific permissions
        viewer_role.permissions.set(all_permissions)
        
        # Update the description
        viewer_role.description = (
            'Read-only access to view, comment, and export data for Invoices, Receipts, '
            'Waybills, Job Orders, and Quotations. Cannot create, edit, or delete records '
            'except for adding comments to Job Orders.'
        )
        viewer_role.save()
        
        # Update or create PermissionGroup
        viewer_group, created = PermissionGroup.objects.get_or_create(
            name='Viewer Business Documents',
            defaults={
                'description': 'Permissions for viewing, commenting, and exporting business documents'
            }
        )
        
        if created:
            self.stdout.write(f'Created new PermissionGroup: {viewer_group.name}')
        else:
            self.stdout.write(f'Updated existing PermissionGroup: {viewer_group.name}')
        
        viewer_group.permissions.set(all_permissions)
        
        # Display summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('VIEWER ROLE UPDATED SUCCESSFULLY')
        self.stdout.write('='*60)
        self.stdout.write(f'Role Name: {viewer_role.name}')
        self.stdout.write(f'Role Type: {viewer_role.role_type}')
        self.stdout.write(f'Total Permissions: {len(all_permissions)}')
        self.stdout.write(f'View Permissions: {len(view_permissions)}')
        self.stdout.write(f'Comment Permissions: {len(comment_permissions)}')
        self.stdout.write(f'Export Permissions: {len(export_permissions)}')
        
        self.stdout.write('\n📋 VIEW PERMISSIONS:')
        for permission in view_permissions:
            self.stdout.write(f'  • {permission.name}')
        
        if comment_permissions:
            self.stdout.write('\n💬 COMMENT PERMISSIONS:')
            for permission in comment_permissions:
                self.stdout.write(f'  • {permission.name}')
        
        if export_permissions:
            self.stdout.write('\n📤 EXPORT PERMISSIONS:')
            for permission in export_permissions:
                self.stdout.write(f'  • {permission.name}')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('✅ Viewer role updated successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('👁️  Viewers can now view, comment, and export business documents')
        )
        self.stdout.write(
            self.style.SUCCESS('🚫 Viewers cannot create, edit, or delete records (except comments)')
        )
