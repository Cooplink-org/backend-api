from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class PaymentMethod(models.Model):
    METHOD_TYPES = [
        ('uzcard', 'UzCard'),
        ('humo', 'Humo'),
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('paypal', 'PayPal'),
        ('click', 'Click'),
        ('payme', 'Payme'),
        ('mirpay', 'MirPay'),
        ('balance', 'Account Balance'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    is_active = models.BooleanField(default=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0300'))  # 3%
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('1000.00'))
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('50000000.00'))
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='payment_methods/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_method'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Project Purchase'),
        ('refund', 'Refund'),
        ('withdrawal', 'Seller Withdrawal'),
        ('deposit', 'Account Deposit'),
        ('commission', 'Platform Commission'),
        ('penalty', 'Penalty'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='UZS')
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)  # amount - commission
    
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    external_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Related objects
    purchase = models.ForeignKey('projects.Purchase', on_delete=models.CASCADE, null=True, blank=True)
    withdrawal = models.ForeignKey('WithdrawalRequest', on_delete=models.CASCADE, null=True, blank=True)
    
    description = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments_transaction'
        indexes = [
            models.Index(fields=['user', 'status', 'created_at']),
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['external_transaction_id']),
            models.Index(fields=['purchase']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.transaction_type} - {self.amount} {self.currency} - {self.status}'


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('bank_transfer', 'Bank Transfer'),
        ('uzcard', 'UzCard'),
        ('humo', 'Humo'),
        ('paypal', 'PayPal'),
        ('click', 'Click'),
        ('payme', 'Payme'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_details = models.JSONField(default=dict)  # Card number, bank details, etc.
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    processed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_withdrawals')
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_withdrawal_request'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Withdrawal {self.amount} UZS - {self.user.username} - {self.status}'


class PaymentGatewayLog(models.Model):
    LOG_TYPES = [
        ('request', 'Request'),
        ('response', 'Response'),
        ('webhook', 'Webhook'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='gateway_logs')
    gateway_name = models.CharField(max_length=50)  # mirpay, click, payme, etc.
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    headers = models.JSONField(default=dict, blank=True)
    
    status_code = models.PositiveIntegerField(null=True, blank=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments_gateway_log'
        indexes = [
            models.Index(fields=['transaction', 'created_at']),
            models.Index(fields=['gateway_name', 'log_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']


class BalanceTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='balance_transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Related transaction
    related_transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    
    description = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments_balance_transaction'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['related_transaction']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.transaction_type} {self.amount} UZS for {self.user.username}'


class PaymentConfiguration(models.Model):
    """Global payment settings"""
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_configuration'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RecurringPayment(models.Model):
    """For subscription-based features in the future"""
    INTERVALS = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='recurring_payments')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='UZS')
    interval = models.CharField(max_length=10, choices=INTERVALS)
    interval_count = models.PositiveIntegerField(default=1)  # Every X intervals
    
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    next_payment_at = models.DateTimeField()
    last_payment_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_recurring_payment'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'next_payment_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']


class FinancialReport(models.Model):
    """Pre-calculated financial reports for admin dashboard"""
    REPORT_TYPES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('yearly', 'Yearly Report'),
    ]
    
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_commission = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_seller_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_refunds = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_withdrawals = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    transactions_count = models.PositiveIntegerField(default=0)
    successful_transactions = models.PositiveIntegerField(default=0)
    failed_transactions = models.PositiveIntegerField(default=0)
    
    avg_transaction_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    highest_transaction = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    report_data = models.JSONField(default=dict)  # Detailed breakdown
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_financial_report'
        unique_together = ['report_type', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['report_type', 'period_start']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-period_start']
