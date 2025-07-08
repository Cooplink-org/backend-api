from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'admin-actions', views.AdminActionViewSet, basename='adminaction')
router.register(r'system-configurations', views.SystemConfigurationViewSet, basename='systemconfiguration')
router.register(r'maintenance-modes', views.MaintenanceModeViewSet, basename='maintenancemode')
router.register(r'notifications', views.AdminNotificationViewSet, basename='adminnotification')
router.register(r'backups', views.BackupRecordViewSet, basename='backuprecord')
router.register(r'system-health', views.SystemHealthViewSet, basename='systemhealth')
router.register(r'dashboard-widgets', views.AdminDashboardWidgetViewSet, basename='admindashboardwidget')
router.register(r'bulk-actions', views.BulkActionViewSet, basename='bulkaction')
router.register(r'admin-sessions', views.AdminSessionViewSet, basename='adminsession')

app_name = 'admin_panel'

urlpatterns = [
    # 📊 Dashboard & Analytics
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
    path('analytics/', views.analytics_dashboard, name='analytics-dashboard'),
    path('activities/', views.recent_activities, name='recent-activities'),
    
    # 👥 User Management
    path('users/', views.user_management, name='user-management'),
    
    # 📁 Project Management
    path('projects/', views.project_management, name='project-management'),
    
    # 🔔 Notifications & Health
    path('notifications/', views.notifications, name='notifications'),
    path('health/', views.health_status, name='health-status'),
    path('backup-status/', views.backup_status, name='backup-status'),
    
    # 🔧 Admin Actions
    path('bulk-user-action/', views.bulk_user_action, name='bulk-user-action'),
    path('bulk-project-action/', views.bulk_project_action, name='bulk-project-action'),
    path('user/<int:user_id>/', views.user_details, name='user-details'),
    path('project/<uuid:project_id>/', views.project_details, name='project-details'),
    path('export-data/', views.export_data, name='export-data'),
    path('system-overview/', views.system_overview, name='system-overview'),

    # API ViewSets
    path('', include(router.urls)),
]
