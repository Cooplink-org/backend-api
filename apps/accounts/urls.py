from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # GitHub OAuth endpoints
    path('github/initiate/', views.github_oauth_initiate, name='github_oauth_initiate'),
    path('github/callback/', views.github_oauth_callback, name='github_oauth_callback'),
    path('github/link/', views.link_github, name='github_link'),
]
