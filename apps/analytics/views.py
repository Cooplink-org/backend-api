from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import structlog

from .models import (
    UserActivity, PageView, SearchQuery, RevenueAnalytics,
    UserMetrics, ProjectMetrics, TelegramMetrics, SystemMetrics, CustomEvent
)
from apps.accounts.models import User
from apps.projects.models import Project, Purchase
from apps.payments.models import Transaction

logger = structlog.get_logger(__name__)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_overview(request):
    """Get dashboard overview metrics"""
    try:
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User metrics
        total_users = User.objects.count()
        new_users_week = User.objects.filter(created_at__date__gte=week_ago).count()
        active_users_week = UserActivity.objects.filter(
            created_at__date__gte=week_ago
        ).values('user').distinct().count()
        
        # Project metrics
        total_projects = Project.objects.count()
        approved_projects = Project.objects.filter(is_approved=True).count()
        pending_projects = Project.objects.filter(is_approved=False, is_active=True).count()
        
        # Transaction metrics
        total_transactions = Transaction.objects.count()
        completed_transactions = Transaction.objects.filter(status='completed').count()
        monthly_revenue = Transaction.objects.filter(
            status='completed',
            created_at__date__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Activity metrics
        page_views_today = PageView.objects.filter(created_at__date=today).count()
        searches_today = SearchQuery.objects.filter(created_at__date=today).count()
        
        data = {
            'users': {
                'total': total_users,
                'new_week': new_users_week,
                'active_week': active_users_week,
                'growth_rate': (new_users_week / total_users * 100) if total_users > 0 else 0
            },
            'projects': {
                'total': total_projects,
                'approved': approved_projects,
                'pending': pending_projects,
                'approval_rate': (approved_projects / total_projects * 100) if total_projects > 0 else 0
            },
            'transactions': {
                'total': total_transactions,
                'completed': completed_transactions,
                'monthly_revenue': float(monthly_revenue),
                'success_rate': (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0
            },
            'activity': {
                'page_views_today': page_views_today,
                'searches_today': searches_today
            }
        }
        
        return Response(data)
        
    except Exception as e:
        logger.error("Dashboard overview error", error=str(e))
        return Response(
            {'error': 'Failed to fetch dashboard data'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_analytics(request):
    """Get user analytics data"""
    period = request.GET.get('period', 'weekly')
    
    try:
        if period == 'daily':
            days = 30
            date_field = 'created_at__date'
        elif period == 'weekly':
            days = 12 * 7  # 12 weeks
            date_field = 'created_at__week'
        else:  # monthly
            days = 12 * 30  # 12 months
            date_field = 'created_at__month'
        
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Get user registration data
        user_data = User.objects.filter(
            created_at__date__gte=start_date
        ).extra({
            'date': f"date({date_field})"
        }).values('date').annotate(count=Count('id')).order_by('date')
        
        # Get user activity data
        activity_data = UserActivity.objects.filter(
            created_at__date__gte=start_date
        ).extra({
            'date': f"date({date_field})"
        }).values('date').annotate(count=Count('user', distinct=True)).order_by('date')
        
        return Response({
            'registrations': list(user_data),
            'active_users': list(activity_data)
        })
        
    except Exception as e:
        logger.error("User analytics error", error=str(e))
        return Response(
            {'error': 'Failed to fetch user analytics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def revenue_analytics(request):
    """Get revenue analytics data"""
    period = request.GET.get('period', 'monthly')
    
    try:
        if period == 'daily':
            days = 30
        elif period == 'weekly':
            days = 12 * 7
        else:  # monthly
            days = 12 * 30
        
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Get revenue data
        revenue_data = Transaction.objects.filter(
            status='completed',
            created_at__date__gte=start_date
        ).extra({
            'date': f"date(created_at)"
        }).values('date').annotate(
            revenue=Sum('amount'),
            count=Count('id')
        ).order_by('date')
        
        # Get commission data
        commission_data = Transaction.objects.filter(
            status='completed',
            created_at__date__gte=start_date
        ).extra({
            'date': f"date(created_at)"
        }).values('date').annotate(
            commission=Sum('commission_amount')
        ).order_by('date')
        
        return Response({
            'revenue': list(revenue_data),
            'commission': list(commission_data)
        })
        
    except Exception as e:
        logger.error("Revenue analytics error", error=str(e))
        return Response(
            {'error': 'Failed to fetch revenue analytics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_user_activity(request):
    """Track user activity"""
    try:
        action = request.data.get('action')
        if not action:
            return Response(
                {'error': 'Action is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get client info
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        session_id = request.session.session_key
        
        # Create activity record
        UserActivity.objects.create(
            user=request.user,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action=action,
            metadata=request.data.get('metadata', {}),
            referrer=request.META.get('HTTP_REFERER', '')
        )
        
        return Response({'message': 'Activity tracked'})
        
    except Exception as e:
        logger.error("Activity tracking error", error=str(e))
        return Response(
            {'error': 'Failed to track activity'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_page_view(request):
    """Track page view"""
    try:
        path = request.data.get('path')
        if not path:
            return Response(
                {'error': 'Path is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get client info
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        session_id = request.session.session_key
        
        # Create page view record
        PageView.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            path=path,
            query_params=request.data.get('query_params', ''),
            referrer=request.META.get('HTTP_REFERER', ''),
            response_time_ms=request.data.get('response_time_ms')
        )
        
        return Response({'message': 'Page view tracked'})
        
    except Exception as e:
        logger.error("Page view tracking error", error=str(e))
        return Response(
            {'error': 'Failed to track page view'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_search_query(request):
    """Track search query"""
    try:
        query = request.data.get('query')
        if not query:
            return Response(
                {'error': 'Query is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session_id = request.session.session_key
        
        # Create search query record
        SearchQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=session_id,
            query=query,
            filters=request.data.get('filters', {}),
            results_count=request.data.get('results_count', 0),
            clicked_result_id=request.data.get('clicked_result_id'),
            click_position=request.data.get('click_position')
        )
        
        return Response({'message': 'Search query tracked'})
        
    except Exception as e:
        logger.error("Search tracking error", error=str(e))
        return Response(
            {'error': 'Failed to track search'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_metrics(request):
    """Get system metrics"""
    try:
        # Get latest system metrics
        latest_metrics = SystemMetrics.objects.order_by('-timestamp').first()
        
        if not latest_metrics:
            return Response({
                'message': 'No system metrics available'
            })
        
        data = {
            'timestamp': latest_metrics.timestamp,
            'cpu_usage': float(latest_metrics.cpu_usage) if latest_metrics.cpu_usage else None,
            'memory_usage': float(latest_metrics.memory_usage) if latest_metrics.memory_usage else None,
            'disk_usage': float(latest_metrics.disk_usage) if latest_metrics.disk_usage else None,
            'database_connections': latest_metrics.database_connections,
            'database_size_mb': latest_metrics.database_size_mb,
            'active_users': latest_metrics.active_users,
            'response_time_avg': float(latest_metrics.response_time_avg) if latest_metrics.response_time_avg else None,
            'error_rate': float(latest_metrics.error_rate) if latest_metrics.error_rate else None
        }
        
        return Response(data)
        
    except Exception as e:
        logger.error("System metrics error", error=str(e))
        return Response(
            {'error': 'Failed to fetch system metrics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def public_test(request):
    """Public test endpoint to verify CORS and connectivity"""
    return Response({
        'message': 'CORS is working!',
        'timestamp': timezone.now().isoformat(),
        'user_authenticated': request.user.is_authenticated,
        'user_admin': request.user.is_staff if request.user.is_authenticated else False
    })


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
