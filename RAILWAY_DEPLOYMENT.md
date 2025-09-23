# Railway Deployment Guide

## Environment Variables to Set in Railway

You need to set the following environment variables in your Railway project:

### Required Variables:
- `SECRET_KEY`: A secure Django secret key (generate one using Django's `get_random_secret_key()`)
- `DEBUG`: Set to `False` for production
- `DEBUG_INVENTORY`: Set to `False` for production

### Automatically Provided by Railway:
- `RAILWAY_PUBLIC_DOMAIN`: Your app's domain (e.g., `your-app-name.railway.app`)
- `DATABASE_URL`: PostgreSQL connection string
- `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`: PostgreSQL credentials

### Optional Variables:
- `EMAIL_HOST`: SMTP server for emails (e.g., `smtp.gmail.com`)
- `EMAIL_PORT`: SMTP port (usually `587`)
- `EMAIL_USE_TLS`: Set to `True`
- `EMAIL_HOST_USER`: Your email address
- `EMAIL_HOST_PASSWORD`: Your email app password
- `DEFAULT_FROM_EMAIL`: Default sender email
- `SERVER_EMAIL`: Server email for error notifications
- `REDIS_URL`: If you add Redis service to Railway

## Deployment Steps:

1. **Create Railway Account**: Go to [railway.app](https://railway.app) and sign up
2. **Create New Project**: Click "New Project" and select "Deploy from GitHub repo"
3. **Connect Repository**: Connect your GitHub repository
4. **Add PostgreSQL**: In your Railway project, click "New" → "Database" → "PostgreSQL"
5. **Set Environment Variables**: Go to your service → Variables tab and add the required variables
6. **Deploy**: Railway will automatically deploy your app

## Generate Secret Key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Post-Deployment:
1. Run migrations: Railway will handle this automatically, but you can also run:
   ```bash
   python manage.py migrate
   ```
2. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
3. Collect static files (handled automatically by Railway)

## File Structure:
- `Procfile`: Defines how to run your app
- `railway.json`: Railway-specific configuration
- `requirements.txt`: Python dependencies
- `business_app/settings_production.py`: Production settings (optional)

Your app will be available at: `https://your-app-name.railway.app`
