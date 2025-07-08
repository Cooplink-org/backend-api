from django.db import models
from django.core.validators import MinValueValidator
from markdownx.models import MarkdownxField
from decimal import Decimal
import uuid

class Project(models.Model):
    PROJECT_TYPES = [
        ('web_app', 'Web Application'),
        ('mobile_app', 'Mobile Application'),
        ('desktop_app', 'Desktop Application'),
        ('script', 'Script'),
        ('library', 'Library'),
        ('api', 'API'),
        ('bot', 'Bot'),
        ('game', 'Game'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = MarkdownxField()
    image = models.ImageField(upload_to='projects/images/', null=True, blank=True)
    demo_link = models.URLField(null=True, blank=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    languages = models.CharField(max_length=500, help_text="Comma-separated programming languages")
    frameworks = models.CharField(max_length=500, help_text="Comma-separated frameworks")
    price_uzs = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    file = models.FileField(upload_to='projects/files/')
    downloads = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    reviews_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects_project'
        indexes = [
            models.Index(fields=['seller']),
            models.Index(fields=['project_type']),
            models.Index(fields=['price_uzs']),
            models.Index(fields=['is_approved', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['rating']),
        ]
        ordering = ['-created_at']

class ProjectTranslation(models.Model):
    LANGUAGE_CHOICES = [
        ('uz', 'Uzbek'),
        ('en', 'English'),
        ('ru', 'Russian'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'projects_project_translation'
        unique_together = ['project', 'language']
        indexes = [
            models.Index(fields=['project', 'language']),
        ]

class Purchase(models.Model):
    PURCHASE_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='purchases')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='purchases')
    amount_uzs = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=PURCHASE_STATUS, default='pending')
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    verification_deadline = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'projects_purchase'
        indexes = [
            models.Index(fields=['buyer']),
            models.Index(fields=['project']),
            models.Index(fields=['status']),
            models.Index(fields=['verification_deadline']),
            models.Index(fields=['created_at']),
        ]

class Review(models.Model):
    buyer = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'projects_review'
        unique_together = ['buyer', 'project']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]

class ProjectReport(models.Model):
    REPORT_STATUS = [
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved_refund', 'Resolved - Refunded'),
        ('resolved_release', 'Resolved - Funds Released'),
        ('dismissed', 'Dismissed'),
    ]
    
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE)
    reason = models.TextField()
    admin_notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'projects_report'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
