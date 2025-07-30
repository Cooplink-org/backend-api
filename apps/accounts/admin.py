from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User

class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ('email', 'username', 'role', 'github_username', 'balance', 'is_verified', 'is_active', 'created_at')
    list_filter = ('role', 'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'username', 'github_username')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'github_id', 'github_username', 'balance', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

# Explicitly register the User model
admin.site.register(User, UserAdmin)

