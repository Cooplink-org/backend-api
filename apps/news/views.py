from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, F
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import structlog

from .models import NewsArticle, NewsCategory, NewsLike, NewsView, NewsComment
from .serializers import (
    NewsArticleSerializer,
    NewsCategorySerializer,
    NewsCommentSerializer,
    NewsLikeSerializer
)

logger = structlog.get_logger(__name__)


class NewsCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsCategory.objects.filter(is_active=True)
    serializer_class = NewsCategorySerializer
    permission_classes = [AllowAny]


class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.filter(status='published').select_related('author', 'category').prefetch_related('translations')
    serializer_class = NewsArticleSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = NewsArticle.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('translations')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(tags__icontains=search)
            )
        
        return queryset.order_by('-is_pinned', '-published_at')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track view
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        NewsView.objects.create(
            user=request.user if request.user.is_authenticated else None,
            article=instance,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Increment view count
        NewsArticle.objects.filter(pk=instance.pk).update(
            views_count=F('views_count') + 1
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class NewsCommentViewSet(viewsets.ModelViewSet):
    queryset = NewsComment.objects.all()
    serializer_class = NewsCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        article_id = self.request.query_params.get('article')
        if article_id:
            return NewsComment.objects.filter(
                article_id=article_id,
                is_approved=True
            ).select_related('user', 'article').order_by('created_at')
        return NewsComment.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(ratelimit(key='user', rate='5/m', method='POST'), name='post')
class NewsLikeView(generics.CreateAPIView):
    serializer_class = NewsLikeSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, article_id):
        try:
            article = NewsArticle.objects.get(id=article_id, status='published')
        except NewsArticle.DoesNotExist:
            return Response(
                {'error': 'Article not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        like, created = NewsLike.objects.get_or_create(
            user=request.user,
            article=article
        )
        
        if created:
            # Increment like count
            NewsArticle.objects.filter(pk=article.pk).update(
                likes_count=F('likes_count') + 1
            )
            logger.info("News article liked", user_id=request.user.id, article_id=article.id)
            return Response({'message': 'Article liked'}, status=status.HTTP_201_CREATED)
        else:
            # Unlike - remove like
            like.delete()
            NewsArticle.objects.filter(pk=article.pk).update(
                likes_count=F('likes_count') - 1
            )
            logger.info("News article unliked", user_id=request.user.id, article_id=article.id)
            return Response({'message': 'Article unliked'}, status=status.HTTP_200_OK)


class NewsViewCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request, article_id):
        try:
            article = NewsArticle.objects.get(id=article_id, status='published')
        except NewsArticle.DoesNotExist:
            return Response(
                {'error': 'Article not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create view record
        NewsView.objects.create(
            user=request.user if request.user.is_authenticated else None,
            article=article,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return Response({'message': 'View recorded'}, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TrendingNewsView(generics.ListAPIView):
    serializer_class = NewsArticleSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        # Get trending news based on views and likes in last 7 days
        week_ago = timezone.now() - timezone.timedelta(days=7)
        return NewsArticle.objects.filter(
            status='published',
            published_at__gte=week_ago
        ).order_by('-views_count', '-likes_count')[:10]


class FeaturedNewsView(generics.ListAPIView):
    serializer_class = NewsArticleSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return NewsArticle.objects.filter(
            status='published',
            is_featured=True
        ).order_by('-published_at')[:5]
