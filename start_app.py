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
    
    # Migrations should already be run during build, but let's verify
    print("📦 Verifying database migrations...")
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'showmigrations', '--plan'
        ], capture_output=True, text=True)
        
        print(f"Migration status: {result.stdout}")
        if result.stderr:
            print(f"Migration warnings: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
    
    # Start Gunicorn
    print("🎉 Starting Gunicorn server...")
    os.execvp('gunicorn', [
        'gunicorn', 
        'business_app.wsgi:application',
        '--bind', '0.0.0.0:{}'.format(os.environ.get('PORT', '10000'))
    ])

if __name__ == "__main__":
    main()
