from django.urls import path
from . import views

app_name = 'telegram'

urlpatterns = [
    # Telegram webhook endpoint
    path('webhook/', views.webhook_view, name='webhook'),
    # Bot status endpoints
    path('status/', views.bot_status_view, name='status'),
    path('bot/status/', views.bot_status_view, name='bot_status'),
    path('bot/commands/', views.bot_commands_view, name='bot_commands'),
]
