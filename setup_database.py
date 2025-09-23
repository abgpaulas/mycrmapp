#!/usr/bin/env python
"""
Database setup script for Render deployment
This script ensures the database is properly set up before starting the app
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_database():
    """Setup the database with migrations"""
    print("🚀 Setting up database for MyCRM App...")
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
        django.setup()
        print("✅ Django setup successful")
        
        # Run migrations
        print("📦 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput', '--verbosity=2'])
        print("✅ Migrations completed successfully")
        
        # Check database
        print("🔍 Verifying database setup...")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✅ Database tables created: {len(tables)} tables")
            for table in tables:
                print(f"   - {table[0]}")
        
        print("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    if not success:
        sys.exit(1)
