#!/usr/bin/env python
"""
Deployment script for Railway
This script helps prepare your Django app for Railway deployment
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Prepare the app for deployment"""
    print("🚀 Preparing Django app for Railway deployment...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
    
    try:
        django.setup()
        print("✅ Django setup successful")
        
        # Run migrations
        print("📦 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed")
        
        # Collect static files
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected")
        
        print("🎉 Your app is ready for Railway deployment!")
        print("\nNext steps:")
        print("1. Push your code to GitHub")
        print("2. Create a Railway project")
        print("3. Connect your GitHub repository")
        print("4. Add PostgreSQL database")
        print("5. Set environment variables")
        print("6. Deploy!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
