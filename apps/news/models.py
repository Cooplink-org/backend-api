from django.db import models
from django.urls import reverse
from markdownx.models import MarkdownxField
import uuid


class NewsCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_category'
        verbose_name_plural = 'News Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NewsArticle(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.TextField(max_length=300, help_text="Brief description")
    content = MarkdownxField()
    featured_image = models.ImageField(upload_to='news/images/', blank=True, null=True)
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, related_name='articles')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='news_articles')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    is_pinned = models.BooleanField(default=False, help_text="Pin to top of news list")
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_article'
        ordering = ['-is_pinned', '-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['is_pinned', 'status']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})


class NewsLike(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_like'
        unique_together = ['user', 'article']
        indexes = [
            models.Index(fields=['article', 'created_at']),
        ]


class NewsView(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_view'
        indexes = [
            models.Index(fields=['article', 'created_at']),
            models.Index(fields=['ip_address', 'article']),
        ]


class NewsComment(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_comment'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['article', 'is_approved', 'created_at']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.article.title}'


class NewsTranslation(models.Model):
    LANGUAGE_CHOICES = [
        ('uz', 'Uzbek'),
        ('en', 'English'),
        ('ru', 'Russian'),
    ]
    
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=200)
    excerpt = models.TextField(max_length=300)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_translation'
        unique_together = ['article', 'language']
        indexes = [
            models.Index(fields=['article', 'language']),
        ]
