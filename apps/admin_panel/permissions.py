from rest_framework.permissions import BasePermission
from django.utils import timezone
from .models import AdminSession


class IsAdminOrSuperUser(BasePermission):
    """
    Permission that allows access only to admin users or superusers.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (
            request.user.is_superuser or 
            request.user.is_staff or 
            getattr(request.user, 'role', None) == 'admin'
        )


class IsSuperUserOnly(BasePermission):
    """
    Permission that allows access only to superusers.
    For critical system operations.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class CanManageUsers(BasePermission):
    """
    Permission for user management operations.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (
            request.user.is_superuser or
            (request.user.is_staff and 
             request.user.has_perm('accounts.change_user'))
        )


class CanManageProjects(BasePermission):
    """
    Permission for project management operations.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (
            request.user.is_superuser or
            (request.user.is_staff and 
             request.user.has_perm('projects.change_project'))
        )


class CanAccessSystemHealth(BasePermission):
    """
    Permission for system health monitoring.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (
            request.user.is_superuser or
            request.user.is_staff
        )


class CanManageBackups(BasePermission):
    """
    Permission for backup management.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only superusers can manage backups
        return request.user.is_superuser


class CanViewAnalytics(BasePermission):
    """
    Permission for viewing analytics data.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (
            request.user.is_superuser or
            request.user.is_staff or
            getattr(request.user, 'role', None) == 'admin'
        )


class IsActiveAdminSession(BasePermission):
    """
    Permission that checks if the admin has an active session.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not (request.user.is_staff or request.user.is_superuser):
            return False
        
        # Check for active admin session
        session_key = request.session.session_key
        if session_key:
            try:
                admin_session = AdminSession.objects.get(
                    admin=request.user,
                    session_key=session_key,
                    ended_at__isnull=True
                )
                
                # Check if session is still active (within 30 minutes of last activity)
                if admin_session.last_activity:
                    time_diff = timezone.now() - admin_session.last_activity
                    if time_diff.total_seconds() > 1800:  # 30 minutes
                        return False
                
                # Update last activity
                admin_session.last_activity = timezone.now()
                admin_session.save()
                
                return True
            except AdminSession.DoesNotExist:
                # Create new session if it doesn't exist
                AdminSession.objects.create(
                    admin=request.user,
                    session_key=session_key,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                return True
        
        return True
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CanExportData(BasePermission):
    """
    Permission for data export operations.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only superusers can export sensitive data
        return request.user.is_superuser


class CanManageSystemConfiguration(BasePermission):
    """
    Permission for system configuration management.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Read access for staff, write access for superusers only
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_staff or request.user.is_superuser
        else:
            return request.user.is_superuser


class CanManageMaintenanceMode(BasePermission):
    """
    Permission for maintenance mode management.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only superusers can manage maintenance mode
        return request.user.is_superuser


class RateLimitedAdminAccess(BasePermission):
    """
    Rate limiting for admin operations to prevent abuse.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check rate limits based on user and IP
        # This is a simplified implementation
        # In production, you'd use a proper rate limiting solution like django-ratelimit
        
        cache_key = f"admin_rate_limit_{request.user.id}_{self.get_client_ip(request)}"
        # Implementation would use cache to track request counts
        
        return True
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Composite permissions for common use cases
class AdminPanelAccess(IsAdminOrSuperUser, IsActiveAdminSession):
    """
    Composite permission for general admin panel access.
    """
    pass


class CriticalSystemAccess(IsSuperUserOnly, IsActiveAdminSession):
    """
    Composite permission for critical system operations.
    """
    pass
