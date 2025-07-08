from rest_framework import serializers
from .models import NewsArticle, NewsCategory, NewsLike, NewsView, NewsComment, NewsTranslation


class NewsCategorySerializer(serializers.ModelSerializer):
    articles_count = serializers.IntegerField(source='articles.count', read_only=True)
    
    class Meta:
        model = NewsCategory
        fields = [
            'id', 'name', 'slug', 'description', 'color', 
            'is_active', 'articles_count', 'created_at'
        ]


class NewsTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTranslation
        fields = ['language', 'title', 'excerpt', 'content', 'meta_description', 'meta_keywords']


class NewsArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    translations = NewsTranslationSerializer(many=True, read_only=True)
    tags_list = serializers.SerializerMethodField()
    reading_time = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'featured_image',
            'category', 'category_name', 'category_color', 'author', 'author_name',
            'status', 'priority', 'is_featured', 'is_pinned', 'views_count',
            'likes_count', 'tags', 'tags_list', 'meta_description', 'meta_keywords',
            'published_at', 'created_at', 'updated_at', 'translations',
            'reading_time', 'is_liked'
        ]
        read_only_fields = ['id', 'views_count', 'likes_count', 'created_at', 'updated_at']
    
    def get_tags_list(self, obj):
        if obj.tags:
            return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]
        return []
    
    def get_reading_time(self, obj):
        # Estimate reading time based on content length (average 200 words per minute)
        words = len(obj.content.split())
        minutes = max(1, words // 200)
        return f"{minutes} min read"
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return NewsLike.objects.filter(user=request.user, article=obj).exists()
        return False


class NewsCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsComment
        fields = [
            'id', 'article', 'user', 'user_name', 'parent', 'content',
            'is_approved', 'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = ['id', 'user', 'is_approved', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return NewsCommentSerializer(
                obj.replies.filter(is_approved=True).order_by('created_at'),
                many=True,
                context=self.context
            ).data
        return []


class NewsLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsLike
        fields = ['id', 'user', 'article', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class NewsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsView
        fields = ['id', 'user', 'article', 'ip_address', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
