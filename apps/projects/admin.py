from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db import models
from unfold.admin import ModelAdmin
from .models import (
    Project, 
    ProjectTranslation, 
    Purchase, 
    Review, 
    ProjectReport
)


class ProjectTranslationInline(admin.TabularInline):
    model = ProjectTranslation
    extra = 0
    fields = ('language', 'title', 'description')


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('buyer', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = (
        'title', 
        'seller', 
        'project_type', 
        'price_uzs_formatted', 
        'downloads', 
        'rating', 
        'is_approved', 
        'is_active', 
        'created_at'
    )
    list_filter = (
        'project_type', 
        'is_approved', 
        'is_active', 
        'created_at', 
        'rating'
    )
    search_fields = (
        'title', 
        'description', 
        'languages', 
        'frameworks', 
        'seller__username', 
        'seller__email'
    )
    readonly_fields = (
        'id', 
        'downloads', 
        'rating', 
        'reviews_count', 
        'created_at', 
        'updated_at'
    )
    inlines = [ProjectTranslationInline, ReviewInline]
    
    fieldsets = (
        ('Project Information', {
            'fields': (
                'id', 
                'title', 
                'description', 
                'image', 
                'demo_link'
            )
        }),
        ('Technical Details', {
            'fields': (
                'project_type', 
                'languages', 
                'frameworks', 
                'file'
            )
        }),
        ('Pricing & Sales', {
            'fields': (
                'price_uzs', 
                'downloads', 
                'rating', 
                'reviews_count'
            )
        }),
        ('Status & Approval', {
            'fields': (
                'seller', 
                'is_approved', 
                'is_active'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def price_uzs_formatted(self, obj):
        return f"{obj.price_uzs:,.0f} UZS"
    price_uzs_formatted.short_description = 'Price'
    price_uzs_formatted.admin_order_field = 'price_uzs'
    
    actions = ['approve_projects', 'reject_projects', 'activate_projects', 'deactivate_projects']
    
    def approve_projects(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} projects approved.')
    approve_projects.short_description = 'Approve selected projects'
    
    def reject_projects(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} projects rejected.')
    reject_projects.short_description = 'Reject selected projects'
    
    def activate_projects(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} projects activated.')
    activate_projects.short_description = 'Activate selected projects'
    
    def deactivate_projects(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} projects deactivated.')
    deactivate_projects.short_description = 'Deactivate selected projects'


@admin.register(Purchase)
class PurchaseAdmin(ModelAdmin):
    list_display = (
        'id', 
        'buyer', 
        'project', 
        'amount_uzs_formatted', 
        'status', 
        'is_verified', 
        'created_at'
    )
    list_filter = (
        'status', 
        'is_verified', 
        'created_at', 
        'verification_deadline'
    )
    search_fields = (
        'buyer__username', 
        'buyer__email', 
        'project__title', 
        'payment_id'
    )
    readonly_fields = (
        'id', 
        'created_at', 
        'completed_at'
    )
    
    fieldsets = (
        ('Purchase Information', {
            'fields': (
                'id', 
                'buyer', 
                'project', 
                'amount_uzs', 
                'status'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_id', 
                'verification_deadline', 
                'is_verified', 
                'verification_notes'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'completed_at'
            )
        }),
    )
    
    def amount_uzs_formatted(self, obj):
        return f"{obj.amount_uzs:,.0f} UZS"
    amount_uzs_formatted.short_description = 'Amount'
    amount_uzs_formatted.admin_order_field = 'amount_uzs'
    
    actions = ['verify_purchases', 'complete_purchases']
    
    def verify_purchases(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} purchases verified.')
    verify_purchases.short_description = 'Verify selected purchases'
    
    def complete_purchases(self, request, queryset):
        updated = queryset.update(
            status='completed', 
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} purchases completed.')
    complete_purchases.short_description = 'Complete selected purchases'


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = (
        'project', 
        'buyer', 
        'rating', 
        'short_comment', 
        'created_at'
    )
    list_filter = (
        'rating', 
        'created_at', 
        'project__project_type'
    )
    search_fields = (
        'buyer__username', 
        'project__title', 
        'comment'
    )
    readonly_fields = ('created_at',)
    
    def short_comment(self, obj):
        if obj.comment:
            return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
        return 'No comment'
    short_comment.short_description = 'Comment Preview'


@admin.register(ProjectReport)
class ProjectReportAdmin(ModelAdmin):
    list_display = (
        'purchase', 
        'get_project_title', 
        'get_buyer', 
        'status', 
        'created_at'
    )
    list_filter = (
        'status', 
        'created_at', 
        'resolved_at'
    )
    search_fields = (
        'purchase__buyer__username', 
        'purchase__project__title', 
        'reason', 
        'admin_notes'
    )
    readonly_fields = (
        'created_at', 
        'resolved_at'
    )
    
    fieldsets = (
        ('Report Information', {
            'fields': (
                'purchase', 
                'reason', 
                'status'
            )
        }),
        ('Admin Response', {
            'fields': (
                'admin_notes', 
                'resolved_at'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        }),
    )
    
    def get_project_title(self, obj):
        return obj.purchase.project.title
    get_project_title.short_description = 'Project'
    get_project_title.admin_order_field = 'purchase__project__title'
    
    def get_buyer(self, obj):
        return obj.purchase.buyer.username
    get_buyer.short_description = 'Buyer'
    get_buyer.admin_order_field = 'purchase__buyer__username'
    
    actions = ['resolve_refund', 'resolve_release', 'dismiss_reports']
    
    def resolve_refund(self, request, queryset):
        updated = queryset.update(
            status='resolved_refund', 
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports resolved with refund.')
    resolve_refund.short_description = 'Resolve with refund'
    
    def resolve_release(self, request, queryset):
        updated = queryset.update(
            status='resolved_release', 
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports resolved with funds release.')
    resolve_release.short_description = 'Resolve with funds release'
    
    def dismiss_reports(self, request, queryset):
        updated = queryset.update(
            status='dismissed', 
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports dismissed.')
    dismiss_reports.short_description = 'Dismiss selected reports'


@admin.register(ProjectTranslation)
class ProjectTranslationAdmin(ModelAdmin):
    list_display = (
        'project', 
        'language', 
        'title', 
        'created_at'
    )
    list_filter = (
        'language', 
        'created_at'
    )
    search_fields = (
        'project__title', 
        'title', 
        'description'
    )
    readonly_fields = ('created_at',)
