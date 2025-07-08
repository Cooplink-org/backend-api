from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import secrets
import structlog
import requests
import urllib.parse

from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    GitHubOAuthSerializer
)

logger = structlog.get_logger(__name__)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        logger.info("User registered", user_id=user.id, email=user.email)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        logger.info("User logged in", user_id=user.id, email=user.email)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info("User logged out", user_id=request.user.id)
            
            return Response({'message': 'Successfully logged out'}, 
                          status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Logout error", error=str(e), user_id=request.user.id)
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

@api_view(['GET'])
@permission_classes([AllowAny])
def github_oauth_initiate(request):
    client_id = settings.GITHUB_CLIENT_ID
    redirect_uri = request.build_absolute_uri('/api/auth/github/callback/')
    
    # Generate and store a random state parameter
    state = secrets.token_urlsafe(16)
    request.session['oauth_state'] = state
    
    params = urllib.parse.urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'user',
        'response_type': 'code',
        'state': state
    })
    auth_url = f'https://github.com/login/oauth/authorize?{params}'
    
    logger.info("GitHub OAuth initiated", state=state)
    
    return Response({'auth_url': auth_url, 'state': state})

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def github_oauth_callback(request):
    state = request.GET.get('state') or request.data.get('state')
    saved_state = request.session.get('oauth_state')
    if not state or state != saved_state:
        return Response({'error': 'Invalid or missing state parameter'}, status=status.HTTP_400_BAD_REQUEST)

    code = request.GET.get('code') or request.data.get('code')
    if not code:
        return Response({'error': 'Authorization code is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    token_url = 'https://github.com/login/oauth/access_token'
    client_id = settings.GITHUB_CLIENT_ID
    client_secret = settings.GITHUB_CLIENT_SECRET
    redirect_uri = request.build_absolute_uri('/api/auth/github/callback/')
    
    token_response = requests.post(token_url, data={
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri
    }, headers={'Accept': 'application/json'})
    
    if token_response.status_code != 200:
        return Response({'error': 'Failed to obtain access token'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    access_token = token_response.json().get('access_token')
    if not access_token:
        return Response({'error': 'No access token found'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    user_data_response = requests.get('https://api.github.com/user', 
                                      headers={'Authorization': f'token {access_token}'})

    if user_data_response.status_code != 200:
        return Response({'error': 'Failed to fetch user data'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    user_data = user_data_response.json()
    github_id = user_data.get('id')
    github_username = user_data.get('login')

    if not github_id or not github_username:
        return Response({'error': 'Incomplete user data from GitHub'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    user, created = User.objects.get_or_create(
        github_id=github_id,
        defaults={'github_username': github_username}
    )

    if created:
        logger.info("New user registered via GitHub", github_id=github_id, github_username=github_username)
    else:
        logger.info("Existing user logged in via GitHub", github_id=github_id, github_username=github_username)

    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserProfileSerializer(user).data,
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def link_github(request):
    github_id = request.data.get('github_id')
    github_username = request.data.get('github_username')
    
    if not github_id:
        return Response({'error': 'GitHub ID is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(github_id=github_id).exclude(id=request.user.id).exists():
        return Response({'error': 'This GitHub account is already linked to another user'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    request.user.github_id = github_id
    request.user.github_username = github_username
    request.user.save()
    
    logger.info("GitHub linked", user_id=request.user.id, github_id=github_id)
    
    return Response({
        'message': 'GitHub account linked successfully',
        'user': UserProfileSerializer(request.user).data
    })
