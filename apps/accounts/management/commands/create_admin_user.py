"""
Django management command to create an admin user
Run with: python manage.py create_admin_user
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import CompanyProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create an admin user with company profile'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@mycrmapp.com',
            help='Email for the admin user'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for the admin user'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        
        self.stdout.write("🚀 Creating admin user...")
        
        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.SUCCESS(f"✅ User with email {email} already exists!")
                )
                user = User.objects.get(email=email)
            else:
                # Create new user
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name="Admin",
                    last_name="User",
                    phone="+1234567890",
                    is_active=True,
                    is_staff=True,
                    is_superuser=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f"✅ User created successfully: {email}")
                )
            
            # Create company profile if it doesn't exist
            if not hasattr(user, 'company_profile'):
                company_profile = CompanyProfile.objects.create(
                    user=user,
                    company_name="MyCRM Company",
                    company_email=email,
                    company_phone="+1234567890",
                    company_address="123 Business Street, City, State 12345",
                    company_website="https://mycrmapp.com",
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS("✅ Company profile created successfully")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("✅ Company profile already exists")
                )
            
            self.stdout.write(
                self.style.SUCCESS("\n🎉 SUCCESS! Your account is ready!")
            )
            self.stdout.write(f"📧 Email: {email}")
            self.stdout.write(f"🔑 Password: {password}")
            self.stdout.write(f"🌐 Login URL: https://mycrmapp-jrs0.onrender.com/auth/login/")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error creating user: {e}")
            )
            raise
