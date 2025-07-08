from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from decimal import Decimal
import uuid


class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('register', 'User Registration'),
        ('profile_update', 'Profile Update'),
        ('project_view', 'Project View'),
        ('project_purchase', 'Project Purchase'),
        ('project_upload', 'Project Upload'),
        ('search', 'Search Query'),
        ('download', 'File Download'),
        ('review_submit', 'Review Submission'),
        ('news_view', 'News Article View'),
        ('news_like', 'News Article Like'),
        ('telegram_auth', 'Telegram Authentication'),
        ('payment_initiated', 'Payment Initiated'),
        ('payment_completed', 'Payment Completed'),
        ('dispute_opened', 'Dispute Opened'),
        ('report_submitted', 'Report Submitted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    metadata = models.JSONField(default=dict, blank=True)  # Additional data
    referrer = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_user_activity'
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        ordering = ['-created_at']


class PageView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=500)
    query_params = models.TextField(blank=True)
    referrer = models.URLField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    browser = models.CharField(max_length=100, null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_page_view'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['path', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['country', 'created_at']),
            models.Index(fields=['device_type', 'created_at']),
        ]


class SearchQuery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    clicked_result_id = models.UUIDField(null=True, blank=True)
    click_position = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_search_query'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['query']),
            models.Index(fields=['created_at']),
            models.Index(fields=['results_count']),
        ]


class RevenueAnalytics(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    date = models.DateField()
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    commission_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    seller_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    transactions_count = models.PositiveIntegerField(default=0)
    avg_transaction_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    refunds_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    refunds_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_revenue'
        unique_together = ['period', 'date']
        indexes = [
            models.Index(fields=['period', 'date']),
            models.Index(fields=['date']),
        ]


class UserMetrics(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    date = models.DateField()
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    new_sellers = models.PositiveIntegerField(default=0)
    active_sellers = models.PositiveIntegerField(default=0)
    new_buyers = models.PositiveIntegerField(default=0)
    active_buyers = models.PositiveIntegerField(default=0)
    telegram_linked_users = models.PositiveIntegerField(default=0)
    verified_users = models.PositiveIntegerField(default=0)
    retention_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    churn_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_user_metrics'
        unique_together = ['period', 'date']
        indexes = [
            models.Index(fields=['period', 'date']),
            models.Index(fields=['date']),
        ]


class ProjectMetrics(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    date = models.DateField()
    new_projects = models.PositiveIntegerField(default=0)
    approved_projects = models.PositiveIntegerField(default=0)
    rejected_projects = models.PositiveIntegerField(default=0)
    total_downloads = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    reviews_count = models.PositiveIntegerField(default=0)
    reports_count = models.PositiveIntegerField(default=0)
    
    # By project type
    web_app_count = models.PositiveIntegerField(default=0)
    mobile_app_count = models.PositiveIntegerField(default=0)
    desktop_app_count = models.PositiveIntegerField(default=0)
    script_count = models.PositiveIntegerField(default=0)
    library_count = models.PositiveIntegerField(default=0)
    api_count = models.PositiveIntegerField(default=0)
    bot_count = models.PositiveIntegerField(default=0)
    game_count = models.PositiveIntegerField(default=0)
    other_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_project_metrics'
        unique_together = ['period', 'date']
        indexes = [
            models.Index(fields=['period', 'date']),
            models.Index(fields=['date']),
        ]


class TelegramMetrics(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    date = models.DateField()
    bot_starts = models.PositiveIntegerField(default=0)
    auth_attempts = models.PositiveIntegerField(default=0)
    successful_auths = models.PositiveIntegerField(default=0)
    failed_auths = models.PositiveIntegerField(default=0)
    account_links = models.PositiveIntegerField(default=0)
    commands_used = models.PositiveIntegerField(default=0)
    active_telegram_users = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_telegram_metrics'
        unique_together = ['period', 'date']
        indexes = [
            models.Index(fields=['period', 'date']),
            models.Index(fields=['date']),
        ]


class SystemMetrics(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    memory_usage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    disk_usage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    active_connections = models.PositiveIntegerField(null=True, blank=True)
    database_size_mb = models.PositiveIntegerField(null=True, blank=True)
    media_size_mb = models.PositiveIntegerField(null=True, blank=True)
    response_time_avg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    error_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'analytics_system_metrics'
        indexes = [
            models.Index(fields=['timestamp']),
        ]


class CustomEvent(models.Model):
    EVENT_TYPES = [
        ('business', 'Business Event'),
        ('technical', 'Technical Event'),
        ('user', 'User Event'),
        ('system', 'System Event'),
        ('marketing', 'Marketing Event'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    properties = models.JSONField(default=dict, blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_custom_event'
        indexes = [
            models.Index(fields=['name', 'created_at']),
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]
