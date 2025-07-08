from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from datetime import timedelta

from .models import (
    AdminAction, SystemConfiguration, MaintenanceMode, AdminNotification,
    BackupRecord, SystemHealth, AdminDashboardWidget, BulkAction, AdminSession
)
from apps.accounts.models import User
from apps.projects.models import Project, Purchase, Review, ProjectReport
from apps.payments.models import Transaction
from apps.news.models import NewsArticle


User = get_user_model()


class AdminActionSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    target_user_username = serializers.CharField(source='target_user.username', read_only=True)
    
    class Meta:
        model = AdminAction
        fields = [
            'id', 'admin', 'admin_username', 'action_type', 'target_user', 
            'target_user_username', 'description', 'reason', 'object_type', 
            'object_id', 'metadata', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'admin', 'created_at']


class SystemConfigurationSerializer(serializers.ModelSerializer):
    last_modified_by_username = serializers.CharField(source='last_modified_by.username', read_only=True)
    
    class Meta:
        model = SystemConfiguration
        fields = [
            'name', 'config_type', 'value', 'default_value', 'description',
            'is_active', 'is_sensitive', 'validation_rules', 'last_modified_by',
            'last_modified_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Hide sensitive values for non-superusers
        request = self.context.get('request')
        if instance.is_sensitive and request and not request.user.is_superuser:
            data['value'] = '***HIDDEN***'
        return data


class MaintenanceModeSerializer(serializers.ModelSerializer):
    activated_by_username = serializers.CharField(source='activated_by.username', read_only=True)
    deactivated_by_username = serializers.CharField(source='deactivated_by.username', read_only=True)
    
    class Meta:
        model = MaintenanceMode
        fields = [
            'is_active', 'title', 'message', 'estimated_completion', 'allowed_ips',
            'activated_by', 'activated_by_username', 'deactivated_by', 
            'deactivated_by_username', 'activated_at', 'deactivated_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['activated_by', 'deactivated_by', 'activated_at', 'deactivated_at']


class AdminNotificationSerializer(serializers.ModelSerializer):
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    time_since = serializers.SerializerMethodField()
    
    class Meta:
        model = AdminNotification
        fields = [
            'id', 'title', 'message', 'notification_type', 'priority',
            'recipient', 'recipient_username', 'is_global', 'is_read', 'is_dismissed',
            'action_url', 'action_text', 'metadata', 'time_since',
            'read_at', 'dismissed_at', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_time_since(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"


class BackupRecordSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    duration_formatted = serializers.SerializerMethodField()
    size_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupRecord
        fields = [
            'id', 'backup_type', 'status', 'file_path', 'file_size_mb',
            'backup_duration_seconds', 'duration_formatted', 'size_formatted',
            'created_by', 'created_by_username', 'is_automated', 'error_message',
            'notes', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_duration_formatted(self, obj):
        if obj.backup_duration_seconds:
            minutes, seconds = divmod(obj.backup_duration_seconds, 60)
            return f"{minutes}m {seconds}s"
        return None
    
    def get_size_formatted(self, obj):
        if obj.file_size_mb:
            if obj.file_size_mb >= 1024:
                return f"{obj.file_size_mb / 1024:.1f} GB"
            return f"{obj.file_size_mb} MB"
        return None


class SystemHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemHealth
        fields = [
            'timestamp', 'overall_status', 'cpu_usage', 'memory_usage', 
            'disk_usage', 'database_connections', 'database_size_mb',
            'slow_queries', 'active_users', 'response_time_avg', 'error_rate',
            'payment_gateway_status', 'telegram_bot_status', 'email_service_status',
            'issues'
        ]
        read_only_fields = ['timestamp']


class AdminDashboardWidgetSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    
    class Meta:
        model = AdminDashboardWidget
        fields = [
            'admin', 'admin_username', 'widget_type', 'title', 'position_x',
            'position_y', 'width', 'height', 'configuration', 'is_visible',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['admin', 'created_at', 'updated_at']


class BulkActionSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BulkAction
        fields = [
            'id', 'admin', 'admin_username', 'action_type', 'status',
            'total_items', 'processed_items', 'successful_items', 'failed_items',
            'progress_percentage', 'filters_applied', 'action_parameters',
            'started_at', 'completed_at', 'error_log', 'created_at'
        ]
        read_only_fields = ['id', 'admin', 'created_at']
    
    def get_progress_percentage(self, obj):
        if obj.total_items > 0:
            return round((obj.processed_items / obj.total_items) * 100, 1)
        return 0


class AdminSessionSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    duration = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = AdminSession
        fields = [
            'admin', 'admin_username', 'session_key', 'ip_address', 'user_agent',
            'country', 'city', 'is_suspicious', 'security_score', 'last_activity',
            'pages_visited', 'actions_performed', 'duration', 'is_active',
            'created_at', 'ended_at'
        ]
        read_only_fields = ['admin', 'session_key', 'created_at']
    
    def get_duration(self, obj):
        end_time = obj.ended_at or timezone.now()
        duration = end_time - obj.created_at
        return str(duration)
    
    def get_is_active(self, obj):
        if obj.ended_at:
            return False
        # Consider active if last activity was within 30 minutes
        return (timezone.now() - obj.last_activity).total_seconds() < 1800


# Enhanced User Management Serializers
class UserDetailSerializer(serializers.ModelSerializer):
    projects_count = serializers.SerializerMethodField()
    purchases_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    total_earned = serializers.SerializerMethodField()
    last_login_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'github_id', 'github_username', 'balance', 'is_verified', 'is_active',
            'is_staff', 'is_superuser', 'projects_count', 'purchases_count',
            'total_spent', 'total_earned', 'last_login', 'last_login_formatted',
            'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at']
    
    def get_projects_count(self, obj):
        return obj.projects.count()
    
    def get_purchases_count(self, obj):
        return obj.purchases.count()
    
    def get_total_spent(self, obj):
        return obj.purchases.filter(status='completed').aggregate(
            total=models.Sum('amount_uzs')
        )['total'] or 0
    
    def get_total_earned(self, obj):
        # Calculate from project sales
        return Transaction.objects.filter(
            transaction_type='project_sale',
            recipient=obj,
            status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    def get_last_login_formatted(self, obj):
        if obj.last_login:
            now = timezone.now()
            diff = now - obj.last_login
            if diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600} hours ago"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60} minutes ago"
            else:
                return "Just now"
        return "Never"


class ProjectDetailSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    purchases_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'seller', 'seller_username', 'title', 'description', 'image',
            'demo_link', 'project_type', 'languages', 'frameworks', 'price_uzs',
            'downloads', 'rating', 'reviews_count', 'purchases_count', 'total_revenue',
            'avg_rating', 'is_approved', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'downloads', 'rating', 'reviews_count', 'created_at', 'updated_at']
    
    def get_purchases_count(self, obj):
        return obj.purchases.filter(status='completed').count()
    
    def get_total_revenue(self, obj):
        return obj.purchases.filter(status='completed').aggregate(
            total=models.Sum('amount_uzs')
        )['total'] or 0
    
    def get_avg_rating(self, obj):
        return obj.reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0


class TransactionDetailSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_username', 'transaction_type', 'status', 'amount',
            'currency', 'commission_amount', 'net_amount', 'payment_method',
            'payment_method_name', 'external_transaction_id', 'gateway_response',
            'purchase', 'withdrawal', 'description', 'failure_reason',
            'ip_address', 'user_agent', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectReportDetailSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='purchase.buyer.username', read_only=True)
    seller_username = serializers.CharField(source='purchase.project.seller.username', read_only=True)
    project_title = serializers.CharField(source='purchase.project.title', read_only=True)
    
    class Meta:
        model = ProjectReport
        fields = [
            'purchase', 'buyer_username', 'seller_username', 'project_title',
            'reason', 'admin_notes', 'status', 'created_at', 'resolved_at'
        ]
        read_only_fields = ['purchase', 'created_at']


# Bulk Action Request Serializers
class BulkUserActionSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    action = serializers.ChoiceField(choices=[
        'ban', 'unban', 'verify', 'unverify', 'activate', 'deactivate'
    ])
    reason = serializers.CharField(max_length=500, required=False)


class BulkProjectActionSerializer(serializers.Serializer):
    project_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False
    )
    action = serializers.ChoiceField(choices=[
        'approve', 'reject', 'activate', 'deactivate'
    ])
    reason = serializers.CharField(max_length=500, required=False)


class SystemStatsSerializer(serializers.Serializer):
    # User Statistics
    total_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    new_users_week = serializers.IntegerField()
    new_users_month = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    
    # Project Statistics
    total_projects = serializers.IntegerField()
    approved_projects = serializers.IntegerField()
    pending_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    
    # Transaction Statistics
    total_transactions = serializers.IntegerField()
    completed_transactions = serializers.IntegerField()
    pending_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    
    # Revenue Statistics
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    revenue_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    revenue_week = serializers.DecimalField(max_digits=12, decimal_places=2)
    revenue_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # System Health
    system_status = serializers.CharField()
    last_backup = serializers.DateTimeField()
    disk_usage = serializers.DecimalField(max_digits=5, decimal_places=2)
    memory_usage = serializers.DecimalField(max_digits=5, decimal_places=2)
