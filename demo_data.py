#!/usr/bin/env python
"""
Demo Data Creation Script
This file creates sample data for development and testing purposes.
DO NOT run this in production!
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()

from apps.accounts.models import User
from apps.news.models import NewsCategory, NewsArticle
from apps.projects.models import Project, ProjectTranslation, Purchase
from apps.payments.models import PaymentMethod, Transaction

def create_users():
    """Create demo users"""
    print("Creating demo users...")
    
    # Create admin user
    admin, created = User.objects.get_or_create(
        email='admin@cooplink.uz',
        defaults={
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'is_verified': True,
            'balance': Decimal('100000.00')
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"Created admin user: {admin.email}")
    
    # Create sellers
    sellers = []
    seller_data = [
        ('john.doe@example.com', 'john_doe', 'John', 'Doe'),
        ('jane.smith@example.com', 'jane_smith', 'Jane', 'Smith'),
        ('alex.dev@example.com', 'alex_dev', 'Alex', 'Developer'),
    ]
    
    for email, username, first_name, last_name in seller_data:
        seller, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'seller',
                'is_verified': True,
                'balance': Decimal(str(random.randint(5000, 50000)))
            }
        )
        if created:
            seller.set_password('demo123')
            seller.save()
            print(f"Created seller: {seller.email}")
        sellers.append(seller)
    
    # Create buyers
    buyers = []
    buyer_data = [
        ('buyer1@example.com', 'buyer1', 'Alice', 'Johnson'),
        ('buyer2@example.com', 'buyer2', 'Bob', 'Wilson'),
        ('buyer3@example.com', 'buyer3', 'Carol', 'Brown'),
    ]
    
    for email, username, first_name, last_name in buyer_data:
        buyer, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'buyer',
                'is_verified': True,
                'balance': Decimal(str(random.randint(10000, 100000)))
            }
        )
        if created:
            buyer.set_password('demo123')
            buyer.save()
            print(f"Created buyer: {buyer.email}")
        buyers.append(buyer)
    
    return admin, sellers, buyers

def create_news_data(admin):
    """Create demo news data"""
    print("Creating demo news data...")
    
    # Create news categories
    categories_data = [
        ('Technology', 'technology', 'Latest technology news and updates', '#007bff'),
        ('Development', 'development', 'Software development news', '#28a745'),
        ('Business', 'business', 'Business and entrepreneurship', '#ffc107'),
        ('Announcements', 'announcements', 'Platform announcements', '#dc3545'),
    ]
    
    categories = []
    for name, slug, description, color in categories_data:
        category, created = NewsCategory.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'description': description,
                'color': color,
                'is_active': True
            }
        )
        if created:
            print(f"Created news category: {name}")
        categories.append(category)
    
    # Create news articles
    articles_data = [
        {
            'title': 'Welcome to Cooplink Platform',
            'slug': 'welcome-to-cooplink-platform',
            'excerpt': 'Discover the new marketplace for developers to buy and sell projects.',
            'content': '''# Welcome to Cooplink!

We are excited to announce the launch of Cooplink, a revolutionary marketplace for developers.

## Features:
- Buy and sell programming projects
- Secure payment processing
- Community-driven platform
- Multi-language support

Join us today and start exploring amazing projects!''',
            'category': categories[3],
            'status': 'published',
            'is_featured': True,
            'is_pinned': True,
            'priority': 'high',
            'tags': 'announcement, welcome, platform',
        },
        {
            'title': 'Top 10 Web Development Trends in 2024',
            'slug': 'top-10-web-development-trends-2024',
            'excerpt': 'Explore the latest trends shaping web development this year.',
            'content': '''# Web Development Trends 2024

Here are the top trends every developer should know:

## 1. AI Integration
Artificial Intelligence is becoming integral to web development...

## 2. Progressive Web Apps
PWAs continue to gain popularity...

## 3. Serverless Architecture
The rise of serverless computing...''',
            'category': categories[0],
            'status': 'published',
            'is_featured': True,
            'priority': 'normal',
            'tags': 'web development, trends, 2024, technology',
        },
        {
            'title': 'How to Price Your Programming Projects',
            'slug': 'how-to-price-programming-projects',
            'excerpt': 'A comprehensive guide to pricing your development work.',
            'content': '''# Pricing Your Programming Projects

Pricing can be challenging for developers. Here's a comprehensive guide:

## Factors to Consider:
1. Complexity of the project
2. Time investment
3. Market demand
4. Your experience level

## Pricing Strategies:
- Hourly rates
- Fixed project pricing
- Value-based pricing''',
            'category': categories[2],
            'status': 'published',
            'priority': 'normal',
            'tags': 'pricing, business, freelancing, guide',
        },
    ]
    
    for article_data in articles_data:
        article, created = NewsArticle.objects.get_or_create(
            slug=article_data['slug'],
            defaults={
                **article_data,
                'author': admin,
                'published_at': datetime.now() - timedelta(days=random.randint(1, 30)),
                'views_count': random.randint(50, 1000),
                'likes_count': random.randint(5, 100),
            }
        )
        if created:
            print(f"Created news article: {article_data['title']}")

def create_payment_methods():
    """Create payment methods"""
    print("Creating payment methods...")
    
    methods_data = [
        ('UzCard', 'uzcard', True, '0.0250', '1000.00', '10000000.00'),
        ('Humo', 'humo', True, '0.0250', '1000.00', '10000000.00'),
        ('Visa', 'visa', True, '0.0300', '5000.00', '50000000.00'),
        ('MasterCard', 'mastercard', True, '0.0300', '5000.00', '50000000.00'),
        ('MirPay', 'mirpay', True, '0.0200', '1000.00', '25000000.00'),
        ('Click', 'click', True, '0.0150', '1000.00', '15000000.00'),
        ('Payme', 'payme', True, '0.0150', '1000.00', '15000000.00'),
    ]
    
    for name, method_type, is_active, commission, min_amount, max_amount in methods_data:
        method, created = PaymentMethod.objects.get_or_create(
            name=name,
            defaults={
                'method_type': method_type,
                'is_active': is_active,
                'commission_rate': Decimal(commission),
                'min_amount': Decimal(min_amount),
                'max_amount': Decimal(max_amount),
                'description': f'{name} payment method'
            }
        )
        if created:
            print(f"Created payment method: {name}")

def create_projects_data(sellers):
    """Create demo projects"""
    print("Creating demo projects...")
    
    projects_data = [
        {
            'title': 'E-Commerce Website with Django',
            'description': '''# Complete E-Commerce Solution

A full-featured e-commerce website built with Django and React.

## Features:
- User authentication and profiles
- Product catalog with search and filtering
- Shopping cart and checkout process
- Payment integration
- Order management
- Admin dashboard
- Responsive design

## Technologies Used:
- Backend: Django, Django REST Framework
- Frontend: React, Redux, Material-UI
- Database: PostgreSQL
- Payment: Stripe integration
- Deployment: Docker, AWS

## What's Included:
- Complete source code
- Database schema and migrations
- API documentation
- Setup instructions
- Demo data fixtures''',
            'project_type': 'web_app',
            'languages': 'Python, JavaScript, HTML, CSS',
            'frameworks': 'Django, React, Redux, Material-UI',
            'price_uzs': Decimal('1500000.00'),
        },
        {
            'title': 'Task Management Mobile App',
            'description': '''# Task Management Mobile App

A cross-platform mobile application for task and project management.

## Features:
- Create and manage tasks
- Project organization
- Team collaboration
- Real-time notifications
- File attachments
- Time tracking
- Progress reports
- Offline synchronization

## Technologies:
- Framework: React Native
- State Management: Redux Toolkit
- Navigation: React Navigation
- Backend: Node.js, Express
- Database: MongoDB
- Authentication: JWT
- Push Notifications: Firebase

## Deliverables:
- Complete mobile app source code
- Backend API with documentation
- Setup and deployment guide
- Design assets and mockups''',
            'project_type': 'mobile_app',
            'languages': 'JavaScript, TypeScript',
            'frameworks': 'React Native, Node.js, Express, MongoDB',
            'price_uzs': Decimal('2000000.00'),
        },
        {
            'title': 'Cryptocurrency Portfolio Tracker',
            'description': '''# Crypto Portfolio Tracker

A desktop application to track cryptocurrency investments and portfolio performance.

## Features:
- Real-time price tracking
- Portfolio management
- Profit/loss calculations
- Historical charts and graphs
- Price alerts and notifications
- Multiple exchange support
- Tax reporting tools
- Dark/light theme

## Technologies:
- Framework: Electron
- Frontend: Vue.js, Chart.js
- State: Vuex
- API Integration: CoinGecko, Binance
- Database: SQLite
- Charts: Chart.js, ApexCharts

## Package Includes:
- Full desktop application
- Source code with comments
- API integration examples
- User manual and documentation
- Installation packages for Windows/Mac/Linux''',
            'project_type': 'desktop_app',
            'languages': 'JavaScript, HTML, CSS',
            'frameworks': 'Electron, Vue.js, Chart.js',
            'price_uzs': Decimal('1200000.00'),
        },
        {
            'title': 'Social Media Analytics API',
            'description': '''# Social Media Analytics REST API

A comprehensive API for social media analytics and reporting.

## API Features:
- Multi-platform data aggregation
- Real-time analytics
- Custom reporting endpoints
- User engagement metrics
- Content performance analysis
- Hashtag and mention tracking
- Sentiment analysis
- Rate limiting and authentication

## Technical Stack:
- Framework: FastAPI (Python)
- Database: PostgreSQL + Redis
- Authentication: OAuth 2.0 + JWT
- Documentation: OpenAPI/Swagger
- Testing: Pytest
- Deployment: Docker + Kubernetes

## What You Get:
- Complete API source code
- Database schema and migrations
- Comprehensive API documentation
- Unit and integration tests
- Docker configuration
- Postman collection for testing''',
            'project_type': 'api',
            'languages': 'Python',
            'frameworks': 'FastAPI, PostgreSQL, Redis',
            'price_uzs': Decimal('1800000.00'),
        },
        {
            'title': 'Automated Web Scraper Suite',
            'description': '''# Advanced Web Scraping Suite

A collection of web scrapers for various e-commerce and data collection needs.

## Scrapers Included:
- E-commerce product scraper
- Social media content scraper
- News and blog post collector
- Real estate data scraper
- Job listings aggregator
- Price monitoring tools

## Features:
- Rotating proxies and user agents
- CAPTCHA solving integration
- Data export to multiple formats
- Scheduling and automation
- Error handling and retry logic
- Database storage options
- Web dashboard for management

## Technology Stack:
- Python with Scrapy framework
- Selenium for dynamic content
- BeautifulSoup for HTML parsing
- Requests for API calls
- SQLite/PostgreSQL for storage
- Celery for task scheduling

## Deliverables:
- Complete scraper suite
- Configuration examples
- Deployment scripts
- Usage documentation
- Legal compliance guide''',
            'project_type': 'script',
            'languages': 'Python',
            'frameworks': 'Scrapy, Selenium, BeautifulSoup',
            'price_uzs': Decimal('900000.00'),
        },
    ]
    
    for i, project_data in enumerate(projects_data):
        seller = sellers[i % len(sellers)]
        
        project, created = Project.objects.get_or_create(
            title=project_data['title'],
            defaults={
                **project_data,
                'seller': seller,
                'is_approved': True,
                'is_active': True,
                'downloads': random.randint(10, 200),
                'rating': Decimal(str(round(random.uniform(3.5, 5.0), 2))),
                'reviews_count': random.randint(5, 50),
            }
        )
        if created:
            print(f"Created project: {project_data['title']}")

def create_transactions_data(buyers, sellers):
    """Create demo transactions"""
    print("Creating demo transactions...")
    
    payment_methods = list(PaymentMethod.objects.all())
    
    for _ in range(20):
        buyer = random.choice(buyers)
        amount = Decimal(str(random.randint(50000, 2000000)))
        commission = amount * Decimal('0.03')
        
        transaction = Transaction.objects.create(
            user=buyer,
            transaction_type=random.choice(['purchase', 'deposit', 'refund']),
            status=random.choice(['completed', 'pending', 'failed']),
            amount=amount,
            commission_amount=commission,
            net_amount=amount - commission,
            payment_method=random.choice(payment_methods),
            description=f"Demo transaction for {buyer.username}",
            created_at=datetime.now() - timedelta(days=random.randint(1, 90))
        )
        print(f"Created transaction: {transaction.id}")

def main():
    """Main function to create all demo data"""
    print("Starting demo data creation...")
    print("=" * 50)
    
    try:
        # Create users
        admin, sellers, buyers = create_users()
        
        # Create news data
        create_news_data(admin)
        
        # Create payment methods
        create_payment_methods()
        
        # Create projects
        create_projects_data(sellers)
        
        # Create transactions
        create_transactions_data(buyers, sellers)
        
        print("=" * 50)
        print("Demo data creation completed successfully!")
        print("\nLogin credentials:")
        print("Admin: admin@cooplink.uz / admin123")
        print("Sellers: john.doe@example.com / demo123")
        print("Buyers: buyer1@example.com / demo123")
        
    except Exception as e:
        print(f"Error creating demo data: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
