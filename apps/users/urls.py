from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

router = DefaultRouter()
router.register('profiles', views.UserProfileViewSet)
router.register('skills', views.UserSkillViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', views.user_profile, name='user-profile'),
    path('dashboard/', views.user_dashboard, name='user-dashboard'),
    path('settings/', views.user_settings, name='user-settings'),
]
