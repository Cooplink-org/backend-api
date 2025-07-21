# 🚀 Cooplink Production Deployment Guide

## Changes Made

### ✅ Fixed Production Issues
- **Removed debug tools**: Eliminated all development debugging code
- **Fixed syntax errors**: Corrected email settings syntax error in prod.py
- **Fixed Sentry DSN bug**: Resolved "Unsupported scheme" error by conditionally initializing Sentry only when DSN is provided
- **Removed insecure defaults**: Removed hardcoded debug values and insecure settings
- **Optimized settings**: Set manage.py to use production settings by default
- **Updated dependencies**: All package versions updated to latest compatible versions
- **Cleaned codebase**: Removed comments and debug prints throughout the application

### ✅ CORS & Security Configuration
The following domains are now allowed in CORS and CSRF trusted origins:
- `cloude.qzz.io`
- `cooplink.onrender.com` 
- `*.pythonanywhere.com`
- `*.sevella.com`
- `*.sevella.app`

### ✅ Environment Configuration
- **Consolidated `.env`**: Single environment file for all configurations
- **Removed duplicate files**: Deleted `.env.production`, `.env.production.template` 
- **Production-ready variables**: All environment variables configured for production

### ✅ Docker & Deployment
- **Updated Dockerfile**: Production-optimized container configuration
- **Fixed docker-compose**: Uses main Dockerfile, removed references to production-specific files
- **Security hardening**: Non-root user, proper file permissions

### ✅ File Cleanup
**Removed Files:**
- `.env.production*` (consolidated into main `.env`)
- `Dockerfile.production` (merged into main Dockerfile)
- `docker-compose.production.yml`
- `requirements-production.txt` (kept `requirements.production.txt`)
- `scripts/deploy_production.py`
- `scripts/start_dev.py`

## 🔐 Security Configuration

### Environment Variables Required
Update your `.env` file with production values:

```bash
SECRET_KEY=your_actual_secret_key_here
DEBUG=False
DATABASE_URL=your_production_database_url
REDIS_URL=your_production_redis_url
EMAIL_HOST_PASSWORD=your_actual_email_password
SENTRY_DSN=your_sentry_dsn_for_error_tracking
```

### SSL/TLS Configuration
- HTTPS redirect enabled
- Secure cookies configured
- HSTS headers enabled
- Security middleware active

## 🚀 Deployment Instructions

### Option 1: Docker Deployment
```bash
# 1. Build and run with docker-compose
docker-compose up -d --build

# 2. Run migrations
docker-compose exec web python manage.py migrate

# 3. Create superuser
docker-compose exec web python manage.py createsuperuser

# 4. Collect static files (if not using S3)
docker-compose exec web python manage.py collectstatic --noinput
```

### Option 2: Direct Deployment
```bash
# 1. Install dependencies
pip install -r requirements.production.txt

# 2. Set environment
export DJANGO_SETTINGS_MODULE=core.settings.prod

# 3. Run migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Start with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 3 core.wsgi:application
```

### Option 3: Platform Deployments

#### Render.com
- Use the provided `Dockerfile`
- Set environment variables in Render dashboard
- Database: Use PostgreSQL add-on
- Redis: Use Redis add-on

#### PythonAnywhere
- Upload code to Files section
- Install requirements: `pip3.10 install --user -r requirements.production.txt`
- Configure WSGI file to point to `core.wsgi`
- Set environment variables in Files tab

#### Railway/Heroku
- Connect GitHub repository
- Set environment variables
- Use Dockerfile for deployment

## 📊 Post-Deployment Checklist

### ✅ Verify Deployment
1. **Health Check**: Visit `/api/` endpoint
2. **Admin Access**: Visit `/admin/` and login
3. **API Documentation**: Check `/api/docs/` (Swagger UI)
4. **CORS Test**: Test API calls from allowed domains

### ✅ Monitor Application
1. **Logs**: Check application logs for errors
2. **Performance**: Monitor response times
3. **Database**: Verify database connections
4. **Redis**: Check cache functionality
5. **Celery**: Ensure background tasks are running

### ✅ Security Verification
1. **HTTPS**: Verify SSL certificate is working
2. **Headers**: Check security headers are present
3. **CORS**: Test cross-origin requests
4. **Rate Limiting**: Verify API rate limiting works

## 🔧 Production Settings Overview

### Key Production Features
- **DEBUG=False**: No debug information exposed
- **Secure cookies**: HTTPS-only cookies
- **CORS configured**: Only allowed origins accepted
- **Rate limiting**: API endpoints protected
- **Logging**: Comprehensive logging to files
- **Caching**: Redis-based caching enabled
- **Static files**: Whitenoise for static file serving
- **Database**: PostgreSQL with connection pooling
- **Email**: SMTP backend configured
- **Monitoring**: Sentry integration ready

### Performance Optimizations
- **Gunicorn**: Production WSGI server
- **Redis caching**: Fast data retrieval
- **Static file compression**: Optimized asset delivery
- **Database connection pooling**: Efficient database usage
- **Celery background tasks**: Asynchronous processing

## 🛠 Maintenance

### Regular Tasks
```bash
# Update dependencies
pip install -r requirements.production.txt --upgrade

# Database migrations
python manage.py migrate

# Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Collect static files
python manage.py collectstatic --noinput
```

### Backup Strategy
- **Database**: Regular PostgreSQL backups
- **Media files**: Backup user uploads
- **Environment**: Secure backup of `.env` file

## 📞 Support

For deployment issues:
1. Check logs in `/app/logs/` directory
2. Verify all environment variables are set
3. Ensure database and Redis are accessible
4. Check CORS/CSRF settings for your domain

---

**Note**: Remember to replace placeholder values in `.env` with actual production values before deployment.
