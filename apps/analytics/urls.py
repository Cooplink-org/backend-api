from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Public test endpoint
    path('test/', views.public_test, name='public-test'),
    
    # Dashboard endpoints
    path('dashboard/', views.dashboard_overview, name='dashboard-overview'),
    path('users/', views.user_analytics, name='user-analytics'),
    path('revenue/', views.revenue_analytics, name='revenue-analytics'),
    path('system/', views.system_metrics, name='system-metrics'),
    
    # Tracking endpoints
    path('track/activity/', views.track_user_activity, name='track-activity'),
    path('track/pageview/', views.track_page_view, name='track-pageview'),
    path('track/search/', views.track_search_query, name='track-search'),
]
