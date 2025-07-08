from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Avg
# Admin models are registered in their respective apps
from .models import (
    AdminAction,
    SystemConfiguration,
    MaintenanceMode,
    AdminNotification,
    BackupRecord,
    SystemHealth,
    AdminDashboardWidget,
    BulkAction,
    AdminSession
)


@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = (
        'admin',
        'action_type',
        'target_user',
        'object_type',
        'short_description',
        'created_at'
    )
    list_filter = (
        'action_type',
        'object_type',
        'created_at'
    )
    search_fields = (
        'admin__username',
        'target_user__username',
        'description',
        'reason',
        'object_type',
        'object_id'
    )
    readonly_fields = (
        'id',
        'created_at'
    )
    
    fieldsets = (
        ('Action Information', {
            'fields': (
                'id',
                'admin',
                'action_type',
                'target_user',
                'description',
                'reason'
            )
        }),
        ('Target Object', {
            'fields': (
                'object_type',
                'object_id'
            )
        }),
        ('Technical Data', {
            'fields': (
                'metadata',
                'ip_address',
                'user_agent'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        }),
    )
    
    def short_description(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    short_description.short_description = 'Description'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('admin', 'target_user')


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'config_type',
        'value_preview',
        'is_active',
        'is_sensitive',
        'last_modified_by',
        'updated_at'
    )
    list_filter = (
        'config_type',
        'is_active',
        'is_sensitive',
        'updated_at'
    )
    search_fields = (
        'name',
        'description'
    )
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Configuration Information', {
            'fields': (
                'name',
                'config_type',
                'description',
                'is_active',
                'is_sensitive'
            )
        }),
        ('Values', {
            'fields': (
                'value',
                'default_value'
            )
        }),
        ('Validation', {
            'fields': (
                'validation_rules',
            ),
            'classes': ('collapse',)
        }),
        ('Modification Info', {
            'fields': (
                'last_modified_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def value_preview(self, obj):
        if obj.is_sensitive:
            return '***HIDDEN***'
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value
    value_preview.short_description = 'Value'
    
    def save_model(self, request, obj, form, change):
        obj.last_modified_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display = (
        'is_active',
        'title',
        'estimated_completion',
        'activated_by',
        'activated_at',
        'created_at'
    )
    list_filter = (
        'is_active',
        'activated_at',
        'deactivated_at',
        'created_at'
    )
    search_fields = (
        'title',
        'message',
        'allowed_ips'
    )
    readonly_fields = (
        'activated_at',
        'deactivated_at',
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Maintenance Information', {
            'fields': (
                'is_active',
                'title',
                'message',
                'estimated_completion'
            )
        }),
        ('Access Control', {
            'fields': (
                'allowed_ips',
            )
        }),
        ('Status Tracking', {
            'fields': (
                'activated_by',
                'deactivated_by',
                'activated_at',
                'deactivated_at'
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
    
    def save_model(self, request, obj, form, change):
        if obj.is_active and not obj.activated_at:
            obj.activated_by = request.user
            obj.activated_at = timezone.now()
        elif not obj.is_active and obj.activated_at and not obj.deactivated_at:
            obj.deactivated_by = request.user
            obj.deactivated_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'notification_type',
        'priority',
        'recipient',
        'is_global',
        'is_read',
        'is_dismissed',
        'created_at'
    )
    list_filter = (
        'notification_type',
        'priority',
        'is_global',
        'is_read',
        'is_dismissed',
        'created_at'
    )
    search_fields = (
        'title',
        'message',
        'recipient__username'
    )
    readonly_fields = (
        'id',
        'read_at',
        'dismissed_at',
        'created_at'
    )
    
    fieldsets = (
        ('Notification Information', {
            'fields': (
                'id',
                'title',
                'message',
                'notification_type',
                'priority'
            )
        }),
        ('Recipients', {
            'fields': (
                'recipient',
                'is_global'
            )
        }),
        ('Status', {
            'fields': (
                'is_read',
                'is_dismissed',
                'read_at',
                'dismissed_at',
                'expires_at'
            )
        }),
        ('Action', {
            'fields': (
                'action_url',
                'action_text'
            )
        }),
        ('Additional Data', {
            'fields': (
                'metadata',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_dismissed']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'
    
    def mark_as_dismissed(self, request, queryset):
        updated = queryset.update(is_dismissed=True, dismissed_at=timezone.now())
        self.message_user(request, f'{updated} notifications dismissed.')
    mark_as_dismissed.short_description = 'Dismiss selected notifications'


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = (
        'backup_type',
        'status',
        'file_size_formatted',
        'backup_duration_formatted',
        'created_by',
        'is_automated',
        'created_at'
    )
    list_filter = (
        'backup_type',
        'status',
        'is_automated',
        'created_at'
    )
    search_fields = (
        'file_path',
        'created_by__username',
        'notes'
    )
    readonly_fields = (
        'id',
        'backup_duration_seconds',
        'created_at',
        'completed_at'
    )
    
    fieldsets = (
        ('Backup Information', {
            'fields': (
                'id',
                'backup_type',
                'status',
                'created_by',
                'is_automated'
            )
        }),
        ('File Information', {
            'fields': (
                'file_path',
                'file_size_mb',
                'backup_duration_seconds'
            )
        }),
        ('Notes & Errors', {
            'fields': (
                'notes',
                'error_message'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'completed_at'
            )
        }),
    )
    
    def file_size_formatted(self, obj):
        if obj.file_size_mb:
            if obj.file_size_mb >= 1024:
                return f"{obj.file_size_mb / 1024:.1f} GB"
            return f"{obj.file_size_mb:.1f} MB"
        return "N/A"
    file_size_formatted.short_description = 'File Size'
    file_size_formatted.admin_order_field = 'file_size_mb'
    
    def backup_duration_formatted(self, obj):
        if obj.backup_duration_seconds:
            minutes = obj.backup_duration_seconds // 60
            seconds = obj.backup_duration_seconds % 60
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            return f"{seconds}s"
        return "N/A"
    backup_duration_formatted.short_description = 'Duration'
    backup_duration_formatted.admin_order_field = 'backup_duration_seconds'


@admin.register(SystemHealth)
class SystemHealthAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'overall_status',
        'cpu_usage_formatted',
        'memory_usage_formatted',
        'disk_usage_formatted',
        'response_time_formatted',
        'error_rate_formatted'
    )
    list_filter = (
        'overall_status',
        'payment_gateway_status',
        'telegram_bot_status',
        'email_service_status',
        'timestamp'
    )
    readonly_fields = (
        'timestamp',
    )
    
    fieldsets = (
        ('System Status', {
            'fields': (
                'timestamp',
                'overall_status',
                'issues'
            )
        }),
        ('System Resources', {
            'fields': (
                'cpu_usage',
                'memory_usage',
                'disk_usage'
            )
        }),
        ('Database Metrics', {
            'fields': (
                'database_connections',
                'database_size_mb',
                'slow_queries'
            )
        }),
        ('Application Metrics', {
            'fields': (
                'active_users',
                'response_time_avg',
                'error_rate'
            )
        }),
        ('External Services', {
            'fields': (
                'payment_gateway_status',
                'telegram_bot_status',
                'email_service_status'
            )
        }),
    )
    
    def cpu_usage_formatted(self, obj):
        if obj.cpu_usage is not None:
            return f"{obj.cpu_usage:.1f}%"
        return "N/A"
    cpu_usage_formatted.short_description = 'CPU'
    cpu_usage_formatted.admin_order_field = 'cpu_usage'
    
    def memory_usage_formatted(self, obj):
        if obj.memory_usage is not None:
            return f"{obj.memory_usage:.1f}%"
        return "N/A"
    memory_usage_formatted.short_description = 'Memory'
    memory_usage_formatted.admin_order_field = 'memory_usage'
    
    def disk_usage_formatted(self, obj):
        if obj.disk_usage is not None:
            return f"{obj.disk_usage:.1f}%"
        return "N/A"
    disk_usage_formatted.short_description = 'Disk'
    disk_usage_formatted.admin_order_field = 'disk_usage'
    
    def response_time_formatted(self, obj):
        if obj.response_time_avg is not None:
            return f"{obj.response_time_avg:.0f}ms"
        return "N/A"
    response_time_formatted.short_description = 'Response Time'
    response_time_formatted.admin_order_field = 'response_time_avg'
    
    def error_rate_formatted(self, obj):
        if obj.error_rate is not None:
            return f"{obj.error_rate:.2f}%"
        return "N/A"
    error_rate_formatted.short_description = 'Error Rate'
    error_rate_formatted.admin_order_field = 'error_rate'


@admin.register(AdminDashboardWidget)
class AdminDashboardWidgetAdmin(admin.ModelAdmin):
    list_display = (
        'admin',
        'widget_type',
        'title',
        'position_display',
        'size_display',
        'is_visible',
        'updated_at'
    )
    list_filter = (
        'widget_type',
        'is_visible',
        'updated_at'
    )
    search_fields = (
        'admin__username',
        'title'
    )
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Widget Information', {
            'fields': (
                'admin',
                'widget_type',
                'title',
                'is_visible'
            )
        }),
        ('Position & Size', {
            'fields': (
                'position_x',
                'position_y',
                'width',
                'height'
            )
        }),
        ('Configuration', {
            'fields': (
                'configuration',
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
    
    def position_display(self, obj):
        return f"({obj.position_x}, {obj.position_y})"
    position_display.short_description = 'Position (X, Y)'
    
    def size_display(self, obj):
        return f"{obj.width} × {obj.height}"
    size_display.short_description = 'Size (W × H)'


@admin.register(BulkAction)
class BulkActionAdmin(admin.ModelAdmin):
    list_display = (
        'admin',
        'action_type',
        'status',
        'progress_display',
        'total_items',
        'successful_items',
        'failed_items',
        'created_at'
    )
    list_filter = (
        'action_type',
        'status',
        'created_at'
    )
    search_fields = (
        'admin__username',
        'action_type'
    )
    readonly_fields = (
        'id',
        'processed_items',
        'successful_items',
        'failed_items',
        'started_at',
        'completed_at',
        'created_at'
    )
    
    fieldsets = (
        ('Action Information', {
            'fields': (
                'id',
                'admin',
                'action_type',
                'status'
            )
        }),
        ('Progress', {
            'fields': (
                'total_items',
                'processed_items',
                'successful_items',
                'failed_items'
            )
        }),
        ('Configuration', {
            'fields': (
                'filters_applied',
                'action_parameters'
            ),
            'classes': ('collapse',)
        }),
        ('Error Log', {
            'fields': (
                'error_log',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'started_at',
                'completed_at'
            )
        }),
    )
    
    def progress_display(self, obj):
        if obj.total_items > 0:
            percentage = (obj.processed_items / obj.total_items) * 100
            return f"{obj.processed_items}/{obj.total_items} ({percentage:.1f}%)"
        return f"{obj.processed_items}/{obj.total_items}"
    progress_display.short_description = 'Progress'


@admin.register(AdminSession)
class AdminSessionAdmin(admin.ModelAdmin):
    list_display = (
        'admin',
        'ip_address',
        'country',
        'city',
        'is_suspicious',
        'security_score',
        'pages_visited',
        'actions_performed',
        'last_activity'
    )
    list_filter = (
        'is_suspicious',
        'country',
        'last_activity',
        'created_at'
    )
    search_fields = (
        'admin__username',
        'ip_address',
        'session_key',
        'user_agent'
    )
    readonly_fields = (
        'session_key',
        'pages_visited',
        'actions_performed',
        'last_activity',
        'created_at',
        'ended_at'
    )
    
    fieldsets = (
        ('Session Information', {
            'fields': (
                'admin',
                'session_key',
                'ip_address',
                'user_agent'
            )
        }),
        ('Location', {
            'fields': (
                'country',
                'city'
            )
        }),
        ('Security', {
            'fields': (
                'is_suspicious',
                'security_score'
            )
        }),
        ('Activity Tracking', {
            'fields': (
                'pages_visited',
                'actions_performed',
                'last_activity'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'ended_at'
            )
        }),
    )
    
    actions = ['mark_suspicious', 'mark_safe']
    
    def mark_suspicious(self, request, queryset):
        updated = queryset.update(is_suspicious=True, security_score=25)
        self.message_user(request, f'{updated} sessions marked as suspicious.')
    mark_suspicious.short_description = 'Mark selected sessions as suspicious'
    
    def mark_safe(self, request, queryset):
        updated = queryset.update(is_suspicious=False, security_score=100)
        self.message_user(request, f'{updated} sessions marked as safe.')
    mark_safe.short_description = 'Mark selected sessions as safe'
