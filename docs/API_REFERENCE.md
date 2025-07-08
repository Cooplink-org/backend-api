# 📚 Cooplink API Reference

Comprehensive API documentation for the Cooplink Developer Marketplace Platform.

## 🔗 Base URL
- **Development**: `http://localhost:8000/api/`
- **Production**: `https://api.cooplink.uz/api/`

## 🔑 Authentication

### JWT Token Authentication
All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Token Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login/` | Login with email/password |
| POST | `/auth/register/` | Create new account |
| POST | `/auth/token/refresh/` | Refresh JWT token |

## 👥 User Management

### Account Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/auth/profile/` | ✅ | Get user profile |
| PUT | `/auth/profile/` | ✅ | Update user profile |
| POST | `/auth/telegram/initiate/` | ❌ | Start Telegram auth |
| POST | `/auth/telegram/verify/` | ❌ | Verify Telegram auth |
| POST | `/auth/telegram/link/` | ✅ | Link Telegram account |

### User Registration
```json
POST /auth/register/
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "buyer"
}
```

### User Login
```json
POST /auth/login/
{
  "email": "john@example.com",
  "password": "secure_password123"
}
```

## 📁 Project Management

### Project Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/projects/` | ❌ | List all projects |
| POST | `/projects/` | ✅ | Create new project |
| GET | `/projects/{id}/` | ❌ | Get project details |
| PUT | `/projects/{id}/` | ✅ | Update project |
| DELETE | `/projects/{id}/` | ✅ | Delete project |
| POST | `/projects/{id}/purchase/` | ✅ | Purchase project |
| GET | `/projects/{id}/download/` | ✅ | Download project files |

### Create Project
```json
POST /projects/
{
  "title": "React E-commerce Template",
  "description": "Modern e-commerce template built with React and TypeScript",
  "category": "web",
  "price": 50000,
  "programming_languages": ["javascript", "typescript"],
  "frameworks": ["react", "nodejs"],
  "features": ["responsive", "dark-mode", "pwa"],
  "demo_url": "https://demo.example.com",
  "documentation": "# Installation\n\n```bash\nnpm install\n```",
  "tags": "react,ecommerce,typescript"
}
```

### Query Parameters
- `?search=query` - Search in title/description
- `?category=web` - Filter by category
- `?min_price=1000&max_price=50000` - Price range
- `?languages=javascript,python` - Programming languages
- `?frameworks=react,django` - Frameworks
- `?sort=created_at` - Sort by field
- `?ordering=-price` - Order direction

## 💰 Payment System

### Payment Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/payments/create/` | ✅ | Create payment |
| GET | `/payments/status/{id}/` | ✅ | Check payment status |
| POST | `/payments/webhook/` | ❌ | Payment webhook |
| GET | `/payments/balance/` | ✅ | Get user balance |
| GET | `/payments/transactions/` | ✅ | List transactions |
| POST | `/payments/withdraw/` | ✅ | Request withdrawal |

### Create Payment
```json
POST /payments/create/
{
  "amount": 50000,
  "currency": "UZS",
  "description": "Purchase: React E-commerce Template",
  "project_id": 123,
  "payment_method": "mirpay"
}
```

### Transaction Response
```json
{
  "id": "txn_abc123",
  "amount": 50000,
  "currency": "UZS",
  "status": "completed",
  "type": "purchase",
  "description": "Purchase: React E-commerce Template",
  "created_at": "2024-01-15T10:30:00Z",
  "project": {
    "id": 123,
    "title": "React E-commerce Template"
  }
}
```

## 📰 Content Management

### News Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/news/` | ❌ | List news articles |
| GET | `/news/{id}/` | ❌ | Get article details |
| POST | `/news/{id}/like/` | ✅ | Like/unlike article |
| POST | `/news/{id}/comments/` | ✅ | Add comment |
| GET | `/news/{id}/comments/` | ❌ | List comments |

