from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta

# Configure the admin site
admin.site.site_header = "🚀 Cooplink Administration"
admin.site.site_title = "Cooplink Admin"
admin.site.index_title = "📊 Platform Management Dashboard"

# Custom admin site with enhanced dashboard
class CooplinkAdminSite(admin.AdminSite):
    site_header = "🚀 Cooplink Administration Panel"
    site_title = "Cooplink Admin"
    index_title = "📊 Platform Management Dashboard"
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered with the admin site.
        """
        app_dict = self._build_app_dict(request, app_label)
        
        # Sort apps by priority
        app_order = {
            'accounts': 1,
            'projects': 2,
            'payments': 3,
            'news': 4,
            'analytics': 5,
            'admin_panel': 6,
            'telegram': 7,
        }
        
        # Sort the apps list according to the custom order
        app_list = sorted(app_dict.values(), 
                         key=lambda x: app_order.get(x['app_label'], 999))
        
        # Add custom icons and descriptions
        icon_map = {
            'accounts': '👥',
            'projects': '📁',
            'payments': '💰',
            'news': '📰',
            'analytics': '📊',
            'admin_panel': '⚙️',
            'telegram': '📱',
            'auth': '🔐',
            'sites': '🌐',
        }
        
        description_map = {
            'accounts': 'User management and authentication',
            'projects': 'Code projects and marketplace',
            'payments': 'Payment processing and transactions',
            'news': 'Platform news and announcements',
            'analytics': 'Platform analytics and metrics',
            'admin_panel': 'Administrative tools and settings',
            'telegram': 'Telegram bot management',
            'auth': 'Authentication and permissions',
            'sites': 'Site configuration',
        }
        
        for app in app_list:
            app_label = app['app_label']
            app['icon'] = icon_map.get(app_label, '📦')
            app['description'] = description_map.get(app_label, 'Application management')
            
            # Add model counts and statistics
            if app_label == 'accounts':
                from apps.accounts.models import User
                app['stats'] = {
                    'total_users': User.objects.count(),
                    'verified_users': User.objects.filter(is_verified=True).count(),
                    'sellers': User.objects.filter(role='seller').count(),
                }
            elif app_label == 'projects':
                from apps.projects.models import Project, Purchase
                app['stats'] = {
                    'total_projects': Project.objects.count(),
                    'approved_projects': Project.objects.filter(is_approved=True).count(),
                    'total_purchases': Purchase.objects.count(),
                }
            elif app_label == 'payments':
                from apps.payments.models import Transaction
                today = timezone.now().date()
                app['stats'] = {
                    'total_transactions': Transaction.objects.count(),
                    'today_transactions': Transaction.objects.filter(created_at__date=today).count(),
                    'completed_transactions': Transaction.objects.filter(status='completed').count(),
                }
        
        return app_list
    
    def index(self, request, extra_context=None):
        """
        Enhanced admin index with dashboard metrics
        """
        extra_context = extra_context or {}
        
        # Get key metrics for dashboard
        try:
            from apps.accounts.models import User
            from apps.projects.models import Project, Purchase
            from apps.payments.models import Transaction
            from apps.news.models import NewsArticle
            
            # Calculate date ranges
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # User metrics
            total_users = User.objects.count()
            new_users_week = User.objects.filter(created_at__date__gte=week_ago).count()
            verified_users = User.objects.filter(is_verified=True).count()
            
            # Project metrics
            total_projects = Project.objects.count()
            approved_projects = Project.objects.filter(is_approved=True).count()
            pending_projects = Project.objects.filter(is_approved=False, is_active=True).count()
            
            # Transaction metrics
            total_transactions = Transaction.objects.count()
            completed_transactions = Transaction.objects.filter(status='completed').count()
            today_transactions = Transaction.objects.filter(created_at__date=today).count()
            
            # Revenue metrics (last 30 days)
            recent_revenue = Transaction.objects.filter(
                status='completed',
                created_at__date__gte=month_ago
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # News metrics
            published_news = NewsArticle.objects.filter(status='published').count()
            
            extra_context.update({
                'dashboard_metrics': {
                    'users': {
                        'total': total_users,
                        'new_week': new_users_week,
                        'verified': verified_users,
                        'verification_rate': (verified_users / total_users * 100) if total_users > 0 else 0,
                    },
                    'projects': {
                        'total': total_projects,
                        'approved': approved_projects,
                        'pending': pending_projects,
                        'approval_rate': (approved_projects / total_projects * 100) if total_projects > 0 else 0,
                    },
                    'transactions': {
                        'total': total_transactions,
                        'completed': completed_transactions,
                        'today': today_transactions,
                        'success_rate': (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0,
                    },
                    'revenue': {
                        'last_30_days': recent_revenue,
                        'formatted': f"{recent_revenue:,.0f} UZS" if recent_revenue else "0 UZS",
                    },
                    'content': {
                        'published_news': published_news,
                    }
                },
                'recent_activities': self.get_recent_activities(),
                'system_alerts': self.get_system_alerts(),
            })
        except Exception as e:
            # Gracefully handle any database errors during dashboard loading
            extra_context['dashboard_error'] = str(e)
        
        return super().index(request, extra_context)
    
    def get_recent_activities(self):
        """Get recent admin activities for dashboard"""
        try:
            from apps.admin_panel.models import AdminAction
            return AdminAction.objects.select_related('admin', 'target_user')[:10]
        except:
            return []
    
    def get_system_alerts(self):
        """Get system alerts for dashboard"""
        alerts = []
        
        try:
            # Check for pending approvals
            from apps.projects.models import Project
            pending_projects = Project.objects.filter(is_approved=False, is_active=True).count()
            if pending_projects > 0:
                alerts.append({
                    'type': 'warning',
                    'message': f'{pending_projects} projects pending approval',
                    'url': '/admin/projects/project/?is_approved__exact=0&is_active__exact=1'
                })
            
            # Check for failed transactions
            from apps.payments.models import Transaction
            failed_transactions = Transaction.objects.filter(status='failed').count()
            if failed_transactions > 0:
                alerts.append({
                    'type': 'error',
                    'message': f'{failed_transactions} failed transactions require attention',
                    'url': '/admin/payments/transaction/?status__exact=failed'
                })
            
            # Check for unread notifications
            from apps.admin_panel.models import AdminNotification
            unread_notifications = AdminNotification.objects.filter(
                is_read=False, 
                is_dismissed=False
            ).count()
            if unread_notifications > 0:
                alerts.append({
                    'type': 'info',
                    'message': f'{unread_notifications} unread notifications',
                    'url': '/admin/admin_panel/adminnotification/?is_read__exact=0'
                })
                
        except Exception:
            pass  # Silently handle errors
        
        return alerts


def dashboard_callback(request, context):
    """
    Dashboard callback function for django-unfold charts and analytics.
    Returns data for rendering charts on the admin dashboard.
    """
    try:
        from apps.accounts.models import User
        from apps.projects.models import Project, Purchase
        from apps.payments.models import Transaction
        from apps.news.models import NewsArticle
        
        # Calculate date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User registration trend (last 30 days)
        user_registration_data = []
        for i in range(30):
            date = today - timedelta(days=i)
            count = User.objects.filter(created_at__date=date).count()
            user_registration_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        user_registration_data.reverse()
        
        # Transaction volume trend (last 30 days)
        transaction_volume_data = []
        for i in range(30):
            date = today - timedelta(days=i)
            volume = Transaction.objects.filter(
                created_at__date=date,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            transaction_volume_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'volume': float(volume)
            })
        transaction_volume_data.reverse()
        
        # Project types distribution
        project_types = Project.objects.values('project_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # User role distribution
        user_roles = User.objects.values('role').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Transaction status distribution
        transaction_status = Transaction.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Monthly revenue trend (last 12 months)
        monthly_revenue = []
        for i in range(12):
            month_start = today.replace(day=1) - timedelta(days=i*30)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            revenue = Transaction.objects.filter(
                created_at__date__gte=month_start,
                created_at__date__lte=month_end,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_revenue.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': float(revenue)
            })
        monthly_revenue.reverse()
        
        # Top selling projects
        top_projects = Project.objects.annotate(
            purchase_count=Count('purchases')
        ).order_by('-purchase_count')[:5]
        
        # Recent activity counts
        recent_stats = {
            'new_users_today': User.objects.filter(created_at__date=today).count(),
            'new_projects_today': Project.objects.filter(created_at__date=today).count(),
            'transactions_today': Transaction.objects.filter(created_at__date=today).count(),
            'revenue_today': Transaction.objects.filter(
                created_at__date=today,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0,
        }
        
        context.update({
            'dashboard_data': {
                'user_registration_trend': user_registration_data,
                'transaction_volume_trend': transaction_volume_data,
                'project_types': list(project_types),
                'user_roles': list(user_roles),
                'transaction_status': list(transaction_status),
                'monthly_revenue': monthly_revenue,
                'top_projects': [
                    {
                        'name': project.title if hasattr(project, 'title') else project.name,
                        'purchases': project.purchase_count,
                        'price': float(project.price_uzs) if hasattr(project, 'price_uzs') else 0
                    }
                    for project in top_projects
                ],
                'recent_stats': recent_stats,
            },
            'charts': {
                'user_growth': {
                    'type': 'line',
                    'data': {
                        'labels': [item['date'] for item in user_registration_data],
                        'datasets': [{
                            'label': 'New Users',
                            'data': [item['count'] for item in user_registration_data],
                            'borderColor': 'rgb(75, 192, 192)',
                            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                            'tension': 0.1
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'legend': {
                                'position': 'top',
                            },
                            'title': {
                                'display': True,
                                'text': '📈 User Registration Trend (Last 30 Days)'
                            }
                        }
                    }
                },
                'revenue_trend': {
                    'type': 'bar',
                    'data': {
                        'labels': [item['month'] for item in monthly_revenue],
                        'datasets': [{
                            'label': 'Revenue (UZS)',
                            'data': [item['revenue'] for item in monthly_revenue],
                            'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                            'borderColor': 'rgba(54, 162, 235, 1)',
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': '💰 Monthly Revenue Trend'
                            }
                        }
                    }
                },
                'project_types': {
                    'type': 'doughnut',
                    'data': {
                        'labels': [item['project_type'] for item in project_types],
                        'datasets': [{
                            'data': [item['count'] for item in project_types],
                            'backgroundColor': [
                                '#FF6384',
                                '#36A2EB',
                                '#FFCE56',
                                '#4BC0C0',
                                '#9966FF'
                            ]
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': '📁 Project Types Distribution'
                            }
                        }
                    }
                },
                'user_roles': {
                    'type': 'pie',
                    'data': {
                        'labels': [item['role'] for item in user_roles],
                        'datasets': [{
                            'data': [item['count'] for item in user_roles],
                            'backgroundColor': [
                                '#FF6384',
                                '#36A2EB',
                                '#FFCE56',
                                '#4BC0C0'
                            ]
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': '👥 User Roles Distribution'
                            }
                        }
                    }
                },
                'transaction_status': {
                    'type': 'bar',
                    'data': {
                        'labels': [item['status'] for item in transaction_status],
                        'datasets': [{
                            'label': 'Transactions',
                            'data': [item['count'] for item in transaction_status],
                            'backgroundColor': [
                                '#28a745',  # completed - green
                                '#ffc107',  # pending - yellow
                                '#dc3545',  # failed - red
                                '#17a2b8'   # processing - blue
                            ]
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': '📊 Transaction Status Distribution'
                            }
                        }
                    }
                }
            }
        })
        
        return context
    except Exception as e:
        # Return minimal context if there's an error
        context.update({
            'dashboard_error': str(e),
            'charts': {},
            'recent_stats': {},
            'message': 'Dashboard data unavailable - please check database connections'
        })
        return context


# Use the default admin site with customizations
# We'll enhance the default admin site instead of creating a custom one

# Add enhanced admin actions
def export_selected_as_csv(modeladmin, request, queryset):
    """Export selected objects as CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{queryset.model._meta.verbose_name_plural}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    headers = [field.name for field in queryset.model._meta.fields]
    writer.writerow(headers)
    
    # Write data
    for obj in queryset:
        row = []
        for field in queryset.model._meta.fields:
            value = getattr(obj, field.name)
            if value is None:
                value = ''
            row.append(str(value))
        writer.writerow(row)
    
    return response

export_selected_as_csv.short_description = "📊 Export selected as CSV"

def mark_as_verified(modeladmin, request, queryset):
    """Mark selected users as verified"""
    updated = queryset.update(is_verified=True)
    modeladmin.message_user(request, f'{updated} users marked as verified.')

mark_as_verified.short_description = "✅ Mark selected users as verified"

def send_notification(modeladmin, request, queryset):
    """Send notification to selected users"""
    # This would integrate with a notification system
    pass

send_notification.short_description = "📢 Send notification to selected users"

# Register common admin actions
admin.site.add_action(export_selected_as_csv)
admin.site.add_action(mark_as_verified)

# Enhanced admin list filters
class RecentlyCreatedListFilter(admin.SimpleListFilter):
    title = 'Recently Created'
    parameter_name = 'recent'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(created_at__date=timezone.now().date())
        if self.value() == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)
        if self.value() == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=month_ago)


class ActiveStatusListFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'active_status'
    
    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)
