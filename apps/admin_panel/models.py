from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid


User = get_user_model()


class AdminAction(models.Model):
    ACTION_TYPES = [
        ('user_ban', 'User Ban'),
        ('user_unban', 'User Unban'),
        ('user_verify', 'User Verification'),
        ('project_approve', 'Project Approval'),
        ('project_reject', 'Project Rejection'),
        ('project_remove', 'Project Removal'),
        ('payment_refund', 'Payment Refund'),
        ('withdrawal_approve', 'Withdrawal Approval'),
        ('withdrawal_reject', 'Withdrawal Rejection'),
        ('dispute_resolve', 'Dispute Resolution'),
        ('news_publish', 'News Publication'),
        ('system_config', 'System Configuration'),
        ('bulk_action', 'Bulk Action'),
        ('data_export', 'Data Export'),
        ('backup_create', 'Backup Creation'),
        ('maintenance_mode', 'Maintenance Mode'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_actions_received')
    description = models.TextField()
    reason = models.TextField(blank=True)
    
    # Generic relation to affected objects
    object_type = models.CharField(max_length=50, blank=True)  # Model name
    object_id = models.CharField(max_length=255, blank=True)  # Object ID
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_panel_action'
        indexes = [
            models.Index(fields=['admin', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['target_user', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.admin.username} - {self.action_type} - {self.created_at}'


class SystemConfiguration(models.Model):
    CONFIG_TYPES = [
        ('general', 'General Settings'),
        ('payment', 'Payment Settings'),
        ('email', 'Email Settings'),
        ('telegram', 'Telegram Settings'),
        ('security', 'Security Settings'),
        ('performance', 'Performance Settings'),
        ('api', 'API Settings'),
        ('maintenance', 'Maintenance Settings'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPES)
    value = models.TextField()
    default_value = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_sensitive = models.BooleanField(default=False)  # Hide value in admin
    validation_rules = models.JSONField(default=dict, blank=True)
    
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_panel_system_config'
        ordering = ['config_type', 'name']
    
    def __str__(self):
        return f'{self.config_type}: {self.name}'


class MaintenanceMode(models.Model):
    is_active = models.BooleanField(default=False)
    title = models.CharField(max_length=200, default='Site Under Maintenance')
    message = models.TextField(default='We are currently performing maintenance. Please check back soon.')
    estimated_completion = models.DateTimeField(null=True, blank=True)
    allowed_ips = models.TextField(blank=True, help_text='Comma-separated IP addresses that can access during maintenance')
    
    activated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_activations')
    deactivated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_deactivations')
    
    activated_at = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_panel_maintenance_mode'
        ordering = ['-created_at']
    
    def __str__(self):
        status = 'Active' if self.is_active else 'Inactive'
        return f'Maintenance Mode - {status}'


class AdminNotification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    NOTIFICATION_TYPES = [
        ('system_alert', 'System Alert'),
        ('security_warning', 'Security Warning'),
        ('payment_issue', 'Payment Issue'),
        ('user_report', 'User Report'),
        ('performance_warning', 'Performance Warning'),
        ('backup_status', 'Backup Status'),
        ('update_available', 'Update Available'),
        ('error_report', 'Error Report'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Recipients
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Specific admin
    is_global = models.BooleanField(default=False)  # For all admins
    
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=50, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    read_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_panel_notification'
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
            models.Index(fields=['is_global', 'is_read', 'created_at']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.notification_type}: {self.title}'


class BackupRecord(models.Model):
    BACKUP_TYPES = [
        ('database', 'Database Backup'),
        ('media', 'Media Files Backup'),
        ('full', 'Full System Backup'),
        ('config', 'Configuration Backup'),
    ]
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('corrupted', 'Corrupted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    
    file_path = models.CharField(max_length=500, blank=True)
    file_size_mb = models.PositiveIntegerField(null=True, blank=True)
    backup_duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_automated = models.BooleanField(default=False)
    
    error_message = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'admin_panel_backup_record'
        indexes = [
            models.Index(fields=['backup_type', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_automated']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.backup_type} backup - {self.status} - {self.created_at}'


class SystemHealth(models.Model):
    """System health monitoring records"""
    HEALTH_STATUS = [
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('down', 'Down'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    overall_status = models.CharField(max_length=10, choices=HEALTH_STATUS)
    
    # System metrics
    cpu_usage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    memory_usage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    disk_usage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Database metrics
    database_connections = models.PositiveIntegerField(null=True, blank=True)
    database_size_mb = models.PositiveIntegerField(null=True, blank=True)
    slow_queries = models.PositiveIntegerField(null=True, blank=True)
    
    # Application metrics
    active_users = models.PositiveIntegerField(null=True, blank=True)
    response_time_avg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    error_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # External services
    payment_gateway_status = models.CharField(max_length=10, default='unknown')
    telegram_bot_status = models.CharField(max_length=10, default='unknown')
    email_service_status = models.CharField(max_length=10, default='unknown')
    
    issues = models.JSONField(default=list, blank=True)  # List of detected issues
    
    class Meta:
        db_table = 'admin_panel_system_health'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['overall_status', 'timestamp']),
        ]
        ordering = ['-timestamp']


class AdminDashboardWidget(models.Model):
    """Customizable dashboard widgets for admin users"""
    WIDGET_TYPES = [
        ('stats_card', 'Statistics Card'),
        ('chart', 'Chart'),
        ('table', 'Data Table'),
        ('alert_list', 'Alert List'),
        ('activity_feed', 'Activity Feed'),
        ('quick_actions', 'Quick Actions'),
    ]
    
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=100)
    
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=6)  # Grid columns
    height = models.PositiveIntegerField(default=4)  # Grid rows
    
    configuration = models.JSONField(default=dict)  # Widget-specific settings
    is_visible = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_panel_dashboard_widget'
        unique_together = ['admin', 'position_x', 'position_y']
        indexes = [
            models.Index(fields=['admin', 'is_visible']),
        ]
        ordering = ['position_y', 'position_x']


class BulkAction(models.Model):
    """Track bulk operations performed by admins"""
    ACTION_TYPES = [
        ('user_bulk_ban', 'Bulk User Ban'),
        ('user_bulk_verify', 'Bulk User Verification'),
        ('project_bulk_approve', 'Bulk Project Approval'),
        ('project_bulk_reject', 'Bulk Project Rejection'),
        ('payment_bulk_refund', 'Bulk Payment Refund'),
        ('data_bulk_export', 'Bulk Data Export'),
        ('email_bulk_send', 'Bulk Email Send'),
    ]
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partially_completed', 'Partially Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bulk_actions')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    
    total_items = models.PositiveIntegerField()
    processed_items = models.PositiveIntegerField(default=0)
    successful_items = models.PositiveIntegerField(default=0)
    failed_items = models.PositiveIntegerField(default=0)
    
    filters_applied = models.JSONField(default=dict)  # Criteria used for selection
    action_parameters = models.JSONField(default=dict)  # Action-specific parameters
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_log = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_panel_bulk_action'
        indexes = [
            models.Index(fields=['admin', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['action_type']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.action_type} by {self.admin.username} - {self.status}'


class AdminSession(models.Model):
    """Enhanced session tracking for admin users"""
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Location data (if available)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Security flags
    is_suspicious = models.BooleanField(default=False)
    security_score = models.PositiveIntegerField(default=100)  # 0-100
    
    # Activity tracking
    last_activity = models.DateTimeField(auto_now=True)
    pages_visited = models.PositiveIntegerField(default=0)
    actions_performed = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'admin_panel_session'
        indexes = [
            models.Index(fields=['admin', 'last_activity']),
            models.Index(fields=['session_key']),
            models.Index(fields=['is_suspicious']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-last_activity']
