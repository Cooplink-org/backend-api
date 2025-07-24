from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'message': 'Cooplink API - Backend Only',
        'version': '1.0.0',
        'status': 'operational',
        'endpoints': {
            'authentication': '/api/auth/',
            'projects': '/api/projects/',
            'news': '/api/news/',
            'payments': '/api/payments/',
            'analytics': '/api/analytics/',
            'telegram': '/api/telegram/',
            'admin': '/api/admin/',
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('api/', api_root, name='api-root-with-prefix'),
    path('admin/', admin.site.urls),
    path('api/auth/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('api/projects/', include(('apps.projects.urls', 'projects'), namespace='projects')),
    path('api/news/', include(('apps.news.urls', 'news'), namespace='news')),
    path('api/payments/', include(('apps.payments.urls', 'payments'), namespace='payments')),
    path('api/analytics/', include(('apps.analytics.urls', 'analytics'), namespace='analytics')),
    # path('api/telegram/', include(('apps.telegram.urls', 'telegram'), namespace='telegram')),
    path('api/admin/', include(('apps.admin_panel.urls', 'admin_panel'), namespace='admin_panel')),
    path('api/qa/', include(('apps.qa.urls', 'qa'), namespace='qa')),
]

