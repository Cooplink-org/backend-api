# Generated by Django 5.2.3 on 2025-06-29 17:04

import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('value', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'payments_configuration',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('method_type', models.CharField(choices=[('uzcard', 'UzCard'), ('humo', 'Humo'), ('visa', 'Visa'), ('mastercard', 'MasterCard'), ('paypal', 'PayPal'), ('click', 'Click'), ('payme', 'Payme'), ('mirpay', 'MirPay'), ('balance', 'Account Balance')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('commission_rate', models.DecimalField(decimal_places=4, default=Decimal('0.0300'), max_digits=5)),
                ('min_amount', models.DecimalField(decimal_places=2, default=Decimal('1000.00'), max_digits=12)),
                ('max_amount', models.DecimalField(decimal_places=2, default=Decimal('50000000.00'), max_digits=12)),
                ('description', models.TextField(blank=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='payment_methods/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'payments_method',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FinancialReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('daily', 'Daily Report'), ('weekly', 'Weekly Report'), ('monthly', 'Monthly Report'), ('yearly', 'Yearly Report')], max_length=10)),
                ('period_start', models.DateTimeField()),
                ('period_end', models.DateTimeField()),
                ('total_revenue', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('total_commission', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('total_seller_earnings', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('total_refunds', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('total_withdrawals', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('transactions_count', models.PositiveIntegerField(default=0)),
                ('successful_transactions', models.PositiveIntegerField(default=0)),
                ('failed_transactions', models.PositiveIntegerField(default=0)),
                ('avg_transaction_value', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('highest_transaction', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('report_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'payments_financial_report',
                'ordering': ['-period_start'],
                'indexes': [models.Index(fields=['report_type', 'period_start'], name='payments_fi_report__808607_idx'), models.Index(fields=['created_at'], name='payments_fi_created_5f397d_idx')],
                'unique_together': {('report_type', 'period_start', 'period_end')},
            },
        ),
        migrations.CreateModel(
            name='WithdrawalRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('commission_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('payment_method', models.CharField(choices=[('bank_transfer', 'Bank Transfer'), ('uzcard', 'UzCard'), ('humo', 'Humo'), ('paypal', 'PayPal'), ('click', 'Click'), ('payme', 'Payme')], max_length=20)),
                ('payment_details', models.JSONField(default=dict)),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('processing', 'Processing'), ('completed', 'Completed'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('admin_notes', models.TextField(blank=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('processed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_withdrawals', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawal_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'payments_withdrawal_request',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_type', models.CharField(choices=[('purchase', 'Project Purchase'), ('refund', 'Refund'), ('withdrawal', 'Seller Withdrawal'), ('deposit', 'Account Deposit'), ('commission', 'Platform Commission'), ('penalty', 'Penalty')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded'), ('disputed', 'Disputed')], default='pending', max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('currency', models.CharField(default='UZS', max_length=3)),
                ('commission_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('external_transaction_id', models.CharField(blank=True, max_length=255, null=True)),
                ('gateway_response', models.JSONField(blank=True, default=dict)),
                ('description', models.TextField(blank=True)),
                ('failure_reason', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.paymentmethod')),
                ('purchase', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.purchase')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to=settings.AUTH_USER_MODEL)),
                ('withdrawal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.withdrawalrequest')),
            ],
            options={
                'db_table': 'payments_transaction',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RecurringPayment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(default='UZS', max_length=3)),
                ('interval', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=10)),
                ('interval_count', models.PositiveIntegerField(default=1)),
                ('status', models.CharField(choices=[('active', 'Active'), ('paused', 'Paused'), ('cancelled', 'Cancelled'), ('expired', 'Expired')], default='active', max_length=20)),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField(blank=True, null=True)),
                ('next_payment_at', models.DateTimeField()),
                ('last_payment_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.paymentmethod')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'payments_recurring_payment',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'status'], name='payments_re_user_id_621281_idx'), models.Index(fields=['status', 'next_payment_at'], name='payments_re_status_439454_idx'), models.Index(fields=['created_at'], name='payments_re_created_9d9338_idx')],
            },
        ),
        migrations.CreateModel(
            name='PaymentGatewayLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('gateway_name', models.CharField(max_length=50)),
                ('log_type', models.CharField(choices=[('request', 'Request'), ('response', 'Response'), ('webhook', 'Webhook'), ('error', 'Error')], max_length=20)),
                ('request_data', models.JSONField(blank=True, default=dict)),
                ('response_data', models.JSONField(blank=True, default=dict)),
                ('headers', models.JSONField(blank=True, default=dict)),
                ('status_code', models.PositiveIntegerField(blank=True, null=True)),
                ('response_time_ms', models.PositiveIntegerField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gateway_logs', to='payments.transaction')),
            ],
            options={
                'db_table': 'payments_gateway_log',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['transaction', 'created_at'], name='payments_ga_transac_a30799_idx'), models.Index(fields=['gateway_name', 'log_type'], name='payments_ga_gateway_d74fa0_idx'), models.Index(fields=['created_at'], name='payments_ga_created_c2a61b_idx')],
            },
        ),
        migrations.CreateModel(
            name='BalanceTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_type', models.CharField(choices=[('credit', 'Credit'), ('debit', 'Debit')], max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('balance_before', models.DecimalField(decimal_places=2, max_digits=12)),
                ('balance_after', models.DecimalField(decimal_places=2, max_digits=12)),
                ('description', models.CharField(max_length=255)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balance_transactions', to=settings.AUTH_USER_MODEL)),
                ('related_transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.transaction')),
            ],
            options={
                'db_table': 'payments_balance_transaction',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'created_at'], name='payments_ba_user_id_f114d7_idx'), models.Index(fields=['related_transaction'], name='payments_ba_related_ca3f35_idx'), models.Index(fields=['created_at'], name='payments_ba_created_70386b_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='withdrawalrequest',
            index=models.Index(fields=['user', 'status'], name='payments_wi_user_id_3f020a_idx'),
        ),
        migrations.AddIndex(
            model_name='withdrawalrequest',
            index=models.Index(fields=['status', 'created_at'], name='payments_wi_status_630963_idx'),
        ),
        migrations.AddIndex(
            model_name='withdrawalrequest',
            index=models.Index(fields=['created_at'], name='payments_wi_created_0d086c_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['user', 'status', 'created_at'], name='payments_tr_user_id_8d8d07_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['transaction_type', 'status'], name='payments_tr_transac_a6e8b9_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['external_transaction_id'], name='payments_tr_externa_7220bd_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['purchase'], name='payments_tr_purchas_e896a3_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['created_at'], name='payments_tr_created_02ae92_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['status', 'created_at'], name='payments_tr_status_e3597b_idx'),
        ),
    ]
