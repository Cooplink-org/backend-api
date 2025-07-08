from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse
import logging
import json

from apps.accounts.models import User
from apps.projects.models import Project, Purchase
from apps.payments.models import Transaction
from apps.analytics.models import RevenueAnalytics, UserMetrics
from .models import (
    AdminAction, SystemConfiguration, MaintenanceMode, AdminNotification, 
    BackupRecord, SystemHealth, AdminDashboardWidget, BulkAction, AdminSession
)
from .serializers import (
    AdminActionSerializer, SystemConfigurationSerializer, MaintenanceModeSerializer, 
    AdminNotificationSerializer, BackupRecordSerializer, SystemHealthSerializer, 
    AdminDashboardWidgetSerializer, BulkActionSerializer, AdminSessionSerializer
)
from .permissions import (
    IsAdminOrSuperUser, IsSuperUserOnly, CanManageUsers, CanManageProjects,
    CanAccessSystemHealth, CanManageBackups, CanViewAnalytics, 
    CanManageSystemConfiguration, CanManageMaintenanceMode, CanExportData
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def dashboard_stats(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    stats = {
        'users': {
            'total': User.objects.count(),
            'new_this_week': User.objects.filter(created_at__gte=week_ago).count(),
            'new_this_month': User.objects.filter(created_at__gte=month_ago).count(),
            'sellers': User.objects.filter(role='seller').count(),
            'buyers': User.objects.filter(role='buyer').count(),
        },
        'projects': {
            'total': Project.objects.count(),
            'approved': Project.objects.filter(is_approved=True).count(),
            'pending': Project.objects.filter(is_approved=False).count(),
            'this_week': Project.objects.filter(created_at__gte=week_ago).count(),
            'this_month': Project.objects.filter(created_at__gte=month_ago).count(),
        },
        'sales': {
            'total_transactions': Transaction.objects.filter(status='completed').count(),
            'total_revenue': Transaction.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'this_week': Transaction.objects.filter(
                status='completed',
                created_at__gte=week_ago
            ).count(),
            'this_month': Transaction.objects.filter(
                status='completed',
                created_at__gte=month_ago
            ).count(),
        }
    }

    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def recent_activities(request):
    limit = request.GET.get('limit', 20)
    
    recent_users = User.objects.order_by('-created_at')[:int(limit)]
    recent_projects = Project.objects.order_by('-created_at')[:int(limit)]
    recent_transactions = Transaction.objects.order_by('-created_at')[:int(limit)]

    activities = {
        'recent_users': [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at
            } for user in recent_users
        ],
        'recent_projects': [
            {
                'id': project.id,
                'title': project.title,
                'seller': project.seller.username,
                'price_uzs': float(project.price_uzs),
                'is_approved': project.is_approved,
                'created_at': project.created_at
            } for project in recent_projects
        ],
        'recent_transactions': [
            {
                'id': transaction.id,
                'user': transaction.user.username,
                'type': transaction.transaction_type,
                'amount': float(transaction.amount),
                'status': transaction.status,
                'created_at': transaction.created_at
            } for transaction in recent_transactions
        ]
    }

    return Response(activities)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def health_status(request):
    health_records = SystemHealth.objects.order_by('-timestamp')[:10]
    status_list = [
        {
            'timestamp': record.timestamp,
            'overall_status': record.overall_status,
            'cpu_usage': record.cpu_usage,
            'memory_usage': record.memory_usage,
            'disk_usage': record.disk_usage,
            'database_connections': record.database_connections,
            'error_rate': record.error_rate,
        } for record in health_records
    ]
    return Response(status_list)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications(request):
    notifications_query = AdminNotification.objects.filter(
        Q(recipient=request.user) | Q(is_global=True),
        is_read=False
    ).order_by('-created_at')[:10]

    notifications_list = [
        {
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority,
            'notification_type': notification.notification_type
        } for notification in notifications_query
    ]
    return JsonResponse({'notifications': notifications_list})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def backup_status(request):
    backup_records = BackupRecord.objects.order_by('-created_at')[:5]
    records = [
        {
            'backup_type': record.backup_type,
            'status': record.status,
            'file_size_mb': record.file_size_mb,
            'created_at': record.created_at,
            'is_automated': record.is_automated,
        } for record in backup_records
    ]
    return Response(records)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def analytics_dashboard(request):
    """📊 Comprehensive analytics dashboard with emojis 🎯"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    
    # 👥 User Analytics
    user_stats = {
        'total_users': User.objects.count(),
        'new_users_today': User.objects.filter(created_at__date=today).count(),
        'new_users_week': User.objects.filter(created_at__date__gte=week_ago).count(),
        'new_users_month': User.objects.filter(created_at__date__gte=month_ago).count(),
        'verified_users': User.objects.filter(is_verified=True).count(),
        'sellers': User.objects.filter(role='seller').count(),
        'buyers': User.objects.filter(role='buyer').count(),
        'user_growth_rate': calculate_growth_rate(User, 'created_at', month_ago),
    }
    
    # 📁 Project Analytics
    project_stats = {
        'total_projects': Project.objects.count(),
        'approved_projects': Project.objects.filter(is_approved=True).count(),
        'pending_projects': Project.objects.filter(is_approved=False, is_active=True).count(),
        'projects_today': Project.objects.filter(created_at__date=today).count(),
        'projects_week': Project.objects.filter(created_at__date__gte=week_ago).count(),
        'approval_rate': calculate_approval_rate(),
        'avg_project_price': Project.objects.aggregate(avg_price=Avg('price_uzs'))['avg_price'] or 0,
    }
    
    # 💰 Revenue Analytics
    revenue_stats = {
        'total_revenue': Transaction.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0,
        'revenue_today': Transaction.objects.filter(status='completed', created_at__date=today).aggregate(total=Sum('amount'))['total'] or 0,
        'revenue_week': Transaction.objects.filter(status='completed', created_at__date__gte=week_ago).aggregate(total=Sum('amount'))['total'] or 0,
        'revenue_month': Transaction.objects.filter(status='completed', created_at__date__gte=month_ago).aggregate(total=Sum('amount'))['total'] or 0,
        'avg_transaction_value': Transaction.objects.filter(status='completed').aggregate(avg=Avg('amount'))['avg'] or 0,
        'revenue_growth': calculate_revenue_growth(month_ago),
    }
    
    # 📈 Transaction Analytics
    transaction_stats = {
        'total_transactions': Transaction.objects.count(),
        'completed_transactions': Transaction.objects.filter(status='completed').count(),
        'pending_transactions': Transaction.objects.filter(status='pending').count(),
        'failed_transactions': Transaction.objects.filter(status='failed').count(),
        'success_rate': calculate_transaction_success_rate(),
        'transactions_today': Transaction.objects.filter(created_at__date=today).count(),
    }
    
    # 📊 Charts Data
    charts_data = {
        'user_registration_chart': generate_user_registration_chart(30),
        'revenue_trend_chart': generate_revenue_trend_chart(30),
        'project_types_chart': generate_project_categories_chart(),
        'transaction_status_chart': generate_transaction_status_chart(),
        'monthly_growth_chart': generate_monthly_growth_chart(12),
    }
    
    # 🚨 System Alerts
    alerts = {
        'pending_approvals': Project.objects.filter(is_approved=False, is_active=True).count(),
        'failed_transactions': Transaction.objects.filter(status='failed').count(),
        'unverified_sellers': User.objects.filter(role='seller', is_verified=False).count(),
        'low_disk_space': check_disk_space(),
        'system_errors': get_recent_system_errors(),
    }
    
    # 🎯 Performance Metrics
    performance = {
        'response_time_avg': get_avg_response_time(),
        'uptime_percentage': get_uptime_percentage(),
        'active_sessions': get_active_sessions_count(),
        'api_calls_today': get_api_calls_count(today),
    }
    
    return Response({
        '📊 Dashboard': 'Cooplink Analytics Dashboard',
        '👥 users': user_stats,
        '📁 projects': project_stats,
        '💰 revenue': revenue_stats,
        '📈 transactions': transaction_stats,
        '📊 charts': charts_data,
        '🚨 alerts': alerts,
        '🎯 performance': performance,
        'last_updated': timezone.now(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_management(request):
    """👥 Enhanced user management with detailed analytics"""
    users = User.objects.all().order_by('-created_at')
    
    # Apply filters if provided
    role = request.GET.get('role')
    verified = request.GET.get('verified')
    active = request.GET.get('active')
    
    if role:
        users = users.filter(role=role)
    if verified is not None:
        users = users.filter(is_verified=verified.lower() == 'true')
    if active is not None:
        users = users.filter(is_active=active.lower() == 'true')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    users_data = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_verified': user.is_verified,
            'is_active': user.is_active,
            'created_at': user.created_at,
            'last_login': user.last_login,
            'projects_count': user.projects.count() if hasattr(user, 'projects') else 0,
            'transactions_count': user.transactions.count() if hasattr(user, 'transactions') else 0,
        } for user in users[start:end]
    ]
    
    return Response({
        '👥 users': users_data,
        'pagination': {
            'current_page': page,
            'page_size': page_size,
            'total_users': users.count(),
            'total_pages': (users.count() + page_size - 1) // page_size,
        },
        'summary': {
            'total_in_filter': users.count(),
            'verified_in_filter': users.filter(is_verified=True).count(),
            'active_in_filter': users.filter(is_active=True).count(),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def project_management(request):
    """📁 Enhanced project management with analytics"""
    projects = Project.objects.all().order_by('-created_at')
    
    # Apply filters
    approved = request.GET.get('approved')
    active = request.GET.get('active')
    project_type = request.GET.get('project_type')
    
    if approved is not None:
        projects = projects.filter(is_approved=approved.lower() == 'true')
    if active is not None:
        projects = projects.filter(is_active=active.lower() == 'true')
    if project_type:
        projects = projects.filter(project_type=project_type)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    projects_data = [
        {
            'id': project.id,
            'title': project.title,
            'seller': project.seller.username,
            'project_type': project.project_type,
            'price_uzs': float(project.price_uzs),
            'is_approved': project.is_approved,
            'is_active': project.is_active,
            'created_at': project.created_at,
            'purchase_count': project.purchases.count() if hasattr(project, 'purchases') else 0,
        } for project in projects[start:end]
    ]
    
    return Response({
        '📁 projects': projects_data,
        'pagination': {
            'current_page': page,
            'page_size': page_size,
            'total_projects': projects.count(),
            'total_pages': (projects.count() + page_size - 1) // page_size,
        },
        'summary': {
            'total_in_filter': projects.count(),
            'approved_in_filter': projects.filter(is_approved=True).count(),
            'active_in_filter': projects.filter(is_active=True).count(),
        }
    })


# 🔧 Helper Functions
def calculate_growth_rate(model, date_field, start_date):
    """Calculate growth rate over a period"""
    try:
        current_count = model.objects.filter(**{f'{date_field}__gte': start_date}).count()
        previous_period_start = start_date - (timezone.now().date() - start_date)
        previous_count = model.objects.filter(
            **{f'{date_field}__gte': previous_period_start},
            **{f'{date_field}__lt': start_date}
        ).count()
        
        if previous_count == 0:
            return 100 if current_count > 0 else 0
        
        return ((current_count - previous_count) / previous_count) * 100
    except:
        return 0

def calculate_approval_rate():
    """Calculate project approval rate"""
    total_projects = Project.objects.count()
    if total_projects == 0:
        return 0
    approved_projects = Project.objects.filter(is_approved=True).count()
    return (approved_projects / total_projects) * 100

def calculate_revenue_growth(start_date):
    """Calculate revenue growth"""
    try:
        current_revenue = Transaction.objects.filter(
            status='completed',
            created_at__date__gte=start_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        period_length = (timezone.now().date() - start_date).days
        previous_start = start_date - timedelta(days=period_length)
        
        previous_revenue = Transaction.objects.filter(
            status='completed',
            created_at__date__gte=previous_start,
            created_at__date__lt=start_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        if previous_revenue == 0:
            return 100 if current_revenue > 0 else 0
        
        return ((current_revenue - previous_revenue) / previous_revenue) * 100
    except:
        return 0

def calculate_transaction_success_rate():
    """Calculate transaction success rate"""
    total = Transaction.objects.count()
    if total == 0:
        return 0
    completed = Transaction.objects.filter(status='completed').count()
    return (completed / total) * 100

def generate_user_registration_chart(days):
    """Generate user registration chart data"""
    data = []
    today = timezone.now().date()
    
    for i in range(days):
        date = today - timedelta(days=i)
        count = User.objects.filter(created_at__date=date).count()
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count,
            'day_name': date.strftime('%A')
        })
    
    return list(reversed(data))

def generate_revenue_trend_chart(days):
    """Generate revenue trend chart data"""
    data = []
    today = timezone.now().date()
    
    for i in range(days):
        date = today - timedelta(days=i)
        revenue = Transaction.objects.filter(
            status='completed',
            created_at__date=date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(revenue),
            'day_name': date.strftime('%A')
        })
    
    return list(reversed(data))

def generate_project_categories_chart():
    """Generate project types distribution"""
    project_types = Project.objects.values('project_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return list(project_types)

def generate_transaction_status_chart():
    """Generate transaction status distribution"""
    statuses = Transaction.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return list(statuses)

def generate_monthly_growth_chart(months):
    """Generate monthly growth chart"""
    data = []
    today = timezone.now().date()
    
    for i in range(months):
        # Calculate start of month
        month_date = today.replace(day=1) - timedelta(days=i*30)
        month_start = month_date.replace(day=1)
        
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
        
        users = User.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        projects = Project.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        revenue = Transaction.objects.filter(
            status='completed',
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        data.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%B %Y'),
            'users': users,
            'projects': projects,
            'revenue': float(revenue)
        })
    
    return list(reversed(data))

# 🔧 System Helper Functions
def check_disk_space():
    """Check if disk space is low"""
    # This would integrate with actual system monitoring
    return False

def get_recent_system_errors():
    """Get recent system errors count"""
    # This would integrate with logging system
    return 0

def get_avg_response_time():
    """Get average response time"""
    # This would integrate with performance monitoring
    return 0.15

def get_uptime_percentage():
    """Get system uptime percentage"""
    # This would integrate with uptime monitoring
    return 99.9

def get_active_sessions_count():
    """Get active sessions count"""
    # This would integrate with session tracking
    return 0

def get_api_calls_count(date):
    """Get API calls count for a specific date"""
    # This would integrate with API analytics
    return 0


# API ViewSets for Admin Panel Models
class AdminActionViewSet(viewsets.ModelViewSet):
    """Admin actions performed by administrators"""
    queryset = AdminAction.objects.all().order_by('-created_at')
    serializer_class = AdminActionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    
    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)
        
    @action(detail=False, methods=['get'])
    def my_actions(self, request):
        """Get current admin's actions"""
        queryset = self.queryset.filter(admin=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SystemConfigurationViewSet(viewsets.ModelViewSet):
    """System configuration management"""
    queryset = SystemConfiguration.objects.all()
    serializer_class = SystemConfigurationSerializer
    permission_classes = [IsAuthenticated, CanManageSystemConfiguration]
    
    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)
        
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get configurations by type"""
        config_type = request.query_params.get('type')
        if config_type:
            queryset = self.queryset.filter(config_type=config_type)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'error': 'Type parameter required'}, status=400)


class MaintenanceModeViewSet(viewsets.ModelViewSet):
    """Maintenance mode management"""
    queryset = MaintenanceMode.objects.all()
    serializer_class = MaintenanceModeSerializer
    permission_classes = [IsAuthenticated, CanManageMaintenanceMode]
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate maintenance mode"""
        maintenance = self.get_object()
        maintenance.is_active = True
        maintenance.activated_by = request.user
        maintenance.activated_at = timezone.now()
        maintenance.save()
        
        AdminAction.objects.create(
            admin=request.user,
            action_type='maintenance_mode',
            description=f'Activated maintenance mode: {maintenance.title}'
        )
        
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate maintenance mode"""
        maintenance = self.get_object()
        maintenance.is_active = False
        maintenance.deactivated_by = request.user
        maintenance.deactivated_at = timezone.now()
        maintenance.save()
        
        AdminAction.objects.create(
            admin=request.user,
            action_type='maintenance_mode',
            description=f'Deactivated maintenance mode: {maintenance.title}'
        )
        
        return Response({'status': 'deactivated'})


class AdminNotificationViewSet(viewsets.ModelViewSet):
    """Admin notifications management"""
    queryset = AdminNotification.objects.all().order_by('-created_at')
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter notifications for current user"""
        return self.queryset.filter(
            Q(recipient=self.request.user) | Q(is_global=True)
        )
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'status': 'read'})
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss notification"""
        notification = self.get_object()
        notification.is_dismissed = True
        notification.dismissed_at = timezone.now()
        notification.save()
        return Response({'status': 'dismissed'})
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        queryset = self.get_queryset().filter(is_read=False, is_dismissed=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BackupRecordViewSet(viewsets.ModelViewSet):
    """Backup records management"""
    queryset = BackupRecord.objects.all().order_by('-created_at')
    serializer_class = BackupRecordSerializer
    permission_classes = [IsAuthenticated, CanManageBackups]
    
    @action(detail=False, methods=['post'])
    def create_backup(self, request):
        """Create a new backup"""
        backup_type = request.data.get('backup_type', 'database')
        
        backup = BackupRecord.objects.create(
            backup_type=backup_type,
            created_by=request.user,
            status='running'
        )
        
        AdminAction.objects.create(
            admin=request.user,
            action_type='backup_create',
            description=f'Started {backup_type} backup',
            object_type='BackupRecord',
            object_id=str(backup.id)
        )
        
        # Here you would trigger the actual backup process
        # For now, we'll just return the backup object
        serializer = self.get_serializer(backup)
        return Response(serializer.data, status=201)


class SystemHealthViewSet(viewsets.ModelViewSet):
    """System health monitoring"""
    queryset = SystemHealth.objects.all().order_by('-timestamp')
    serializer_class = SystemHealthSerializer
    permission_classes = [IsAuthenticated, CanAccessSystemHealth]
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest health status"""
        latest_health = self.queryset.first()
        if latest_health:
            serializer = self.get_serializer(latest_health)
            return Response(serializer.data)
        return Response({'error': 'No health data available'}, status=404)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get health summary"""
        latest = self.queryset.first()
        if not latest:
            return Response({'error': 'No health data available'}, status=404)
            
        return Response({
            'overall_status': latest.overall_status,
            'cpu_usage': latest.cpu_usage,
            'memory_usage': latest.memory_usage,
            'disk_usage': latest.disk_usage,
            'last_updated': latest.timestamp,
            'issues': latest.issues
        })


class AdminDashboardWidgetViewSet(viewsets.ModelViewSet):
    """Admin dashboard widgets"""
    queryset = AdminDashboardWidget.objects.all()
    serializer_class = AdminDashboardWidgetSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    
    def get_queryset(self):
        """Filter widgets for current admin"""
        return self.queryset.filter(admin=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)


class BulkActionViewSet(viewsets.ModelViewSet):
    """Bulk actions management"""
    queryset = BulkAction.objects.all().order_by('-created_at')
    serializer_class = BulkActionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    
    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active bulk actions"""
        queryset = self.queryset.filter(status__in=['queued', 'running'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminSessionViewSet(viewsets.ModelViewSet):
    """Admin session management"""
    queryset = AdminSession.objects.all().order_by('-last_activity')
    serializer_class = AdminSessionSerializer
    permission_classes = [IsAuthenticated, IsSuperUserOnly]
    
    @action(detail=False, methods=['get'])
    def active_sessions(self, request):
        """Get active admin sessions"""
        threshold = timezone.now() - timedelta(minutes=30)
        queryset = self.queryset.filter(
            last_activity__gte=threshold,
            ended_at__isnull=True
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate an admin session"""
        session = self.get_object()
        session.ended_at = timezone.now()
        session.save()
        
        AdminAction.objects.create(
            admin=request.user,
            action_type='session_terminate',
            description=f'Terminated session for {session.admin.username}',
            object_type='AdminSession',
            object_id=str(session.id)
        )
        
        return Response({'status': 'terminated'})


# User Management API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated, CanManageUsers])
def bulk_user_action(request):
    """Perform bulk actions on users"""
    action = request.data.get('action')
    user_ids = request.data.get('user_ids', [])
    reason = request.data.get('reason', '')
    
    if not action or not user_ids:
        return Response({'error': 'Action and user_ids are required'}, status=400)
    
    users = User.objects.filter(id__in=user_ids)
    if not users.exists():
        return Response({'error': 'No valid users found'}, status=404)
    
    updated_count = 0
    errors = []
    
    for user in users:
        try:
            if action == 'ban':
                user.is_active = False
                user.save()
                updated_count += 1
            elif action == 'unban':
                user.is_active = True
                user.save()
                updated_count += 1
            elif action == 'verify':
                user.is_verified = True
                user.save()
                updated_count += 1
            elif action == 'unverify':
                user.is_verified = False
                user.save()
                updated_count += 1
            else:
                errors.append(f'Unknown action: {action}')
        except Exception as e:
            errors.append(f'Error processing user {user.id}: {str(e)}')
    
    # Log the bulk action
    AdminAction.objects.create(
        admin=request.user,
        action_type=f'user_bulk_{action}',
        description=f'Bulk {action} applied to {updated_count} users',
        reason=reason
    )
    
    return Response({
        'success': True,
        'updated_count': updated_count,
        'total_requested': len(user_ids),
        'errors': errors
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanManageProjects])
def bulk_project_action(request):
    """Perform bulk actions on projects"""
    action = request.data.get('action')
    project_ids = request.data.get('project_ids', [])
    reason = request.data.get('reason', '')
    
    if not action or not project_ids:
        return Response({'error': 'Action and project_ids are required'}, status=400)
    
    projects = Project.objects.filter(id__in=project_ids)
    if not projects.exists():
        return Response({'error': 'No valid projects found'}, status=404)
    
    updated_count = 0
    errors = []
    
    for project in projects:
        try:
            if action == 'approve':
                project.is_approved = True
                project.save()
                updated_count += 1
            elif action == 'reject':
                project.is_approved = False
                project.save()
                updated_count += 1
            elif action == 'activate':
                project.is_active = True
                project.save()
                updated_count += 1
            elif action == 'deactivate':
                project.is_active = False
                project.save()
                updated_count += 1
            else:
                errors.append(f'Unknown action: {action}')
        except Exception as e:
            errors.append(f'Error processing project {project.id}: {str(e)}')
    
    # Log the bulk action
    AdminAction.objects.create(
        admin=request.user,
        action_type=f'project_bulk_{action}',
        description=f'Bulk {action} applied to {updated_count} projects',
        reason=reason
    )
    
    return Response({
        'success': True,
        'updated_count': updated_count,
        'total_requested': len(project_ids),
        'errors': errors
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanManageUsers])
def user_details(request, user_id):
    """Get detailed user information"""
    try:
        user = User.objects.get(id=user_id)
        
        # Get user statistics
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_verified': user.is_verified,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'balance': float(user.balance),
            'created_at': user.created_at,
            'last_login': user.last_login,
            
            # Statistics
            'projects_count': user.projects.count() if hasattr(user, 'projects') else 0,
            'purchases_count': user.purchases.count() if hasattr(user, 'purchases') else 0,
            'total_spent': float(user.purchases.filter(status='completed').aggregate(
                total=Sum('amount_uzs'))['total'] or 0),
            'total_earned': float(Transaction.objects.filter(
                transaction_type='project_sale',
                recipient=user,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0),
            
            # Recent activities
            'recent_projects': list(user.projects.order_by('-created_at')[:5].values(
                'id', 'title', 'price_uzs', 'is_approved', 'created_at'
            )) if hasattr(user, 'projects') else [],
            'recent_purchases': list(user.purchases.order_by('-created_at')[:5].values(
                'id', 'project__title', 'amount_uzs', 'status', 'created_at'
            )) if hasattr(user, 'purchases') else [],
        }
        
        return Response(user_data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanManageProjects])
def project_details(request, project_id):
    """Get detailed project information"""
    try:
        project = Project.objects.get(id=project_id)
        
        project_data = {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'seller': {
                'id': project.seller.id,
                'username': project.seller.username,
                'email': project.seller.email
            },
            'project_type': project.project_type,
            'languages': project.languages,
            'frameworks': project.frameworks,
            'price_uzs': float(project.price_uzs),
            'downloads': project.downloads,
            'rating': float(project.rating),
            'reviews_count': project.reviews_count,
            'is_approved': project.is_approved,
            'is_active': project.is_active,
            'created_at': project.created_at,
            'updated_at': project.updated_at,
            
            # Statistics
            'total_revenue': float(project.purchases.filter(status='completed').aggregate(
                total=Sum('amount_uzs'))['total'] or 0),
            'purchase_count': project.purchases.filter(status='completed').count(),
            
            # Recent activities
            'recent_purchases': list(project.purchases.order_by('-created_at')[:10].values(
                'id', 'buyer__username', 'amount_uzs', 'status', 'created_at'
            )),
            'recent_reviews': list(project.reviews.order_by('-created_at')[:5].values(
                'id', 'buyer__username', 'rating', 'comment', 'created_at'
            )),
        }
        
        return Response(project_data)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanExportData])
def export_data(request):
    """Export system data"""
    export_type = request.data.get('export_type')
    date_from = request.data.get('date_from')
    date_to = request.data.get('date_to')
    
    if not export_type:
        return Response({'error': 'Export type is required'}, status=400)
    
    try:
        from django.core import serializers
        import io
        
        # Create export record
        bulk_action = BulkAction.objects.create(
            admin=request.user,
            action_type='data_bulk_export',
            status='running',
            total_items=0,
            filters_applied={
                'export_type': export_type,
                'date_from': date_from,
                'date_to': date_to
            }
        )
        
        # Log the action
        AdminAction.objects.create(
            admin=request.user,
            action_type='data_export',
            description=f'Started {export_type} data export',
            object_type='BulkAction',
            object_id=str(bulk_action.id)
        )
        
        return Response({
            'export_id': bulk_action.id,
            'status': 'Export started',
            'message': 'Export process initiated. You will be notified when complete.'
        })
        
    except Exception as e:
        return Response({'error': f'Export failed: {str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewAnalytics])
def system_overview(request):
    """Get comprehensive system overview"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    overview = {
        'timestamp': timezone.now(),
        'users': {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'verified': User.objects.filter(is_verified=True).count(),
            'new_this_week': User.objects.filter(created_at__date__gte=week_ago).count(),
            'sellers': User.objects.filter(role='seller').count(),
            'buyers': User.objects.filter(role='buyer').count(),
        },
        'projects': {
            'total': Project.objects.count(),
            'approved': Project.objects.filter(is_approved=True).count(),
            'pending': Project.objects.filter(is_approved=False, is_active=True).count(),
            'active': Project.objects.filter(is_active=True).count(),
            'new_this_week': Project.objects.filter(created_at__date__gte=week_ago).count(),
        },
        'transactions': {
            'total': Transaction.objects.count(),
            'completed': Transaction.objects.filter(status='completed').count(),
            'pending': Transaction.objects.filter(status='pending').count(),
            'failed': Transaction.objects.filter(status='failed').count(),
            'total_revenue': float(Transaction.objects.filter(status='completed').aggregate(
                total=Sum('amount'))['total'] or 0),
            'revenue_this_week': float(Transaction.objects.filter(
                status='completed', created_at__date__gte=week_ago
            ).aggregate(total=Sum('amount'))['total'] or 0),
        },
        'system': {
            'maintenance_mode': MaintenanceMode.objects.filter(is_active=True).exists(),
            'pending_admin_actions': AdminAction.objects.filter(
                created_at__date=today
            ).count(),
            'unread_notifications': AdminNotification.objects.filter(
                is_read=False
            ).count(),
            'recent_backups': BackupRecord.objects.filter(
                created_at__date__gte=week_ago
            ).count(),
        }
    }
    
    return Response(overview)
