from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'projects'

router = DefaultRouter()
router.register(r'', views.ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
    path('purchases/', views.PurchaseListView.as_view(), name='purchase-list'),
    path('purchases/create/', views.PurchaseCreateView.as_view(), name='purchase-create'),
    path('purchases/<uuid:pk>/', views.PurchaseDetailView.as_view(), name='purchase-detail'),
    path('projects/<uuid:project_id>/reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('my-projects/', views.MyProjectsView.as_view(), name='my-projects'),
    path('upload/', views.ProjectUploadView.as_view(), name='project-upload'),
    path('projects/<uuid:pk>/update/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('projects/<uuid:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('projects/<uuid:pk>/download/', views.ProjectDownloadView.as_view(), name='project-download'),
    path('projects/<uuid:pk>/stats/', views.ProjectStatsView.as_view(), name='project-stats'),
    path('reports/create/', views.ProjectReportCreateView.as_view(), name='project-report-create'),
]
