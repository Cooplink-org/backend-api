# Generated by Django 5.2.3 on 2025-06-29 16:10

import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=10)),
                ('date', models.DateField()),
                ('new_projects', models.PositiveIntegerField(default=0)),
                ('approved_projects', models.PositiveIntegerField(default=0)),
                ('rejected_projects', models.PositiveIntegerField(default=0)),
                ('total_downloads', models.PositiveIntegerField(default=0)),
                ('total_views', models.PositiveIntegerField(default=0)),
                ('avg_rating', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=3)),
                ('reviews_count', models.PositiveIntegerField(default=0)),
                ('reports_count', models.PositiveIntegerField(default=0)),
                ('web_app_count', models.PositiveIntegerField(default=0)),
                ('mobile_app_count', models.PositiveIntegerField(default=0)),
                ('desktop_app_count', models.PositiveIntegerField(default=0)),
                ('script_count', models.PositiveIntegerField(default=0)),
                ('library_count', models.PositiveIntegerField(default=0)),
                ('api_count', models.PositiveIntegerField(default=0)),
                ('bot_count', models.PositiveIntegerField(default=0)),
                ('game_count', models.PositiveIntegerField(default=0)),
                ('other_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'analytics_project_metrics',
                'indexes': [models.Index(fields=['period', 'date'], name='analytics_p_period_41baf7_idx'), models.Index(fields=['date'], name='analytics_p_date_723c3d_idx')],
                'unique_together': {('period', 'date')},
            },
        ),
        migrations.CreateModel(
            name='RevenueAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=10)),
                ('date', models.DateField()),
                ('total_revenue', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('commission_revenue', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('seller_earnings', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('transactions_count', models.PositiveIntegerField(default=0)),
                ('avg_transaction_value', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('refunds_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('refunds_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'analytics_revenue',
                'indexes': [models.Index(fields=['period', 'date'], name='analytics_r_period_d2cac2_idx'), models.Index(fields=['date'], name='analytics_r_date_24cc56_idx')],
                'unique_together': {('period', 'date')},
            },
        ),
        migrations.CreateModel(
            name='SystemMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cpu_usage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('memory_usage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('disk_usage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('active_connections', models.PositiveIntegerField(blank=True, null=True)),
                ('database_size_mb', models.PositiveIntegerField(blank=True, null=True)),
                ('media_size_mb', models.PositiveIntegerField(blank=True, null=True)),
                ('response_time_avg', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('error_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ],
            options={
                'db_table': 'analytics_system_metrics',
                'indexes': [models.Index(fields=['timestamp'], name='analytics_s_timesta_5c1fd1_idx')],
            },
        ),
        migrations.CreateModel(
            name='TelegramMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=10)),
                ('date', models.DateField()),
                ('bot_starts', models.PositiveIntegerField(default=0)),
                ('auth_attempts', models.PositiveIntegerField(default=0)),
                ('successful_auths', models.PositiveIntegerField(default=0)),
                ('failed_auths', models.PositiveIntegerField(default=0)),
                ('account_links', models.PositiveIntegerField(default=0)),
                ('commands_used', models.PositiveIntegerField(default=0)),
                ('active_telegram_users', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'analytics_telegram_metrics',
                'indexes': [models.Index(fields=['period', 'date'], name='analytics_t_period_83c88e_idx'), models.Index(fields=['date'], name='analytics_t_date_350d5e_idx')],
                'unique_together': {('period', 'date')},
            },
        ),
        migrations.CreateModel(
            name='UserMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=10)),
                ('date', models.DateField()),
                ('new_users', models.PositiveIntegerField(default=0)),
                ('active_users', models.PositiveIntegerField(default=0)),
                ('new_sellers', models.PositiveIntegerField(default=0)),
                ('active_sellers', models.PositiveIntegerField(default=0)),
                ('new_buyers', models.PositiveIntegerField(default=0)),
                ('active_buyers', models.PositiveIntegerField(default=0)),
                ('telegram_linked_users', models.PositiveIntegerField(default=0)),
                ('verified_users', models.PositiveIntegerField(default=0)),
                ('retention_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('churn_rate', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'analytics_user_metrics',
                'indexes': [models.Index(fields=['period', 'date'], name='analytics_u_period_23610b_idx'), models.Index(fields=['date'], name='analytics_u_date_2ee93a_idx')],
                'unique_together': {('period', 'date')},
            },
        ),
        migrations.CreateModel(
            name='CustomEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('event_type', models.CharField(choices=[('business', 'Business Event'), ('technical', 'Technical Event'), ('user', 'User Event'), ('system', 'System Event'), ('marketing', 'Marketing Event')], max_length=20)),
                ('properties', models.JSONField(blank=True, default=dict)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('session_id', models.CharField(blank=True, max_length=40, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'analytics_custom_event',
                'indexes': [models.Index(fields=['name', 'created_at'], name='analytics_c_name_de6272_idx'), models.Index(fields=['event_type', 'created_at'], name='analytics_c_event_t_63b878_idx'), models.Index(fields=['user', 'created_at'], name='analytics_c_user_id_dd8c33_idx'), models.Index(fields=['created_at'], name='analytics_c_created_e17b8b_idx')],
            },
        ),
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_id', models.CharField(blank=True, max_length=40, null=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('path', models.CharField(max_length=500)),
                ('query_params', models.TextField(blank=True)),
                ('referrer', models.URLField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('browser', models.CharField(blank=True, max_length=100, null=True)),
                ('device_type', models.CharField(blank=True, max_length=50, null=True)),
                ('os', models.CharField(blank=True, max_length=100, null=True)),
                ('response_time_ms', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'analytics_page_view',
                'indexes': [models.Index(fields=['user', 'created_at'], name='analytics_p_user_id_70d566_idx'), models.Index(fields=['path', 'created_at'], name='analytics_p_path_44ef74_idx'), models.Index(fields=['ip_address', 'created_at'], name='analytics_p_ip_addr_f0ec0b_idx'), models.Index(fields=['session_id'], name='analytics_p_session_64e041_idx'), models.Index(fields=['country', 'created_at'], name='analytics_p_country_962cd3_idx'), models.Index(fields=['device_type', 'created_at'], name='analytics_p_device__011e61_idx')],
            },
        ),
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_id', models.CharField(blank=True, max_length=40, null=True)),
                ('query', models.CharField(max_length=500)),
                ('filters', models.JSONField(blank=True, default=dict)),
                ('results_count', models.PositiveIntegerField(default=0)),
                ('clicked_result_id', models.UUIDField(blank=True, null=True)),
                ('click_position', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'analytics_search_query',
                'indexes': [models.Index(fields=['user', 'created_at'], name='analytics_s_user_id_85f279_idx'), models.Index(fields=['query'], name='analytics_s_query_8ba586_idx'), models.Index(fields=['created_at'], name='analytics_s_created_3fae6a_idx'), models.Index(fields=['results_count'], name='analytics_s_results_e769a3_idx')],
            },
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_id', models.CharField(blank=True, max_length=40, null=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('action', models.CharField(choices=[('login', 'User Login'), ('logout', 'User Logout'), ('register', 'User Registration'), ('profile_update', 'Profile Update'), ('project_view', 'Project View'), ('project_purchase', 'Project Purchase'), ('project_upload', 'Project Upload'), ('search', 'Search Query'), ('download', 'File Download'), ('review_submit', 'Review Submission'), ('news_view', 'News Article View'), ('news_like', 'News Article Like'), ('telegram_auth', 'Telegram Authentication'), ('payment_initiated', 'Payment Initiated'), ('payment_completed', 'Payment Completed'), ('dispute_opened', 'Dispute Opened'), ('report_submitted', 'Report Submitted')], max_length=30)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('referrer', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'analytics_user_activity',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'action', 'created_at'], name='analytics_u_user_id_393dd1_idx'), models.Index(fields=['action', 'created_at'], name='analytics_u_action_a2509b_idx'), models.Index(fields=['ip_address', 'created_at'], name='analytics_u_ip_addr_264a6a_idx'), models.Index(fields=['session_id'], name='analytics_u_session_7afbe9_idx'), models.Index(fields=['content_type', 'object_id'], name='analytics_u_content_32e233_idx')],
            },
        ),
    ]
