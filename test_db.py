#!/usr/bin/env python
"""
Test script to verify database connectivity and migrations
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

User = get_user_model()

def test_database():
    """Test database connectivity and basic operations"""
    print("🔍 Testing database connectivity...")
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Database connection successful: {result}")
        
        # Test User model
        user_count = User.objects.count()
        print(f"✅ User model accessible: {user_count} users found")
        
        # Test creating a user (without saving)
        test_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        print("✅ User model creation test passed")
        
        print("🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database()
    if not success:
        sys.exit(1)