### News Article Response
```json
{
  "id": 1,
  "title": "Platform Update v2.0",
  "slug": "platform-update-v2-0",
  "content": "We're excited to announce...",
  "excerpt": "Major updates and new features",
  "featured_image": "https://cdn.cooplink.uz/news/featured.jpg",
  "author": {
    "id": 1,
    "username": "admin",
    "first_name": "Admin"
  },
  "category": "updates",
  "tags": ["update", "features", "announcement"],
  "status": "published",
  "view_count": 1250,
  "like_count": 45,
  "comment_count": 12,
  "reading_time": "3 min read",
  "is_liked": false,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

## 🤖 Telegram Integration

### Telegram Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/telegram/webhook/` | ❌ | Bot webhook endpoint |
| GET | `/telegram/bot/status/` | ❌ | Bot status |
| GET | `/telegram/bot/commands/` | ❌ | Available commands |

### Bot Status Response
```json
{
  "bot_configured": true,
  "token_configured": true,
  "webhook_url": "https://api.cooplink.uz/api/telegram/webhook/",
  "status": "active"
}
```

## 📊 Analytics

### Analytics Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/analytics/dashboard/` | ✅ | Dashboard overview |
| GET | `/analytics/user/` | ✅ | User analytics |
| GET | `/analytics/revenue/` | ✅ | Revenue analytics |
| POST | `/analytics/track/page-view/` | ❌ | Track page view |
| POST | `/analytics/track/search/` | ❌ | Track search query |

### Dashboard Response
```json
{
  "total_users": 1250,
  "total_projects": 450,
  "total_revenue": 12500000,
  "active_users_today": 89,
  "new_signups_today": 15,
  "projects_sold_today": 23,
  "revenue_today": 567000,
  "growth_rate": {
    "users": 12.5,
    "projects": 8.3,
    "revenue": 15.7
  }
}
```

## 🛠️ Admin Panel

### Admin Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/stats/` | ✅ | Admin dashboard stats |
| GET | `/admin/activities/` | ✅ | Recent activities |
| POST | `/admin/projects/{id}/approve/` | ✅ | Approve project |
| POST | `/admin/projects/{id}/reject/` | ✅ | Reject project |
| GET | `/admin/users/` | ✅ | List users |
| POST | `/admin/users/{id}/verify/` | ✅ | Verify user |

## 🔍 Search & Filtering

### Advanced Search
```
GET /projects/?search=react&category=web&min_price=1000&max_price=50000&languages=javascript&frameworks=react&sort=created_at&ordering=-price
```

### Pagination
All list endpoints support pagination:
```json
{
  "count": 450,
  "next": "http://localhost:8000/api/projects/?page=3",
  "previous": "http://localhost:8000/api/projects/?page=1",
  "results": [...]
}
```

## 📤 File Uploads

### Project Files
```
POST /projects/
Content-Type: multipart/form-data

{
  "title": "Project Title",
  "description": "Description",
  "project_file": <file_upload>,
  "preview_images": [<file1>, <file2>],
  "documentation_file": <file_upload>
}
```

### Supported File Types
- **Project Files**: .zip, .tar.gz, .rar (max 100MB)
- **Images**: .jpg, .jpeg, .png, .gif (max 5MB each)
- **Documentation**: .pdf, .md, .txt (max 10MB)

## ⚠️ Error Responses

### Standard Error Format
```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {
    "field_name": ["Specific field errors"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

## 🚦 Rate Limiting

### Default Limits
- **Anonymous users**: 60 requests/minute
- **Authenticated users**: 1000 requests/hour
- **Admin users**: No limits

### Rate Limit Headers
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642248600
```

## 🔧 Development Tools

### Interactive Documentation
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

### Testing Endpoints
```bash
# Health check
curl http://localhost:8000/api/health/

# Get user profile (with auth)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/auth/profile/

# Search projects
curl "http://localhost:8000/api/projects/?search=react&category=web"
```

## 📝 Examples

### Complete Purchase Flow
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# 2. Create payment
curl -X POST http://localhost:8000/api/payments/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 50000, "project_id": 123, "payment_method": "mirpay"}'

# 3. Check payment status
curl -X GET http://localhost:8000/api/payments/status/payment_id/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Download project (after successful payment)
curl -X GET http://localhost:8000/api/projects/123/download/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Telegram Authentication Flow
```bash
# 1. Initiate Telegram auth
curl -X POST http://localhost:8000/api/auth/telegram/initiate/ \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456789}'

# 2. Verify auth token (from Telegram)
curl -X POST http://localhost:8000/api/auth/telegram/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "auth_token_from_telegram"}'
```

---

For more detailed examples and integration guides, check the [main documentation](README.md).
