from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'role')
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        errors = {}
        if email is None:
            errors['email'] = ['This field is required.']
        if password is None:
            errors['password'] = ['This field is required.']

        if errors:
            raise serializers.ValidationError(errors)

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({'non_field_errors': ['Invalid credentials']})
        if not user.is_active:
            raise serializers.ValidationError({'non_field_errors': ['User account is disabled']})

        attrs['user'] = user
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'github_username', 
                 'balance', 'is_verified', 'created_at')
        read_only_fields = ('balance', 'is_verified', 'created_at')

class GitHubOAuthSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField(required=False)
    
    def validate(self, attrs):
        code = attrs.get('code')
        if not code:
            raise serializers.ValidationError({'code': ['This field is required.']})
        return attrs

class GitHubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'github_id', 'github_username')
        read_only_fields = ('id', 'github_id', 'github_username')
