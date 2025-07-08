#!/usr/bin/env python3
"""
Production deployment script for Cooplink
This script handles the deployment process with proper checks and optimizations
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionDeployment:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.env_file = self.base_dir / '.env.production'
        self.requirements_file = self.base_dir / 'requirements.txt'
        
    def check_environment(self):
        """Check if production environment is properly configured"""
        logger.info("🔍 Checking production environment...")
        
        if not self.env_file.exists():
            logger.error("❌ .env.production file not found!")
            logger.info("💡 Please copy .env.production.template to .env.production and configure it")
            return False
            
        # Check required environment variables
        required_vars = [
            'SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST',
            'ALLOWED_HOSTS', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'
        ]
        
        # Load environment variables
        from decouple import config
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.prod')
        
        missing_vars = []
        for var in required_vars:
            if not config(var, default=''):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        logger.info("✅ Environment configuration looks good!")
        return True
    
    def install_dependencies(self):
        """Install production dependencies"""
        logger.info("📦 Installing production dependencies...")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(self.requirements_file)
            ], check=True, cwd=self.base_dir)
            logger.info("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False
    
    def collect_static_files(self):
        """Collect static files for production"""
        logger.info("📁 Collecting static files...")
        
        try:
            subprocess.run([
                sys.executable, 'manage.py', 'collectstatic', '--noinput'
            ], check=True, cwd=self.base_dir)
            logger.info("✅ Static files collected successfully!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to collect static files: {e}")
            return False
    
    def run_migrations(self):
        """Run database migrations"""
        logger.info("🗄️  Running database migrations...")
        
        try:
            subprocess.run([
                sys.executable, 'manage.py', 'migrate', '--noinput'
            ], check=True, cwd=self.base_dir)
            logger.info("✅ Database migrations completed!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to run migrations: {e}")
            return False
    
    def run_system_checks(self):
        """Run Django system checks"""
        logger.info("🔍 Running system checks...")
        
        try:
            subprocess.run([
                sys.executable, 'manage.py', 'check', '--deploy'
            ], check=True, cwd=self.base_dir)
            logger.info("✅ System checks passed!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ System checks failed: {e}")
            return False
    
    def create_superuser(self):
        """Create superuser if needed"""
        logger.info("👤 Checking for superuser...")
        
        try:
            result = subprocess.run([
                sys.executable, 'manage.py', 'shell', '-c',
                'from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())'
            ], capture_output=True, text=True, cwd=self.base_dir)
            
            if 'False' in result.stdout:
                logger.info("Creating superuser...")
                subprocess.run([
                    sys.executable, 'manage.py', 'createsuperuser', '--noinput'
                ], check=True, cwd=self.base_dir)
                logger.info("✅ Superuser created!")
            else:
                logger.info("✅ Superuser already exists!")
            
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Could not create superuser: {e}")
            return True  # Non-critical
    
    def compress_static_files(self):
        """Compress static files for better performance"""
        logger.info("🗜️  Compressing static files...")
        
        try:
            # Check if django-compressor is installed
            subprocess.run([
                sys.executable, '-c', 'import compressor'
            ], check=True, capture_output=True)
            
            subprocess.run([
                sys.executable, 'manage.py', 'compress', '--force'
            ], check=True, cwd=self.base_dir)
            logger.info("✅ Static files compressed!")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("ℹ️  Django-compressor not available, skipping compression")
            return True
    
    def optimize_database(self):
        """Optimize database for production"""
        logger.info("🔧 Optimizing database...")
        
        try:
            # Run database optimization commands
            subprocess.run([
                sys.executable, 'manage.py', 'shell', '-c',
                '''
import django
from django.core.management import call_command
from django.db import connection

# Analyze database tables
with connection.cursor() as cursor:
    cursor.execute("ANALYZE;")
    
print("Database optimization completed!")
                '''
            ], check=True, cwd=self.base_dir)
            logger.info("✅ Database optimized!")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Database optimization failed: {e}")
            return True  # Non-critical
    
    def clear_cache(self):
        """Clear all caches"""
        logger.info("🧹 Clearing cache...")
        
        try:
            subprocess.run([
                sys.executable, 'manage.py', 'shell', '-c',
                '''
from django.core.cache import cache
cache.clear()
print("Cache cleared!")
                '''
            ], check=True, cwd=self.base_dir)
            logger.info("✅ Cache cleared!")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Cache clearing failed: {e}")
            return True  # Non-critical
    
    def run_security_check(self):
        """Run security checks"""
        logger.info("🔒 Running security checks...")
        
        try:
            subprocess.run([
                sys.executable, 'manage.py', 'check', '--deploy', '--fail-level', 'WARNING'
            ], check=True, cwd=self.base_dir)
            logger.info("✅ Security checks passed!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Security checks failed: {e}")
            return False
    
    def deploy(self):
        """Main deployment function"""
        logger.info("🚀 Starting production deployment...")
        
        steps = [
            ("Environment Check", self.check_environment),
            ("Install Dependencies", self.install_dependencies),
            ("Run System Checks", self.run_system_checks),
            ("Run Database Migrations", self.run_migrations),
            ("Collect Static Files", self.collect_static_files),
            ("Compress Static Files", self.compress_static_files),
            ("Create Superuser", self.create_superuser),
            ("Optimize Database", self.optimize_database),
            ("Clear Cache", self.clear_cache),
            ("Security Check", self.run_security_check),
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            logger.info(f"🔄 Executing: {step_name}")
            
            if not step_func():
                failed_steps.append(step_name)
                logger.error(f"❌ Failed: {step_name}")
                
                # Critical steps that should stop deployment
                critical_steps = [
                    "Environment Check", "Install Dependencies", 
                    "Run System Checks", "Run Database Migrations",
                    "Security Check"
                ]
                
                if step_name in critical_steps:
                    logger.error("🛑 Deployment stopped due to critical failure!")
                    return False
            else:
                logger.info(f"✅ Completed: {step_name}")
        
        if failed_steps:
            logger.warning(f"⚠️  Deployment completed with warnings. Failed steps: {', '.join(failed_steps)}")
        else:
            logger.info("🎉 Deployment completed successfully!")
        
        logger.info("📋 Post-deployment checklist:")
        logger.info("   - Configure web server (Nginx/Apache)")
        logger.info("   - Set up SSL certificates")
        logger.info("   - Configure process manager (systemd/supervisor)")
        logger.info("   - Set up monitoring and logging")
        logger.info("   - Configure backup strategy")
        logger.info("   - Test all endpoints")
        
        return True

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
Production Deployment Script for Cooplink

Usage: python scripts/deploy_production.py

This script will:
1. Check environment configuration
2. Install production dependencies
3. Run system checks
4. Execute database migrations
5. Collect and compress static files
6. Create superuser (if needed)
7. Optimize database
8. Clear cache
9. Run security checks

Make sure to:
- Configure .env.production file
- Set DJANGO_SETTINGS_MODULE=core.settings.prod
- Have proper database and Redis access
        """)
        return
    
    deployment = ProductionDeployment()
    success = deployment.deploy()
    
    if success:
        logger.info("✅ Deployment process completed!")
        sys.exit(0)
    else:
        logger.error("❌ Deployment process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
