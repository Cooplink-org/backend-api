from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from unittest.mock import patch

from .models import (
    AdminAction, SystemConfiguration, MaintenanceMode, AdminNotification,
    BackupRecord, SystemHealth, AdminDashboardWidget, BulkAction, AdminSession
)
from apps.projects.models import Project
from apps.payments.models import Transaction

User = get_user_model()


class AdminPanelAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='user123',
            role='buyer'
        )
        
        # Create seller user
        self.seller_user = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='seller123',
            role='seller'
        )
        
        # Get JWT tokens
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.user_token = str(RefreshToken.for_user(self.regular_user).access_token)
        
        # Set up API client
        self.client = APIClient()
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
    def authenticate_user(self):
        """Authenticate as regular user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        
    def test_admin_action_creation(self):
        """Test creating admin actions"""
        self.authenticate_admin()
        
        data = {
            'action_type': 'user_ban',
            'target_user': self.regular_user.id,
            'description': 'Banned user for violation',
            'reason': 'Spam'
        }
        
        response = self.client.post('/api/admin/admin-actions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if admin action was created
        action = AdminAction.objects.get(id=response.data['id'])
        self.assertEqual(action.admin, self.admin_user)
        self.assertEqual(action.action_type, 'user_ban')
        
    def test_system_configuration_management(self):
        """Test system configuration CRUD operations"""
        self.authenticate_admin()
        
        # Create configuration
        config_data = {
            'name': 'test_setting',
            'config_type': 'general',
            'value': 'test_value',
            'description': 'Test configuration',
            'is_active': True
        }
        
        response = self.client.post('/api/admin/system-configurations/', config_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Update configuration
        config_id = response.data['name']
        update_data = {'value': 'updated_value'}
        
        response = self.client.patch(f'/api/admin/system-configurations/{config_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'updated_value')
        
    def test_maintenance_mode_activation(self):
        """Test maintenance mode activation/deactivation"""
        self.authenticate_admin()
        
        # Create maintenance mode
        maintenance_data = {
            'title': 'System Maintenance',
            'message': 'System under maintenance',
            'is_active': False
        }
        
        response = self.client.post('/api/admin/maintenance-modes/', maintenance_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        maintenance_id = response.data['id'] if 'id' in response.data else 1
        
        # Activate maintenance mode
        response = self.client.post(f'/api/admin/maintenance-modes/{maintenance_id}/activate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'activated')
        
        # Deactivate maintenance mode
        response = self.client.post(f'/api/admin/maintenance-modes/{maintenance_id}/deactivate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'deactivated')
        
    def test_bulk_user_actions(self):
        """Test bulk user actions"""
        self.authenticate_admin()
        
        # Create additional users
        user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='user123'
        )
        
        bulk_data = {
            'action': 'ban',
            'user_ids': [self.regular_user.id, user2.id],
            'reason': 'Bulk ban test'
        }
        
        response = self.client.post('/api/admin/bulk-user-action/', bulk_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)
        
        # Verify users are banned
        self.regular_user.refresh_from_db()
        user2.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)
        self.assertFalse(user2.is_active)
        
    def test_user_details_endpoint(self):
        """Test user details endpoint"""
        self.authenticate_admin()
        
        response = self.client.get(f'/api/admin/user/{self.regular_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.regular_user.id)
        self.assertEqual(response.data['username'], self.regular_user.username)
        
    def test_system_overview(self):
        """Test system overview endpoint"""
        self.authenticate_admin()
        
        response = self.client.get('/api/admin/system-overview/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check required keys
        required_keys = ['users', 'projects', 'transactions', 'system']
        for key in required_keys:
            self.assertIn(key, response.data)
            
    def test_admin_notifications(self):
        """Test admin notifications"""
        self.authenticate_admin()
        
        # Create notification
        notification = AdminNotification.objects.create(
            title='Test Notification',
            message='Test message',
            notification_type='system_alert',
            recipient=self.admin_user
        )
        
        # Get notifications
        response = self.client.get('/api/admin/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Mark as read
        response = self.client.post(f'/api/admin/notifications/{notification.id}/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        
    def test_backup_creation(self):
        """Test backup creation"""
        self.authenticate_admin()
        
        backup_data = {
            'backup_type': 'database'
        }
        
        response = self.client.post('/api/admin/backups/create_backup/', backup_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if backup record was created
        backup = BackupRecord.objects.get(id=response.data['id'])
        self.assertEqual(backup.backup_type, 'database')
        self.assertEqual(backup.created_by, self.admin_user)
        
    def test_system_health_monitoring(self):
        """Test system health monitoring"""
        self.authenticate_admin()
        
        # Create health record
        health_record = SystemHealth.objects.create(
            overall_status='healthy',
            cpu_usage=25.5,
            memory_usage=60.0,
            disk_usage=45.0
        )
        
        # Get latest health status
        response = self.client.get('/api/admin/system-health/latest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['overall_status'], 'healthy')
        
    def test_unauthorized_access(self):
        """Test that non-admin users cannot access admin endpoints"""
        self.authenticate_user()
        
        # Try to access admin-only endpoint
        response = self.client.get('/api/admin/admin-actions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access admin endpoints"""
        # Don't authenticate
        response = self.client.get('/api/admin/admin-actions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        self.authenticate_admin()
        
        response = self.client.get('/api/admin/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check required sections
        required_sections = ['users', 'projects', 'sales']
        for section in required_sections:
            self.assertIn(section, response.data)
            
    def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint"""
        self.authenticate_admin()
        
        response = self.client.get('/api/admin/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check for analytics sections
        self.assertIn('👥 users', response.data)
        self.assertIn('📁 projects', response.data)
        self.assertIn('💰 revenue', response.data)
        
    def test_export_data(self):
        """Test data export functionality"""
        self.authenticate_admin()
        
        export_data = {
            'export_type': 'users',
            'date_from': '2023-01-01',
            'date_to': '2023-12-31'
        }
        
        response = self.client.post('/api/admin/export-data/', export_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('export_id', response.data)
        
    def test_admin_session_management(self):
        """Test admin session management"""
        self.authenticate_admin()
        
        # Create admin session
        session = AdminSession.objects.create(
            admin=self.admin_user,
            session_key='test_session_key',
            ip_address='127.0.0.1'
        )
        
        # Get active sessions
        response = self.client.get('/api/admin/admin-sessions/active_sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Terminate session
        response = self.client.post(f'/api/admin/admin-sessions/{session.id}/terminate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        session.refresh_from_db()
        self.assertIsNotNone(session.ended_at)
        

class AdminPanelModelTestCase(TestCase):
    """Test admin panel models"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_staff=True
        )
        
    def test_admin_action_creation(self):
        """Test AdminAction model"""
        action = AdminAction.objects.create(
            admin=self.admin_user,
            action_type='user_ban',
            description='Test action'
        )
        
        self.assertEqual(str(action), f'{self.admin_user.username} - user_ban - {action.created_at}')
        self.assertEqual(action.admin, self.admin_user)
        
    def test_system_configuration(self):
        """Test SystemConfiguration model"""
        config = SystemConfiguration.objects.create(
            name='test_config',
            config_type='general',
            value='test_value',
            last_modified_by=self.admin_user
        )
        
        self.assertEqual(str(config), 'general: test_config')
        self.assertEqual(config.last_modified_by, self.admin_user)
        
    def test_maintenance_mode(self):
        """Test MaintenanceMode model"""
        maintenance = MaintenanceMode.objects.create(
            title='Test Maintenance',
            message='System under maintenance',
            is_active=True
        )
        
        self.assertTrue('Active' in str(maintenance))
        self.assertTrue(maintenance.is_active)
        
    def test_admin_notification(self):
        """Test AdminNotification model"""
        notification = AdminNotification.objects.create(
            title='Test Notification',
            message='Test message',
            notification_type='system_alert',
            recipient=self.admin_user
        )
        
        self.assertEqual(str(notification), 'system_alert: Test Notification')
        self.assertFalse(notification.is_read)
        
    def test_backup_record(self):
        """Test BackupRecord model"""
        backup = BackupRecord.objects.create(
            backup_type='database',
            status='completed',
            created_by=self.admin_user
        )
        
        self.assertIn('database backup', str(backup))
        self.assertEqual(backup.created_by, self.admin_user)
        
    def test_system_health(self):
        """Test SystemHealth model"""
        health = SystemHealth.objects.create(
            overall_status='healthy',
            cpu_usage=25.5,
            memory_usage=60.0
        )
        
        self.assertEqual(health.overall_status, 'healthy')
        self.assertEqual(health.cpu_usage, 25.5)
        
    def test_bulk_action(self):
        """Test BulkAction model"""
        bulk_action = BulkAction.objects.create(
            admin=self.admin_user,
            action_type='user_bulk_ban',
            total_items=10,
            processed_items=5
        )
        
        self.assertIn('user_bulk_ban', str(bulk_action))
        self.assertEqual(bulk_action.total_items, 10)
        
    def test_admin_session(self):
        """Test AdminSession model"""
        session = AdminSession.objects.create(
            admin=self.admin_user,
            session_key='test_session',
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(session.admin, self.admin_user)
        self.assertEqual(session.ip_address, '127.0.0.1')
