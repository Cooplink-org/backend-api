from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class User(AbstractUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    github_id = models.BigIntegerField(null=True, blank=True, unique=True)
    github_username = models.CharField(max_length=100, null=True, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'accounts_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['github_id']),
            models.Index(fields=['role']),
        ]

