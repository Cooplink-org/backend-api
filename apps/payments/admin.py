from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum, Count
from django.contrib import admin
from .models import (
    PaymentMethod,
    Transaction,
    WithdrawalRequest,
    PaymentGatewayLog,
    BalanceTransaction,
    PaymentConfiguration,
    RecurringPayment,
    FinancialReport
)


class PaymentGatewayLogInline(admin.TabularInline):
    model = PaymentGatewayLog
    extra = 0
    fields = ('gateway_name', 'log_type', 'status_code', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'method_type',
        'commission_rate_formatted',
        'min_amount_formatted',
        'max_amount_formatted',
        'is_active',
        'created_at'
    )
    list_filter = ('method_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'method_type', 'description', 'icon', 'is_active')
        }),
        ('Financial Settings', {
            'fields': ('commission_rate', 'min_amount', 'max_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def commission_rate_formatted(self, obj):
        return f"{obj.commission_rate * 100:.2f}%"
    commission_rate_formatted.short_description = 'Commission'
    commission_rate_formatted.admin_order_field = 'commission_rate'
    
    def min_amount_formatted(self, obj):
        return f"{obj.min_amount:,.0f} UZS"
    min_amount_formatted.short_description = 'Min Amount'
    min_amount_formatted.admin_order_field = 'min_amount'
    
    def max_amount_formatted(self, obj):
        return f"{obj.max_amount:,.0f} UZS"
    max_amount_formatted.short_description = 'Max Amount'
    max_amount_formatted.admin_order_field = 'max_amount'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'transaction_type',
        'amount_formatted',
        'status',
        'payment_method',
        'created_at'
    )
    list_filter = (
        'transaction_type',
        'status',
        'payment_method',
        'currency',
        'created_at'
    )
    search_fields = (
        'user__username',
        'user__email',
        'external_transaction_id',
        'description'
    )
    readonly_fields = (
        'id',
        'net_amount',
        'created_at',
        'updated_at',
        'completed_at'
    )
    inlines = [PaymentGatewayLogInline]
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'id',
                'user',
                'transaction_type',
                'status',
                'description'
            )
        }),
        ('Financial Details', {
            'fields': (
                'amount',
                'currency',
                'commission_amount',
                'net_amount'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method',
                'external_transaction_id',
                'gateway_response'
            )
        }),
        ('Related Objects', {
            'fields': (
                'purchase',
                'withdrawal'
            )
        }),
        ('Technical Info', {
            'fields': (
                'ip_address',
                'user_agent',
                'failure_reason'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def amount_formatted(self, obj):
        return f"{obj.amount:,.0f} {obj.currency}"
    amount_formatted.short_description = 'Amount'
    amount_formatted.admin_order_field = 'amount'
    
    actions = ['mark_completed', 'mark_failed', 'mark_cancelled']
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} transactions marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} transactions marked as failed.')
    mark_failed.short_description = 'Mark as failed'
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} transactions marked as cancelled.')
    mark_cancelled.short_description = 'Mark as cancelled'


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'amount_formatted',
        'payment_method',
        'status',
        'processed_by',
        'created_at'
    )
    list_filter = (
        'status',
        'payment_method',
        'created_at',
        'processed_at'
    )
    search_fields = (
        'user__username',
        'user__email',
        'payment_details'
    )
    readonly_fields = (
        'id',
        'net_amount',
        'created_at',
        'updated_at',
        'processed_at',
        'completed_at'
    )
    
    fieldsets = (
        ('Withdrawal Information', {
            'fields': (
                'id',
                'user',
                'amount',
                'commission_amount',
                'net_amount'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method',
                'payment_details'
            )
        }),
        ('Status & Processing', {
            'fields': (
                'status',
                'processed_by',
                'admin_notes',
                'rejection_reason'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'processed_at',
                'completed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def amount_formatted(self, obj):
        return f"{obj.amount:,.0f} UZS"
    amount_formatted.short_description = 'Amount'
    amount_formatted.admin_order_field = 'amount'
    
    actions = ['approve_withdrawals', 'reject_withdrawals', 'mark_processing']
    
    def approve_withdrawals(self, request, queryset):
        updated = queryset.update(
            status='approved',
            processed_by=request.user,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} withdrawal requests approved.')
    approve_withdrawals.short_description = 'Approve withdrawal requests'
    
    def reject_withdrawals(self, request, queryset):
        updated = queryset.update(
            status='rejected',
            processed_by=request.user,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} withdrawal requests rejected.')
    reject_withdrawals.short_description = 'Reject withdrawal requests'
    
    def mark_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} withdrawal requests marked as processing.')
    mark_processing.short_description = 'Mark as processing'


@admin.register(PaymentGatewayLog)
class PaymentGatewayLogAdmin(admin.ModelAdmin):
    list_display = (
        'transaction',
        'gateway_name',
        'log_type',
        'status_code',
        'response_time_ms',
        'created_at'
    )
    list_filter = (
        'gateway_name',
        'log_type',
        'status_code',
        'created_at'
    )
    search_fields = (
        'transaction__id',
        'gateway_name',
        'error_message'
    )
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        ('Log Information', {
            'fields': (
                'id',
                'transaction',
                'gateway_name',
                'log_type',
                'status_code',
                'response_time_ms'
            )
        }),
        ('Request/Response Data', {
            'fields': (
                'request_data',
                'response_data',
                'headers'
            ),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': (
                'error_message',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
            )
        }),
    )


@admin.register(BalanceTransaction)
class BalanceTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'transaction_type',
        'amount_formatted',
        'balance_after_formatted',
        'description',
        'created_at'
    )
    list_filter = (
        'transaction_type',
        'created_at'
    )
    search_fields = (
        'user__username',
        'user__email',
        'description'
    )
    readonly_fields = (
        'id',
        'balance_before',
        'balance_after',
        'created_at'
    )
    
    def amount_formatted(self, obj):
        sign = '+' if obj.transaction_type == 'credit' else '-'
        return f"{sign}{obj.amount:,.0f} UZS"
    amount_formatted.short_description = 'Amount'
    amount_formatted.admin_order_field = 'amount'
    
    def balance_after_formatted(self, obj):
        return f"{obj.balance_after:,.0f} UZS"
    balance_after_formatted.short_description = 'Balance After'
    balance_after_formatted.admin_order_field = 'balance_after'


