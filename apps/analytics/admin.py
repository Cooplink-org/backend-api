from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Avg
from django.contrib import admin
from .models import (
    UserActivity,
    PageView,
    SearchQuery,
    RevenueAnalytics,
    UserMetrics,
    ProjectMetrics,
    TelegramMetrics,
    SystemMetrics,
    CustomEvent
)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'action',
        'content_type',
        'ip_address',
        'created_at'
    )
    list_filter = (
        'action',
        'content_type',
        'created_at'
    )
    search_fields = (
        'user__username',
        'user__email',
        'action',
        'ip_address',
        'session_id'
    )
    readonly_fields = (
        'id',
        'created_at'
    )
    
    fieldsets = (
        ('Activity Information', {
            'fields': (
                'id',
                'user',
                'session_id',
                'action',
                'ip_address',
                'user_agent'
            )
        }),
        ('Related Object', {
            'fields': (
                'content_type',
                'object_id',
                'content_object'
            )
        }),
        ('Additional Data', {
            'fields': (
                'metadata',
                'referrer'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'path',
        'country',
        'device_type',
        'browser',
        'response_time_ms',
        'created_at'
    )
    list_filter = (
        'country',
        'device_type',
        'browser',
        'os',
        'created_at'
    )
    search_fields = (
        'user__username',
        'path',
        'ip_address',
        'session_id'
    )
    readonly_fields = (
        'id',
        'created_at'
    )
    
    fieldsets = (
        ('Page Information', {
            'fields': (
                'id',
                'user',
                'session_id',
                'path',
                'query_params',
                'referrer'
            )
        }),
        ('User Environment', {
            'fields': (
                'ip_address',
                'user_agent',
                'country',
                'city',
                'browser',
                'device_type',
                'os'
            )
        }),
        ('Performance', {
            'fields': (
                'response_time_ms',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'query',
        'results_count',
        'click_position',
        'created_at'
    )
    list_filter = (
        'results_count',
        'created_at'
    )
    search_fields = (
        'user__username',
        'query',
        'session_id'
    )
    readonly_fields = (
        'id',
        'created_at'
    )
    
    fieldsets = (
        ('Search Information', {
            'fields': (
                'id',
                'user',
                'session_id',
                'query',
                'filters',
                'results_count'
            )
        }),
        ('Click Data', {
            'fields': (
                'clicked_result_id',
                'click_position'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        }),
    )


@admin.register(RevenueAnalytics)
class RevenueAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        'period',
        'date',
        'total_revenue_formatted',
        'commission_revenue_formatted',
        'transactions_count',
        'avg_transaction_value_formatted'
    )
    list_filter = (
        'period',
        'date'
    )
    search_fields = ('period',)
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Period Information', {
            'fields': (
                'period',
                'date'
            )
        }),
        ('Revenue Metrics', {
            'fields': (
                'total_revenue',
                'commission_revenue',
                'seller_earnings',
                'refunds_amount'
            )
        }),
        ('Transaction Metrics', {
            'fields': (
                'transactions_count',
                'avg_transaction_value',
                'refunds_count'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def total_revenue_formatted(self, obj):
        return f"{obj.total_revenue:,.0f} UZS"
    total_revenue_formatted.short_description = 'Total Revenue'
    total_revenue_formatted.admin_order_field = 'total_revenue'
    
    def commission_revenue_formatted(self, obj):
        return f"{obj.commission_revenue:,.0f} UZS"
    commission_revenue_formatted.short_description = 'Commission'
    commission_revenue_formatted.admin_order_field = 'commission_revenue'
    
    def avg_transaction_value_formatted(self, obj):
        return f"{obj.avg_transaction_value:,.0f} UZS"
    avg_transaction_value_formatted.short_description = 'Avg Transaction'
    avg_transaction_value_formatted.admin_order_field = 'avg_transaction_value'


@admin.register(UserMetrics)
class UserMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'period',
        'date',
        'new_users',
        'active_users',
        'new_sellers',
        'retention_rate_formatted',
        'churn_rate_formatted'
    )
    list_filter = (
        'period',
        'date'
    )
    search_fields = ('period',)
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Period Information', {
            'fields': (
                'period',
                'date'
            )
        }),
        ('User Counts', {
            'fields': (
                'new_users',
                'active_users',
                'new_sellers',
                'active_sellers',
                'new_buyers',
                'active_buyers'
            )
        }),
        ('User Status', {
            'fields': (
                'telegram_linked_users',
                'verified_users'
            )
        }),
        ('Engagement Metrics', {
            'fields': (
                'retention_rate',
                'churn_rate'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def retention_rate_formatted(self, obj):
        return f"{obj.retention_rate:.1f}%"
    retention_rate_formatted.short_description = 'Retention Rate'
    retention_rate_formatted.admin_order_field = 'retention_rate'
    
    def churn_rate_formatted(self, obj):
        return f"{obj.churn_rate:.1f}%"
    churn_rate_formatted.short_description = 'Churn Rate'
    churn_rate_formatted.admin_order_field = 'churn_rate'


@admin.register(ProjectMetrics)
class ProjectMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'period',
        'date',
        'new_projects',
        'approved_projects',
        'total_downloads',
        'avg_rating_formatted',
        'reviews_count'
    )
    list_filter = (
        'period',
        'date'
    )
    search_fields = ('period',)
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Period Information', {
            'fields': (
                'period',
                'date'
            )
        }),
        ('Project Counts', {
            'fields': (
                'new_projects',
                'approved_projects',
                'rejected_projects'
            )
        }),
        ('Engagement Metrics', {
            'fields': (
                'total_downloads',
                'total_views',
                'avg_rating',
                'reviews_count',
                'reports_count'
            )
        }),
        ('Project Types', {
            'fields': (
                'web_app_count',
                'mobile_app_count',
                'desktop_app_count',
                'script_count',
                'library_count',
                'api_count',
                'bot_count',
                'game_count',
                'other_count'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def avg_rating_formatted(self, obj):
        return f"{obj.avg_rating:.1f}/5.0"
    avg_rating_formatted.short_description = 'Avg Rating'
    avg_rating_formatted.admin_order_field = 'avg_rating'


@admin.register(TelegramMetrics)
class TelegramMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'period',
        'date',
        'bot_starts',
        'auth_attempts',
        'successful_auths',
        'success_rate_formatted',
        'active_telegram_users'
    )
    list_filter = (
        'period',
        'date'
    )
    search_fields = ('period',)
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Period Information', {
            'fields': (
                'period',
                'date'
            )
        }),
        ('Bot Activity', {
            'fields': (
                'bot_starts',
                'commands_used',
                'active_telegram_users'
            )
        }),
        ('Authentication', {
            'fields': (
                'auth_attempts',
                'successful_auths',
                'failed_auths',
                'account_links'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def success_rate_formatted(self, obj):
        if obj.auth_attempts > 0:
            rate = (obj.successful_auths / obj.auth_attempts) * 100
            return f"{rate:.1f}%"
        return "N/A"
    success_rate_formatted.short_description = 'Success Rate'


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'cpu_usage_formatted',
        'memory_usage_formatted',
        'disk_usage_formatted',
        'active_connections',
        'error_rate_formatted'
    )
    list_filter = (
        'timestamp',
    )
    readonly_fields = (
        'timestamp',
    )
    
    fieldsets = (
        ('System Resources', {
            'fields': (
                'timestamp',
                'cpu_usage',
                'memory_usage',
                'disk_usage'
            )
        }),
        ('Database Metrics', {
            'fields': (
                'database_size_mb',
            )
        }),
        ('Application Metrics', {
            'fields': (
                'active_connections',
                'response_time_avg',
                'error_rate'
            )
        }),
        ('Storage', {
            'fields': (
                'media_size_mb',
            )
        }),
    )
    
    def cpu_usage_formatted(self, obj):
        if obj.cpu_usage is not None:
            return f"{obj.cpu_usage:.1f}%"
        return "N/A"
    cpu_usage_formatted.short_description = 'CPU Usage'
    cpu_usage_formatted.admin_order_field = 'cpu_usage'
    
    def memory_usage_formatted(self, obj):
        if obj.memory_usage is not None:
            return f"{obj.memory_usage:.1f}%"
        return "N/A"
    memory_usage_formatted.short_description = 'Memory Usage'
    memory_usage_formatted.admin_order_field = 'memory_usage'
    
    def disk_usage_formatted(self, obj):
        if obj.disk_usage is not None:
            return f"{obj.disk_usage:.1f}%"
        return "N/A"
    disk_usage_formatted.short_description = 'Disk Usage'
    disk_usage_formatted.admin_order_field = 'disk_usage'
    
    def error_rate_formatted(self, obj):
        if obj.error_rate is not None:
            return f"{obj.error_rate:.2f}%"
        return "N/A"
    error_rate_formatted.short_description = 'Error Rate'
    error_rate_formatted.admin_order_field = 'error_rate'


@admin.register(CustomEvent)
class CustomEventAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'event_type',
        'user',
        'value_formatted',
        'session_id',
        'created_at'
    )
    list_filter = (
        'event_type',
        'name',
        'created_at'
    )
    search_fields = (
        'name',
        'user__username',
        'session_id'
    )
    readonly_fields = (
        'id',
        'created_at'
    )
    
    fieldsets = (
        ('Event Information', {
            'fields': (
                'id',
                'name',
                'event_type',
                'user',
                'session_id'
            )
        }),
        ('Event Data', {
            'fields': (
                'properties',
                'value'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        }),
    )
    
    def value_formatted(self, obj):
        if obj.value is not None:
            return f"{obj.value:,.2f}"
        return "N/A"
    value_formatted.short_description = 'Value'
    value_formatted.admin_order_field = 'value'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
