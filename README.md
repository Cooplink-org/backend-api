# Cooplink Platform

A high-performance, secure, and scalable web platform for developers to buy and sell code/projects with multilingual support (Uzbek, English, Russian), GitHub OAuth authentication, and MirPay payment integration.

## Features

- **Marketplace**: Upload, buy, and sell code/projects with automatic multilingual translation
- **Payments**: MirPay integration with escrow system and 5-day verification period
- **Authentication**: JWT-based auth + GitHub OAuth login
- **Admin Panel**: Django-Unfold powered admin interface
- **Analytics**: Sales statistics with Pandas and Chart.js
- **Multilingual**: Automatic translation using deep-translator
- **Security**: Comprehensive security measures and malware scanning

## Technology Stack

- **Backend**: Django 4.2, DRF, PostgreSQL, Redis, Celery
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Authentication**: JWT, GitHub OAuth
- **Payments**: MirPay API
- **Storage**: AWS S3
- **Translation**: deep-translator
- **Admin**: Django-Unfold
- **Monitoring**: Sentry, structlog

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd cooplink
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

### Environment Variables

```env
# Core Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/cooplink
REDIS_URL=redis://localhost:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/telegram/webhook/

# MirPay Configuration
MIRPAY_KASSA_ID=1413
MIRPAY_API_KEY=13ee7a1299bc5ced2e749899658a69c8
MIRPAY_BASE_URL=https://mirpay.uz/api
MIRPAY_SUCCESS_URL=https://your-domain.com/payment/success/
MIRPAY_FAILURE_URL=https://your-domain.com/payment/failure/

# AWS S3 Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=cooplink-files
AWS_S3_REGION_NAME=us-east-1

# Monitoring
SENTRY_DSN=your-sentry-dsn

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

## API Documentation

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

### Key API Endpoints

#### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Email/password login
- `POST /api/auth/telegram/initiate/` - Start Telegram auth
- `POST /api/auth/telegram/verify/` - Complete Telegram auth
- `GET /api/auth/profile/` - User profile

#### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Project details
- `POST /api/projects/{id}/purchase/` - Purchase project
- `GET /api/projects/{id}/download/` - Download purchased project

#### Payments
- `POST /api/payments/initiate/` - Initiate payment
- `POST /api/payments/callback/` - MirPay callback
- `POST /api/payments/withdraw/` - Withdraw funds

#### Analytics
- `GET /api/analytics/sales/` - Sales statistics
- `GET /api/analytics/dashboard/` - Dashboard data

## Project Structure

```
cooplink/
├── apps/                    # Django apps
│   ├── accounts/           # User authentication & profiles
│   ├── projects/           # Project marketplace
│   ├── news/              # News and updates
│   ├── payments/          # MirPay integration
│   ├── analytics/         # Sales analytics
│   ├── admin_panel/       # Django-Unfold customization
│   └── telegram/          # Telegram bot integration
├── core/                   # Core Django configuration
│   ├── settings/          # Environment-specific settings
│   └── utils/             # Shared utilities
├── static/                # Static files (React build)
├── media/                 # User uploads
├── templates/             # HTML templates
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Development Mode

The platform operates in two modes:

### Development Mode
- SQLite database
- Simulated payments (auto-success)
- Debug logging enabled
- Django debug toolbar

### Production Mode
- PostgreSQL + Redis
- Real MirPay integration
- Production-grade logging with Sentry
- AWS S3 storage

## Payment Workflow

1. **Purchase Initiation**: Buyer selects project and initiates purchase
2. **Escrow**: Funds held in escrow via MirPay (15-minute payment window)
3. **Verification Period**: 5-day window for buyer to test and verify project
4. **Resolution**:
   - **Satisfied**: Funds released to seller after 5 days
   - **Disputed**: Admin reviews code quality and makes decision

## Telegram Bot Integration

1. **Setup Bot**: Create bot via @BotFather and get token
2. **Configure Webhook**: Set webhook URL in environment variables
3. **Authentication Flow**:
   - User starts bot with `/start`
   - Bot provides authentication link
   - User completes auth on platform
   - JWT token issued and linked to Telegram account

## Multilingual Support

- **Supported Languages**: Uzbek, English, Russian
- **Auto-Translation**: Project descriptions and news automatically translated
- **Translation Cache**: Redis caching for performance
- **Fallback**: Original text if translation fails

## Security Features

- JWT-based authentication with refresh tokens
- Input sanitization (XSS, SQL injection prevention)
- CSRF protection
- File upload validation and malware scanning
- Rate limiting
- HTTPS enforcement in production
- Secure headers (HSTS, etc.)

## Testing

Run the test suite:

```bash
# Unit tests
python manage.py test

# Coverage report
coverage run --source='.' manage.py test
coverage report

# Load testing
locust -f tests/load_tests.py
```

## Deployment

### Docker Deployment

1. **Build image**
```bash
docker build -t cooplink .
```

2. **Run with docker-compose**
```bash
docker-compose up -d
```

### AWS ECS Deployment

1. **Push to ECR**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag cooplink:latest <account>.dkr.ecr.us-east-1.amazonaws.com/cooplink:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/cooplink:latest
```

2. **Deploy to ECS**: Use the provided ECS task definition

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure PostgreSQL and Redis
- [ ] Set up AWS S3 bucket
- [ ] Configure domain and SSL
- [ ] Set up Sentry monitoring
- [ ] Configure Telegram bot webhook
- [ ] Test MirPay integration
- [ ] Set up backup strategy
- [ ] Configure monitoring and alerts

## Performance Optimization

- **Database**: Indexed queries, query optimization
- **Caching**: Redis for API responses and translations
- **CDN**: AWS CloudFront for static files
- **Compression**: Gzip compression enabled
- **Monitoring**: Performance tracking with Sentry

## Monitoring and Logging

- **Application Logs**: Structured logging with structlog
- **Error Tracking**: Sentry integration
- **Performance Monitoring**: Response time tracking
- **Business Metrics**: Sales analytics and reporting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary and confidential.

## Support

For support and questions, contact the development team.

---

**Note**: This platform is built to Google-level senior developer standards with focus on scalability, security, and maintainability.
