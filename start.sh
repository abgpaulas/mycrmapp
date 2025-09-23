#!/bin/bash
# Startup script for Django app on Render

# Run migrations
python manage.py migrate

# Start the application
exec gunicorn business_app.wsgi:application --bind 0.0.0.0:$PORT
