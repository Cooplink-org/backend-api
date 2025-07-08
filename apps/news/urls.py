from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'news'

router = DefaultRouter()
router.register('articles', views.NewsArticleViewSet)
router.register('categories', views.NewsCategoryViewSet)
router.register('comments', views.NewsCommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('articles/<uuid:article_id>/like/', views.NewsLikeView.as_view(), name='article-like'),
    path('articles/<uuid:article_id>/view/', views.NewsViewCreateView.as_view(), name='article-view'),
    path('trending/', views.TrendingNewsView.as_view(), name='trending'),
    path('featured/', views.FeaturedNewsView.as_view(), name='featured'),
]
