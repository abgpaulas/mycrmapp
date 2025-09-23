#!/bin/bash
# Startup script for Django app on Render

echo "Starting Django app deployment..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set!"
    echo "Please add DATABASE_URL to your environment variables in Render."
    exit 1
fi

echo "DATABASE_URL is set, running migrations..."

# Run migrations
python manage.py migrate

echo "Migrations completed, starting application..."

# Start the application
exec gunicorn business_app.wsgi:application --bind 0.0.0.0:$PORT
