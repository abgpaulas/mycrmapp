#!/usr/bin/env python
"""
Simple startup script that ensures database is ready
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting MyCRM App...")
    
    # Run migrations
    print("📦 Running database migrations...")
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate', '--noinput'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully")
        else:
            print(f"❌ Migration error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
    
    # Start Gunicorn
    print("🎉 Starting Gunicorn server...")
    os.execvp('gunicorn', [
        'gunicorn', 
        'business_app.wsgi:application',
        '--bind', '0.0.0.0:{}'.format(os.environ.get('PORT', '10000'))
    ])

if __name__ == "__main__":
    main()
