#!/usr/bin/env python
"""
Deployment script for Railway platform
This script helps prepare the Django app for deployment
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from django.core.management import execute_from_command_line

def run_deployment_commands():
    """Run necessary commands for deployment"""
    print("🚀 Starting deployment preparation...")
    
    try:
        # Collect static files
        print("📦 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        # Run migrations
        print("🗄️ Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Create superuser if needed (optional)
        print("✅ Deployment preparation completed!")
        print("📝 Note: You may need to create a superuser manually after deployment")
        
    except Exception as e:
        print(f"❌ Error during deployment preparation: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_deployment_commands()
