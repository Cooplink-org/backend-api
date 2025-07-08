import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, Mock

from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    GitHubOAuthSerializer
)

User = get_user_model()


class UserModelTests(TestCase):
    """Test cases for the User model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'role': 'buyer'
        }
    
    def test_create_user_with_valid_data(self):
        """Test creating a user with valid data."""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'buyer')
        self.assertEqual(user.balance, Decimal('0.00'))
        self.assertFalse(user.is_verified)
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
    
    def test_create_user_with_seller_role(self):
        """Test creating a user with seller role."""
        self.user_data['role'] = 'seller'
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.role, 'seller')
    
    def test_create_user_with_admin_role(self):
        """Test creating a user with admin role."""
        self.user_data['role'] = 'admin'
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.role, 'admin')
    
    def test_unique_email_constraint(self):
        """Test that email field is unique."""
        User.objects.create_user(**self.user_data)
        
        # Try to create another user with the same email
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser2',
                email='test@example.com',
                password='TestPass123!'
            )
    
    
    def test_user_string_representation(self):
        """Test the string representation of User model."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')
    
    def test_default_balance_is_zero(self):
        """Test that default balance is 0.00."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.balance, Decimal('0.00'))
    
    def test_default_role_is_buyer(self):
        """Test that default role is buyer."""
        user_data = self.user_data.copy()
        user_data.pop('role')
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.role, 'buyer')




class UserSerializerTests(TestCase):
    """Test cases for user serializers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'role': 'buyer'
        }
    
    def test_user_registration_serializer_valid_data(self):
        """Test UserRegistrationSerializer with valid data."""
        serializer = UserRegistrationSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'buyer')
        self.assertTrue(user.check_password('TestPass123!'))
    
    def test_user_registration_serializer_password_mismatch(self):
        """Test UserRegistrationSerializer with password mismatch."""
        self.user_data['password_confirm'] = 'DifferentPass123!'
        serializer = UserRegistrationSerializer(data=self.user_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_user_registration_serializer_weak_password(self):
        """Test UserRegistrationSerializer with weak password."""
        self.user_data['password'] = 'weak'
        self.user_data['password_confirm'] = 'weak'
        serializer = UserRegistrationSerializer(data=self.user_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_user_login_serializer_valid_credentials(self):
        """Test UserLoginSerializer with valid credentials."""
        # Create a user first
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        serializer = UserLoginSerializer(data=login_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], user)
    
    def test_user_login_serializer_invalid_credentials(self):
        """Test UserLoginSerializer with invalid credentials."""
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        serializer = UserLoginSerializer(data=login_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_user_login_serializer_missing_fields(self):
        """Test UserLoginSerializer with missing fields."""
        login_data = {'email': 'test@example.com'}
        
        serializer = UserLoginSerializer(data=login_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_user_profile_serializer(self):
        """Test UserProfileSerializer."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            role='seller',
            balance=Decimal('100.50')
        )
        
        serializer = UserProfileSerializer(user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['role'], 'seller')
        self.assertEqual(data['balance'], '100.50')
        self.assertFalse(data['is_verified'])
        self.assertIn('created_at', data)


class AccountsAPITests(APITestCase):
    """Test cases for accounts API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'role': 'buyer'
        }
        
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPass123!'
        )
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        
        # Verify user was created
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'buyer')
    
    def test_user_registration_duplicate_email(self):
        """Test user registration with duplicate email."""
        self.user_data['email'] = 'existing@example.com'
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_password_mismatch(self):
        """Test user registration with password mismatch."""
        self.user_data['password_confirm'] = 'DifferentPass123!'
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_missing_fields(self):
        """Test user registration with missing fields."""
        incomplete_data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        url = reverse('register')
        response = self.client.post(url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_success(self):
        """Test successful user login."""
        login_data = {
            'email': 'existing@example.com',
            'password': 'ExistingPass123!'
        }
        url = reverse('login')
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        
        # Verify user data in response
        user_data = response.data['user']
        self.assertEqual(user_data['email'], 'existing@example.com')
        self.assertEqual(user_data['username'], 'existinguser')
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        login_data = {
            'email': 'existing@example.com',
            'password': 'wrongpassword'
        }
        url = reverse('login')
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_nonexistent_user(self):
        """Test user login with non-existent user."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'TestPass123!'
        }
        url = reverse('login')
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_missing_fields(self):
        """Test user login with missing fields."""
        login_data = {'email': 'existing@example.com'}
        url = reverse('login')
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_refresh_success(self):
        """Test successful token refresh."""
        refresh = RefreshToken.for_user(self.existing_user)
        refresh_data = {'refresh': str(refresh)}
        
        url = reverse('token_refresh')
        response = self.client.post(url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token."""
        refresh_data = {'refresh': 'invalid_token'}
        
        url = reverse('token_refresh')
        response = self.client.post(url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_view_authenticated(self):
        """Test profile view with authenticated user."""
        refresh = RefreshToken.for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'existing@example.com')
        self.assertEqual(response.data['username'], 'existinguser')
    
    def test_profile_view_unauthenticated(self):
        """Test profile view without authentication."""
        url = reverse('profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_update_authenticated(self):
        """Test profile update with authenticated user."""
        refresh = RefreshToken.for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        update_data = {
            'username': 'updateduser',
            'role': 'seller'
        }
        
        url = reverse('profile')
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'updateduser')
        self.assertEqual(response.data['role'], 'seller')
        
        # Verify in database
        self.existing_user.refresh_from_db()
        self.assertEqual(self.existing_user.username, 'updateduser')
        self.assertEqual(self.existing_user.role, 'seller')
    
    def test_profile_update_unauthenticated(self):
        """Test profile update without authentication."""
        update_data = {'username': 'updateduser'}
        
        url = reverse('profile')
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GitHubOAuthAPITests(APITestCase):
    """Test cases for GitHub OAuth authentication API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            github_id=123456789,
            github_username='testuser_gh'
        )
    
    def test_github_auth_initiate_success(self):
        """Test successful GitHub auth initiation."""
        url = reverse('github_oauth_initiate')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_url', response.data)
        self.assertIn('state', response.data)
        
        # Verify auth URL contains GitHub OAuth endpoint
        auth_url = response.data['auth_url']
        self.assertIn('github.com/login/oauth/authorize', auth_url)
        self.assertIn('client_id', auth_url)
        self.assertIn('state', auth_url)
    
    @patch('requests.post')
    def test_github_auth_callback_success(self, mock_post):
        """Test successful GitHub auth callback."""
        # Mock GitHub API responses
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            'access_token': 'github_access_token',
            'token_type': 'bearer'
        }
        
        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = {
            'id': 123456789,
            'login': 'testuser_gh',
            'email': 'test@example.com',
            'name': 'Test User'
        }
        
        with patch('requests.get', return_value=mock_user_response):
            mock_post.return_value = mock_token_response
            
            callback_data = {
                'code': 'github_auth_code',
                'state': 'valid_state'
            }
            
            url = reverse('github_oauth_callback')
            response = self.client.post(url, callback_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('access', response.data)
            self.assertIn('refresh', response.data)
            self.assertIn('user', response.data)
            
            # Verify user data
            user_data = response.data['user']
            self.assertEqual(user_data['github_id'], 123456789)
            self.assertEqual(user_data['github_username'], 'testuser_gh')
    
    def test_github_auth_callback_missing_code(self):
        """Test GitHub auth callback with missing code."""
        callback_data = {'state': 'valid_state'}
        
        url = reverse('github_oauth_callback')
        response = self.client.post(url, callback_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_github_auth_callback_missing_state(self):
        """Test GitHub auth callback with missing state."""
        callback_data = {'code': 'github_auth_code'}
        
        url = reverse('github_oauth_callback')
        response = self.client.post(url, callback_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('requests.post')
    def test_github_auth_callback_invalid_code(self, mock_post):
        """Test GitHub auth callback with invalid code."""
        # Mock GitHub API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': 'bad_verification_code'
        }
        
        mock_post.return_value = mock_response
        
        callback_data = {
            'code': 'invalid_code',
            'state': 'valid_state'
        }
        
        url = reverse('github_oauth_callback')
        response = self.client.post(url, callback_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('requests.post')
    def test_github_auth_callback_new_user(self, mock_post):
        """Test GitHub auth callback creating new user."""
        # Mock GitHub API responses for new user
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            'access_token': 'github_access_token',
            'token_type': 'bearer'
        }
        
        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = {
            'id': 987654321,
            'login': 'newuser_gh',
            'email': 'newuser@example.com',
            'name': 'New User'
        }
        
        with patch('requests.get', return_value=mock_user_response):
            mock_post.return_value = mock_token_response
            
            callback_data = {
                'code': 'github_auth_code',
                'state': 'valid_state'
            }
            
            url = reverse('github_oauth_callback')
            response = self.client.post(url, callback_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('access', response.data)
            self.assertIn('refresh', response.data)
            self.assertIn('user', response.data)
            
            # Verify new user was created
            new_user = User.objects.get(github_id=987654321)
            self.assertEqual(new_user.email, 'newuser@example.com')
            self.assertEqual(new_user.github_username, 'newuser_gh')
    
    def test_link_github_success(self):
        """Test successful GitHub account linking."""
        # Create user without github_id
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='TestPass123!'
        )
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        link_data = {
            'github_id': 987654321,
            'github_username': 'newuser_gh'
        }
        
        url = reverse('github_link')
        response = self.client.post(url, link_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        
        # Verify user was updated
        user.refresh_from_db()
        self.assertEqual(user.github_id, 987654321)
        self.assertEqual(user.github_username, 'newuser_gh')
    
    def test_link_github_already_linked(self):
        """Test linking GitHub account that's already linked to another user."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123!'
        )
        
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        link_data = {
            'github_id': 123456789,  # Already linked to self.user
            'github_username': 'otheruser_gh'
        }
        
        url = reverse('github_link')
        response = self.client.post(url, link_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_link_github_unauthenticated(self):
        """Test linking GitHub account without authentication."""
        link_data = {
            'github_id': 987654321,
            'github_username': 'newuser_gh'
        }
        
        url = reverse('github_link')
        response = self.client.post(url, link_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_link_github_missing_github_id(self):
        """Test linking GitHub account with missing github_id."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        link_data = {'github_username': 'newuser_gh'}
        
        url = reverse('github_link')
        response = self.client.post(url, link_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
class AccountsIntegrationTests(APITestCase):
    """Integration tests for accounts functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
    
    def test_complete_user_registration_and_login_flow(self):
        """Test complete user registration and login flow."""
        # 1. Register a new user
        registration_data = {
            'username': 'integrationuser',
            'email': 'integration@example.com',
            'password': 'IntegrationPass123!',
            'password_confirm': 'IntegrationPass123!',
            'role': 'seller'
        }
        
        register_url = reverse('register')
        register_response = self.client.post(register_url, registration_data, format='json')
        
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', register_response.data)
        self.assertIn('refresh', register_response.data)
        
        # 2. Use the access token to access profile
        access_token = register_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_url = reverse('profile')
        profile_response = self.client.get(profile_url)
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['email'], 'integration@example.com')
        self.assertEqual(profile_response.data['role'], 'seller')
        
        # 3. Update profile
        update_data = {'username': 'updatedintegrationuser'}
        update_response = self.client.patch(profile_url, update_data, format='json')
        
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['username'], 'updatedintegrationuser')
        
        # 4. Logout and login again
        self.client.credentials()  # Clear authentication
        
        login_data = {
            'email': 'integration@example.com',
            'password': 'IntegrationPass123!'
        }
        
        login_url = reverse('login')
        login_response = self.client.post(login_url, login_data, format='json')
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(login_response.data['user']['username'], 'updatedintegrationuser')
        
        # 5. Refresh token
        refresh_token = login_response.data['refresh']
        refresh_data = {'refresh': refresh_token}
        
        refresh_url = reverse('token_refresh')
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
    
    def test_user_role_permissions(self):
        """Test that user roles are properly handled."""
        # Create users with different roles
        roles = ['buyer', 'seller', 'admin']
        
        for role in roles:
            user_data = {
                'username': f'{role}user',
                'email': f'{role}@example.com',
                'password': 'TestPass123!',
                'password_confirm': 'TestPass123!',
                'role': role
            }
            
            register_url = reverse('register')
            response = self.client.post(register_url, user_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['user']['role'], role)
            
            # Verify user was created with correct role
            user = User.objects.get(email=f'{role}@example.com')
            self.assertEqual(user.role, role)


# Run tests with verbose output
if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'rest_framework',
                'rest_framework_simplejwt',
                'accounts',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
        )
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    failures = test_runner.run_tests(["__main__"])
