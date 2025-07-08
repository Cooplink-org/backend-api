from rest_framework import serializers
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


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ('id', 'user', 'action', 'metadata', 'created_at')


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = ('id', 'path', 'country', 'device_type', 'browser', 'created_at')


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = ('id', 'query', 'results_count', 'created_at')


class RevenueAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueAnalytics
        fields = ('period', 'date', 'total_revenue', 'commission_revenue', 
                 'transactions_count', 'avg_transaction_value')


class UserMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMetrics
        fields = ('period', 'date', 'new_users', 'active_users', 'retention_rate')


class ProjectMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMetrics
        fields = ('period', 'date', 'new_projects', 'approved_projects', 
                 'total_downloads', 'avg_rating')


class TelegramMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramMetrics
        fields = ('period', 'date', 'bot_starts', 'auth_attempts', 
                 'successful_auths', 'active_telegram_users')


class SystemMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetrics
        fields = ('timestamp', 'cpu_usage', 'memory_usage', 'active_connections')


class CustomEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomEvent
        fields = ('id', 'name', 'event_type', 'properties', 'value', 'created_at')
