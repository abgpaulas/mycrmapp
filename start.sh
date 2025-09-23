#!/bin/bash
# Startup script for Django app on Render

echo "🚀 Starting Django app deployment..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set!"
    echo "Please add DATABASE_URL to your environment variables in Render."
    exit 1
fi

echo "✅ DATABASE_URL is set: ${DATABASE_URL:0:20}..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import os
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migrations failed"
    exit 1
fi

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
python -c "
import os
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_app.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating default superuser...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('✅ Superuser already exists')
"

echo "🎉 Starting application server..."

# Start the application
exec gunicorn business_app.wsgi:application --bind 0.0.0.0:$PORT --timeout 120