@admin.register(PaymentConfiguration)
class PaymentConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'value_preview',
        'is_active',
        'updated_at'
    )
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def value_preview(self, obj):
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value
    value_preview.short_description = 'Value'


@admin.register(RecurringPayment)
class RecurringPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'name',
        'amount_formatted',
        'interval_display',
        'status',
        'next_payment_at',
        'created_at'
    )
    list_filter = (
        'status',
        'interval',
        'created_at',
        'next_payment_at'
    )
    search_fields = (
        'user__username',
        'name',
        'description'
    )
    readonly_fields = (
        'id',
        'last_payment_at',
        'created_at',
        'updated_at'
    )
    
    def amount_formatted(self, obj):
        return f"{obj.amount:,.0f} {obj.currency}"
    amount_formatted.short_description = 'Amount'
    amount_formatted.admin_order_field = 'amount'
    
    def interval_display(self, obj):
        if obj.interval_count == 1:
            return obj.get_interval_display()
        return f"Every {obj.interval_count} {obj.get_interval_display().lower()}s"
    interval_display.short_description = 'Interval'
    
    actions = ['activate_payments', 'pause_payments', 'cancel_payments']
    
    def activate_payments(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} recurring payments activated.')
    activate_payments.short_description = 'Activate recurring payments'
    
    def pause_payments(self, request, queryset):
        updated = queryset.update(status='paused')
        self.message_user(request, f'{updated} recurring payments paused.')
    pause_payments.short_description = 'Pause recurring payments'
    
    def cancel_payments(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} recurring payments cancelled.')
    cancel_payments.short_description = 'Cancel recurring payments'


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = (
        'report_type',
        'period_start',
        'period_end',
        'total_revenue_formatted',
        'transactions_count',
        'created_at'
    )
    list_filter = (
        'report_type',
        'period_start',
        'created_at'
    )
    search_fields = ('report_type',)
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Report Information', {
            'fields': (
                'report_type',
                'period_start',
                'period_end'
            )
        }),
        ('Revenue Metrics', {
            'fields': (
                'total_revenue',
                'total_commission',
                'total_seller_earnings',
                'total_refunds',
                'total_withdrawals'
            )
        }),
        ('Transaction Metrics', {
            'fields': (
                'transactions_count',
                'successful_transactions',
                'failed_transactions',
                'avg_transaction_value',
                'highest_transaction'
            )
        }),
        ('Additional Data', {
            'fields': (
                'report_data',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def total_revenue_formatted(self, obj):
        return f"{obj.total_revenue:,.0f} UZS"
    total_revenue_formatted.short_description = 'Total Revenue'
    total_revenue_formatted.admin_order_field = 'total_revenue'
