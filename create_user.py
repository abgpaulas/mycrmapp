#!/usr/bin/env python
"""
Manual User Creation Script for MyCRM App
This script creates a user account directly in the database, bypassing the registration form.
Run this script after the database migrations have been applied.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import CompanyProfile

User = get_user_model()

def create_user():
    """Create a new user account with company profile"""
    
    print("🚀 Creating user account for MyCRM App...")
    
    # User details
    email = "admin@mycrmapp.com"
    password = "admin123"
    first_name = "Admin"
    last_name = "User"
    phone = "+1234567890"
    
    try:
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            print(f"✅ User with email {email} already exists!")
            user = User.objects.get(email=email)
        else:
            # Create new user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            print(f"✅ User created successfully: {email}")
        
        # Create company profile if it doesn't exist
        if not hasattr(user, 'company_profile'):
            company_profile = CompanyProfile.objects.create(
                user=user,
                company_name="MyCRM Company",
                company_email=email,
                company_phone=phone,
                company_address="123 Business Street, City, State 12345",
                company_website="https://mycrmapp.com",
                is_active=True
            )
            print("✅ Company profile created successfully")
        else:
            print("✅ Company profile already exists")
        
        print("\n🎉 SUCCESS! Your account is ready!")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"🌐 Login URL: https://mycrmapp-jrs0.onrender.com/auth/login/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

if __name__ == "__main__":
    success = create_user()
    if success:
        print("\n✅ You can now login to your app!")
    else:
        print("\n❌ Failed to create user. Check the error above.")
        sys.exit(1)
