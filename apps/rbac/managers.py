from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Role, UserRole


class RoleManager:
    """
    Manager class for handling role-related operations
    """
    
    @staticmethod
    def create_default_roles():
        """Create default roles with their permissions"""
        try:
            roles_data = [
                {
                    'name': 'Super Admin',
                    'role_type': 'super_admin',
                    'description': 'Full system access with ability to manage all companies and users',
                    'permissions': ['*']  # All permissions
                },
                {
                    'name': 'Company Admin',
                    'role_type': 'company_admin',
                    'description': 'Full access within their company',
                    'permissions': [
                        'accounts.add_user',
                        'accounts.change_user',
                        'accounts.view_user',
                        'core.add_companyprofile',
                        'core.change_companyprofile',
                        'core.view_companyprofile',
                        'inventory.*',
                        'invoices.*',
                        'quotations.*',
                        'job_orders.*',
                        'receipts.*',
                        'waybills.*',
                        'clients.*',
                        'expenses.*',
                        'accounting.*',
                    ]
                },
                {
                    'name': 'Manager',
                    'role_type': 'manager',
                    'description': 'Management access to most company operations',
                    'permissions': [
                        'inventory.view_product',
                        'inventory.add_product',
                        'inventory.change_product',
                        'invoices.view_invoice',
                        'invoices.add_invoice',
                        'invoices.change_invoice',
                        'quotations.view_quotation',
                        'quotations.add_quotation',
                        'quotations.change_quotation',
                        'job_orders.view_joborder',
                        'job_orders.add_joborder',
                        'job_orders.change_joborder',
                        'clients.view_client',
                        'clients.add_client',
                        'clients.change_client',
                        'receipts.view_receipt',
                        'receipts.add_receipt',
                        'waybills.view_waybill',
                        'waybills.add_waybill',
                    ]
                },
                {
                    'name': 'Production Manager',
                    'role_type': 'production_manager',
                    'description': 'Access to production-related operations',
                    'permissions': [
                        'inventory.view_product',
                        'inventory.add_product',
                        'inventory.change_product',
                        'job_orders.view_joborder',
                        'job_orders.add_joborder',
                        'job_orders.change_joborder',
                        'waybills.view_waybill',
                        'waybills.add_waybill',
                        'clients.view_client',
                    ]
                },
                {
                    'name': 'Accountant',
                    'role_type': 'accountant',
                    'description': 'Access to financial operations',
                    'permissions': [
                        'invoices.view_invoice',
                        'invoices.add_invoice',
                        'invoices.change_invoice',
                        'receipts.view_receipt',
                        'receipts.add_receipt',
                        'clients.view_client',
                        'accounting.*',
                    ]
                },
                {
                    'name': 'Sales Representative',
                    'role_type': 'sales_rep',
                    'description': 'Access to sales operations',
                    'permissions': [
                        'clients.view_client',
                        'clients.add_client',
                        'clients.change_client',
                        'quotations.view_quotation',
                        'quotations.add_quotation',
                        'quotations.change_quotation',
                        'invoices.view_invoice',
                        'invoices.add_invoice',
                    ]
                },
                {
                    'name': 'Store Keeper',
                    'role_type': 'store_keeper',
                    'description': 'Access to inventory management',
                    'permissions': [
                        'inventory.view_product',
                        'inventory.add_product',
                        'inventory.change_product',
                        'inventory.view_stockmovement',
                        'inventory.add_stockmovement',
                        'waybills.view_waybill',
                        'waybills.add_waybill',
                    ]
                },
            ]
            
            created_roles = []
            for role_data in roles_data:
                try:
                    role, created = Role.objects.get_or_create(
                        role_type=role_data['role_type'],
                        defaults={
                            'name': role_data['name'],
                            'description': role_data['description']
                        }
                    )
                    if created:
                        # Add permissions to the role
                        permissions = role_data['permissions']
                        if permissions == ['*']:  # Super admin gets all permissions
                            role.permissions.set(Permission.objects.all())
                        else:
                            role_permissions = []
                            for perm in permissions:
                                if perm.endswith('.*'):  # Wildcard permission
                                    app_label = perm.replace('.*', '')
                                    role_permissions.extend(
                                        Permission.objects.filter(content_type__app_label=app_label)
                                    )
                                else:
                                    try:
                                        app_label, codename = perm.split('.')
                                        role_permissions.append(
                                            Permission.objects.get(content_type__app_label=app_label, codename=codename)
                                        )
                                    except (ValueError, Permission.DoesNotExist):
                                        continue
                            role.permissions.set(role_permissions)
                    created_roles.append(role)
                except Exception as e:
                    # Log individual role creation errors but continue
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error creating role {role_data.get('name', 'Unknown')}: {e}")
                    continue
            
            return created_roles
        except Exception as e:
            # Log the overall error and return empty list
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in create_default_roles: {e}")
            return []


class UserRoleManager:
    """
    Manager class for handling user role assignments
    """
    
    @staticmethod
    def assign_role(user, company, role_type, assigned_by=None, expires_at=None):
        """Assign a role to a user for a specific company"""
        try:
            role = Role.objects.get(role_type=role_type)
            user_role, created = UserRole.objects.get_or_create(
                user=user,
                company=company,
                role=role,
                defaults={
                    'assigned_by': assigned_by,
                    'expires_at': expires_at,
                    'is_active': True
                }
            )
            return user_role, created
        except Role.DoesNotExist:
            raise ValueError(f"Role with type '{role_type}' does not exist")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error assigning role: {e}")
            raise
    
    @staticmethod
    def revoke_role(user, company, role_type):
        """Revoke a role from a user for a specific company"""
        try:
            role = Role.objects.get(role_type=role_type)
            user_role = UserRole.objects.get(
                user=user,
                company=company,
                role=role,
                is_active=True
            )
            user_role.is_active = False
            user_role.save()
            return user_role
        except (Role.DoesNotExist, UserRole.DoesNotExist):
            return None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error revoking role: {e}")
            raise
    
    @staticmethod
    def get_user_roles(user, company=None):
        """Get all active roles for a user, optionally filtered by company"""
        queryset = UserRole.objects.filter(
            user=user,
            is_active=True
        ).select_related('role', 'company')
        
        if company:
            queryset = queryset.filter(company=company)
        
        return queryset
    
    @staticmethod
    def has_role(user, role_type, company=None):
        """Check if a user has a specific role"""
        queryset = UserRole.objects.filter(
            user=user,
            role__role_type=role_type,
            is_active=True
        )
        
        if company:
            queryset = queryset.filter(company=company)
        
        return queryset.exists()
    
    @staticmethod
    def has_permission(user, permission_codename, company=None):
        """Check if a user has a specific permission through their roles"""
        queryset = UserRole.objects.filter(
            user=user,
            is_active=True,
            role__permissions__codename=permission_codename
        )
        
        if company:
            queryset = queryset.filter(company=company)
        
        return queryset.exists()
