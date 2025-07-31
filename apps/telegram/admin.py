from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TelegramLog


@admin.register(TelegramLog)
class TelegramLogAdmin(ModelAdmin):
    list_display = ('event_type', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('event_type',)
    readonly_fields = ('created_at',)
