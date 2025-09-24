from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.rbac.managers import RoleManager, UserRoleManager
from apps.core.models import CompanyProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up the RBAC system with default roles and permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-roles',
            action='store_true',
            help='Create default roles',
        )
        parser.add_argument(
            '--assign-super-admin',
            type=str,
            help='Assign super admin role to a user by email',
        )
        parser.add_argument(
            '--assign-company-admin',
            type=str,
            help='Assign company admin role to a user by email',
        )
        parser.add_argument(
            '--list-roles',
            action='store_true',
            help='List all available roles',
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='List all users with their roles',
        )

    def handle(self, *args, **options):
        if options['create_roles']:
            self.create_default_roles()
        
        if options['assign_super_admin']:
            self.assign_super_admin(options['assign_super_admin'])
        
        if options['assign_company_admin']:
            self.assign_company_admin(options['assign_company_admin'])
        
        if options['list_roles']:
            self.list_roles()
        
        if options['list_users']:
            self.list_users()

    def create_default_roles(self):
        """Create default roles with permissions"""
        self.stdout.write('Creating default roles...')
        try:
            created_roles = RoleManager.create_default_roles()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {len(created_roles)} default roles')
            )
            for role in created_roles:
                self.stdout.write(f'  - {role.name} ({role.role_type})')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating roles: {str(e)}')
            )

    def assign_super_admin(self, email):
        """Assign super admin role to a user"""
        try:
            user = User.objects.get(email=email)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully assigned super admin privileges to {user.get_full_name()}')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {email} does not exist')
            )

    def assign_company_admin(self, email):
        """Assign company admin role to a user"""
        try:
            user = User.objects.get(email=email)
            if not hasattr(user, 'company_profile'):
                self.stdout.write(
                    self.style.ERROR(f'User {user.get_full_name()} does not have a company profile')
                )
                return
            
            user_role, created = UserRoleManager.assign_role(
                user=user,
                company=user.company_profile,
                role_type='company_admin'
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully assigned company admin role to {user.get_full_name()}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User {user.get_full_name()} already has company admin role')
                )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {email} does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error assigning company admin role: {str(e)}')
            )

    def list_roles(self):
        """List all available roles"""
        from apps.rbac.models import Role
        roles = Role.objects.all()
        self.stdout.write('Available roles:')
        for role in roles:
            self.stdout.write(f'  - {role.name} ({role.role_type}) - {role.permissions.count()} permissions')

    def list_users(self):
        """List all users with their roles"""
        from apps.rbac.models import UserRole
        user_roles = UserRole.objects.filter(is_active=True).select_related('user', 'company', 'role')
        
        self.stdout.write('Users and their roles:')
        current_user = None
        for user_role in user_roles:
            if current_user != user_role.user:
                current_user = user_role.user
                self.stdout.write(f'\n{current_user.get_full_name()} ({current_user.email}):')
            
            self.stdout.write(f'  - {user_role.role.name} at {user_role.company.company_name}')
