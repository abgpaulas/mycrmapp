from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.company_management.models import Company, CompanyUser, CompanySettings
from apps.rbac.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for company management system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample companies
        companies_data = [
            {
                'name': 'TechCorp Solutions',
                'email': 'info@techcorp.com',
                'phone': '+1234567890',
                'address': '123 Tech Street, Silicon Valley, CA 94000',
                'website': 'https://techcorp.com',
                'registration_number': 'TC001',
                'tax_id': 'TAX123456',
                'industry': 'Technology',
                'status': 'active'
            },
            {
                'name': 'Global Manufacturing Ltd',
                'email': 'contact@globalmfg.com',
                'phone': '+1987654321',
                'address': '456 Industrial Ave, Detroit, MI 48200',
                'website': 'https://globalmfg.com',
                'registration_number': 'GM002',
                'tax_id': 'TAX789012',
                'industry': 'Manufacturing',
                'status': 'active'
            },
            {
                'name': 'Creative Design Studio',
                'email': 'hello@creativedesign.com',
                'phone': '+1555123456',
                'address': '789 Creative Blvd, New York, NY 10001',
                'website': 'https://creativedesign.com',
                'registration_number': 'CD003',
                'tax_id': 'TAX345678',
                'industry': 'Design',
                'status': 'pending'
            }
        ]
        
        # Get or create superuser
        superuser, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'first_name': 'Super',
                'last_name': 'Admin',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True
            }
        )
        
        if created:
            superuser.set_password('admin123')
            superuser.save()
            self.stdout.write(f'Created superuser: {superuser.email}')
        
        created_companies = []
        for company_data in companies_data:
            company, created = Company.objects.get_or_create(
                name=company_data['name'],
                defaults={
                    **company_data,
                    'created_by': superuser
                }
            )
            
            if created:
                # Create default settings for the company
                CompanySettings.objects.create(company=company)
                created_companies.append(company)
                self.stdout.write(f'Created company: {company.name}')
        
        # Create sample users if they don't exist
        sample_users = [
            {
                'email': 'john.doe@techcorp.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_active': True
            },
            {
                'email': 'jane.smith@globalmfg.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'is_active': True
            },
            {
                'email': 'mike.johnson@creativedesign.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'is_active': True
            }
        ]
        
        created_users = []
        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )
            
            if created:
                user.set_password('password123')
                user.save()
                created_users.append(user)
                self.stdout.write(f'Created user: {user.get_full_name()}')
        
        # Assign users to companies with roles
        if created_companies and created_users:
            # Get roles
            company_admin_role = Role.objects.filter(role_type='company_admin').first()
            manager_role = Role.objects.filter(role_type='manager').first()
            
            if company_admin_role and manager_role:
                # Assign John Doe to TechCorp as Company Admin
                if len(created_companies) > 0 and len(created_users) > 0:
                    CompanyUser.objects.get_or_create(
                        user=created_users[0],
                        company=created_companies[0],
                        defaults={
                            'role': company_admin_role,
                            'assigned_by': superuser,
                            'is_primary': True
                        }
                    )
                    self.stdout.write(f'Assigned {created_users[0].get_full_name()} to {created_companies[0].name} as {company_admin_role.name}')
                
                # Assign Jane Smith to Global Manufacturing as Manager
                if len(created_companies) > 1 and len(created_users) > 1:
                    CompanyUser.objects.get_or_create(
                        user=created_users[1],
                        company=created_companies[1],
                        defaults={
                            'role': manager_role,
                            'assigned_by': superuser,
                            'is_primary': True
                        }
                    )
                    self.stdout.write(f'Assigned {created_users[1].get_full_name()} to {created_companies[1].name} as {manager_role.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('You can now login with:')
        self.stdout.write('Super Admin: admin@example.com / admin123')
        self.stdout.write('Company Admin: john.doe@techcorp.com / password123')
        self.stdout.write('Manager: jane.smith@globalmfg.com / password123')
