# Railway Deployment Guide for Django Multi-Purpose App

This guide will walk you through deploying your Django application to Railway platform.

## Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Django App**: Your app should be ready for deployment

## Step-by-Step Deployment Process

### Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

### Step 2: Create Railway Account and Project

1. **Go to Railway**: Visit [railway.app](https://railway.app)
2. **Sign up/Login**: Use your GitHub account to sign up
3. **Create New Project**: Click "New Project"
4. **Deploy from GitHub**: Select "Deploy from GitHub repo"
5. **Select Repository**: Choose your `mycrmapp` repository
6. **Deploy**: Click "Deploy Now"

### Step 3: Configure Environment Variables

1. **Go to Variables Tab**: In your Railway project dashboard
2. **Add Environment Variables**:
   ```
   SECRET_KEY=your-very-secure-secret-key-here
   DEBUG=False
   DEBUG_INVENTORY=False
   ```

3. **Generate Secret Key** (if you don't have one):
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

### Step 4: Add PostgreSQL Database

1. **Add Database Service**: In Railway dashboard, click "+ New"
2. **Select PostgreSQL**: Choose PostgreSQL from the database options
3. **Connect to App**: Railway will automatically connect the database to your app
4. **Database URL**: Railway will automatically set the `DATABASE_URL` environment variable

### Step 5: Configure Static Files

1. **Add Static Files Service** (Optional but recommended):
   - Click "+ New" in your project
   - Select "Static Files" service
   - Connect it to your main app

### Step 6: Deploy and Test

1. **Monitor Deployment**: Watch the deployment logs in Railway dashboard
2. **Check Build Logs**: Ensure all dependencies install correctly
3. **Test Your App**: Visit the provided Railway URL
4. **Create Superuser**: 
   ```bash
   # In Railway console or locally with Railway CLI
   python manage.py createsuperuser
   ```

## Important Files for Railway Deployment

### 1. `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn business_app.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. `Procfile`
```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn business_app.wsgi:application --bind 0.0.0.0:$PORT
```

### 3. `requirements.txt`
Your requirements.txt should include:
- `gunicorn` for serving the app
- `psycopg2-binary` for PostgreSQL
- `whitenoise` for static files
- `dj-database-url` for database URL parsing

## Environment Variables

### Required Variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` for production
- `DATABASE_URL`: Automatically provided by Railway PostgreSQL

### Optional Variables:
- `EMAIL_HOST`: SMTP server for emails
- `EMAIL_HOST_USER`: Email username
- `EMAIL_HOST_PASSWORD`: Email password
- `DEFAULT_FROM_EMAIL`: Default sender email

## Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check `requirements.txt` for all dependencies
   - Ensure Python version compatibility
   - Check build logs for specific errors

2. **Database Connection Issues**:
   - Verify PostgreSQL service is running
   - Check `DATABASE_URL` environment variable
   - Ensure migrations are running

3. **Static Files Not Loading**:
   - Verify `whitenoise` is in requirements.txt
   - Check `STATIC_ROOT` setting
   - Ensure `collectstatic` runs during deployment

4. **App Crashes on Startup**:
   - Check environment variables
   - Verify all required settings are configured
   - Check application logs

### Debugging Commands:

```bash
# Check Railway logs
railway logs

# Connect to Railway console
railway shell

# Run Django commands
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

## Post-Deployment Steps

1. **Create Superuser**: Set up admin access
2. **Test All Features**: Verify all app functionality works
3. **Set Up Custom Domain** (Optional): Configure your own domain
4. **Monitor Performance**: Use Railway's monitoring tools
5. **Set Up Backups**: Configure database backups

## Railway CLI (Optional)

Install Railway CLI for easier management:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Deploy
railway up
```

## Cost Considerations

- **Free Tier**: Railway offers a free tier with limited resources
- **Usage Limits**: Monitor your usage to avoid unexpected charges
- **Scaling**: Upgrade plans as your app grows

## Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Railway provides HTTPS by default
3. **Database Security**: Use strong passwords and limit access
4. **Regular Updates**: Keep dependencies updated

## Support and Resources

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Django Deployment**: [docs.djangoproject.com](https://docs.djangoproject.com/en/stable/howto/deployment/)
- **Community Support**: Railway Discord and GitHub discussions

---

**Note**: This deployment guide assumes you're using the standard Django project structure. Adjust paths and settings as needed for your specific setup.
