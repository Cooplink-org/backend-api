# 🚀 Cooplink - Developer Marketplace Platform

A comprehensive platform for developers to buy and sell code projects with integrated Telegram bot functionality.

## 📋 Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Telegram Bot](#telegram-bot)
- [Development](#development)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)

## ✨ Features

### 🔐 User Management
- Custom user authentication with JWT tokens
- Role-based access control (Buyer, Seller, Admin)
- Telegram integration for seamless authentication
- User profiles with balance management

### 📁 Project Marketplace
- Project listing and browsing
- Advanced search and filtering
- Category-based organization
- Secure file uploads with validation
- Project approval workflow

### 💰 Payment System
- MirPay payment gateway integration
- Secure transaction processing
- Balance management
- Transaction history and reporting

### 🤖 Telegram Bot
- Full-featured bot with rich interactions
- Seamless account linking
- Project browsing and purchasing
- Real-time notifications
- Multi-language support

### 📊 Analytics & Admin
- Comprehensive analytics dashboard
- Admin panel with advanced features
- Performance monitoring
- User behavior tracking

### 📰 Content Management
- News and announcements system
- Markdown support for rich content
- SEO-optimized content delivery

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ 
- PostgreSQL 12+
- Redis 6+
- Virtual Environment

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/cooplink.git
cd cooplink
```

2. **Set up virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
copy .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Start development server**
```bash
# Option 1: With Telegram bot
start_dev.bat  # Windows
python scripts/start_dev.py  # Cross-platform

# Option 2: Django only
python manage.py runserver

# Option 3: With custom management command
python manage.py runserver_with_bot
```

## 🏗️ Architecture

### Project Structure
```
cooplink/
├── apps/                    # Django applications
│   ├── accounts/           # User management
│   ├── projects/           # Project marketplace
│   ├── payments/           # Payment processing
│   ├── telegram/           # Telegram bot
│   ├── analytics/          # Analytics and reporting
│   ├── admin_panel/        # Enhanced admin
│   └── news/              # Content management
├── core/                   # Core Django settings
│   ├── settings/          # Environment-specific settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI application
├── scripts/               # Utility scripts
├── static/               # Static files
├── templates/            # Django templates
├── media/                # User uploads
├── logs/                 # Application logs
└── docs/                 # Documentation
```

### Technology Stack
- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL with Redis caching
- **Task Queue**: Celery with Redis broker
- **Bot Framework**: python-telegram-bot
- **Frontend Integration**: CORS-enabled API
- **Authentication**: JWT with Simple JWT
- **Documentation**: DRF Spectacular (OpenAPI)
- **Admin**: Django Unfold (Modern admin interface)

## 📚 API Documentation

### Authentication Endpoints
```
POST /api/auth/register/           # User registration
POST /api/auth/login/              # User login
POST /api/auth/token/refresh/      # Token refresh
GET  /api/auth/profile/            # User profile
```

### Project Endpoints
```
GET    /api/projects/              # List projects
POST   /api/projects/              # Create project
GET    /api/projects/{id}/         # Project details
PUT    /api/projects/{id}/         # Update project
DELETE /api/projects/{id}/         # Delete project
```

### Payment Endpoints
```
POST /api/payments/create/         # Create payment
GET  /api/payments/status/{id}/    # Payment status
POST /api/payments/webhook/        # Payment webhook
```

### Telegram Endpoints
```
POST /api/telegram/webhook/        # Bot webhook
GET  /api/telegram/bot/status/     # Bot status
GET  /api/telegram/bot/commands/   # Available commands
```

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## 🤖 Telegram Bot

### Features
- **Account Management**: Link existing accounts or create new ones
- **Project Browser**: Browse and search projects directly in Telegram
- **Secure Authentication**: JWT-based secure login flow
- **Real-time Notifications**: Get notified about purchases, sales, and updates
- **Multi-language Support**: Uzbek, Russian, and English
- **Rich Interactions**: Inline keyboards and interactive menus

### Bot Commands
```
/start          - 🚀 Start using Cooplink Bot
/help           - 📚 Show help and commands
/login          - 🔐 Login to your account
/profile        - 👤 View your profile
/projects       - 📁 Browse latest projects
/news           - 📰 Latest platform news
/stats          - 📊 Platform statistics
/balance        - 💰 Check your balance
/notifications  - 🔔 Notification settings
/support        - 🆘 Get support
```

### Setup Instructions
1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Update `TELEGRAM_BOT_TOKEN` in `.env`
4. For webhook mode, set `TELEGRAM_WEBHOOK_URL`
5. Start the bot:
```bash
# Polling mode (development)
python manage.py run_telegram_bot --mode=polling

# Webhook mode (production)
python manage.py run_telegram_bot --mode=webhook
```

## 🛠️ Development

### Environment Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Code formatting
black .
isort .

# Linting
flake8 .
```

### Development Commands
```bash
# Create superuser
python manage.py createsuperuser

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Load sample data
python manage.py loaddata fixtures/sample_data.json

# Run Telegram bot only
python manage.py run_telegram_bot

# Run with both Django and bot
python manage.py runserver_with_bot
```

### Development Workflow
1. Create feature branch from `develop`
2. Implement changes with tests
3. Run test suite and ensure coverage
4. Submit pull request with detailed description
5. Code review and merge

## 🚀 Deployment

### Environment Variables
```bash
# Django Configuration
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cooplink
DB_NAME=cooplink
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com

# Payment Gateway
MIRPAY_KASSA_ID=your-kassa-id
MIRPAY_API_KEY=your-api-key
MIRPAY_SUCCESS_URL=https://yourdomain.com/payment/success/
MIRPAY_FAILURE_URL=https://yourdomain.com/payment/failure/

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=cooplink-files
AWS_S3_REGION_NAME=us-east-1

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale web=3

# View logs
docker-compose logs -f
```

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up SSL certificates
- [ ] Configure static file serving
- [ ] Set up database backups
- [ ] Configure monitoring (Sentry, etc.)
- [ ] Set up log rotation
- [ ] Configure rate limiting
- [ ] Set up health checks

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Load testing with Locust
locust -f tests/load_test.py
```

### Test Structure
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── fixtures/          # Test data
└── load_test.py       # Performance tests
```

## 📈 Monitoring & Analytics

### Built-in Analytics
- User registration and activity metrics
- Project performance tracking
- Payment transaction analytics
- Bot usage statistics
- API endpoint performance

### Health Checks
- Database connectivity
- Redis availability
- Bot status monitoring
- External service health

### Logging
- Structured logging with JSON format
- Centralized log collection
- Error tracking with Sentry
- Performance monitoring

## 🔒 Security

### Security Features
- JWT-based authentication
- Rate limiting on API endpoints
- CSRF protection
- SQL injection prevention
- XSS protection
- File upload validation
- Secure payment processing

### Security Best Practices
- Regular dependency updates
- Automated security scanning
- Environment variable management
- Database encryption
- API key rotation
- Access logging

## 🤝 Contributing

### Development Guidelines
1. Follow PEP 8 style guidelines
2. Write comprehensive tests
3. Document all public APIs
4. Use meaningful commit messages
5. Keep pull requests focused

### Code Style
- Use Black for code formatting
- Use isort for import ordering
- Follow Django best practices
- Write docstrings for all functions
- Use type hints where appropriate

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📞 Support

### Getting Help
- **Documentation**: Check this README and inline docs
- **Issues**: Create a GitHub issue for bugs
- **Features**: Submit feature requests via GitHub
- **Security**: Email security@cooplink.uz for security issues

### Community
- **Discord**: [Join our Discord server](https://discord.gg/cooplink)
- **Telegram**: [Developer Community](https://t.me/cooplink_dev)
- **Email**: support@cooplink.uz

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and DRF communities
- python-telegram-bot library
- All contributors and testers

---

**Made with ❤️ by the Cooplink Team**

For more information, visit [cooplink.uz](https://cooplink.uz)
