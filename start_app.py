#!/usr/bin/env python
"""
Simple startup script that ensures database is ready
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting MyCRM App...")
    
    # Check environment variables
    print("🔍 Checking environment variables...")
    print(f"DATABASE_URL: {'SET' if os.environ.get('DATABASE_URL') else 'NOT SET'}")
    print(f"RENDER: {'SET' if os.environ.get('RENDER') else 'NOT SET'}")
    
    # Setup database with migrations
    print("📦 Setting up database...")
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'setup_database'
        ], capture_output=True, text=True)
        
        print(f"Database setup output: {result.stdout}")
        if result.stderr:
            print(f"Database setup errors: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Database setup completed successfully")
        else:
            print(f"❌ Database setup failed with return code: {result.returncode}")
            print("⚠️  Continuing with server start...")
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("⚠️  Continuing with server start...")
    
    # Start Gunicorn
    print("🎉 Starting Gunicorn server...")
    os.execvp('gunicorn', [
        'gunicorn', 
        'business_app.wsgi:application',
        '--bind', '0.0.0.0:{}'.format(os.environ.get('PORT', '10000'))
    ])

if __name__ == "__main__":
    main()
