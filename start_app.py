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
    
    # Run migrations
    print("📦 Running database migrations...")
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate', '--noinput', '--verbosity=2'
        ], capture_output=True, text=True)
        
        print(f"Migration stdout: {result.stdout}")
        print(f"Migration stderr: {result.stderr}")
        print(f"Migration return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully")
        else:
            print(f"❌ Migration error: {result.stderr}")
            print("⚠️  Continuing with server start despite migration failure...")
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        print("⚠️  Continuing with server start despite migration error...")
    
    # Start Gunicorn
    print("🎉 Starting Gunicorn server...")
    os.execvp('gunicorn', [
        'gunicorn', 
        'business_app.wsgi:application',
        '--bind', '0.0.0.0:{}'.format(os.environ.get('PORT', '10000'))
    ])

if __name__ == "__main__":
    main()
