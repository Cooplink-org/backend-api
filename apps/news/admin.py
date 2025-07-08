from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import NewsCategory, NewsArticle, NewsLike, NewsView, NewsComment, NewsTranslation


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'colored_name', 'articles_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    
    def colored_name(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            obj.color,
            obj.name
        )
    colored_name.short_description = 'Color Preview'
    
    def articles_count(self, obj):
        return obj.articles.count()
    articles_count.short_description = 'Articles'


class NewsTranslationInline(admin.TabularInline):
    model = NewsTranslation
    extra = 0
    fields = ('language', 'title', 'excerpt')


class NewsCommentInline(admin.TabularInline):
    model = NewsComment
    extra = 0
    fields = ('user', 'content', 'is_approved', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'priority', 'is_featured', 'is_pinned', 'views_count', 'likes_count', 'published_at', 'created_at')
    list_filter = ('status', 'priority', 'is_featured', 'is_pinned', 'category', 'created_at', 'published_at')
    search_fields = ('title', 'excerpt', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('id', 'views_count', 'likes_count', 'created_at', 'updated_at')
    inlines = [NewsTranslationInline, NewsCommentInline]
    
    fieldsets = (
        ('Article Information', {
            'fields': ('id', 'title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        ('Categorization', {
            'fields': ('category', 'tags', 'author')
        }),
        ('Publishing', {
            'fields': ('status', 'priority', 'is_featured', 'is_pinned', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New article
            obj.author = request.user
        
        # Auto-set published_at when status changes to published
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()
        
        super().save_model(request, obj, form, change)
    
    actions = ['make_published', 'make_draft', 'make_featured', 'make_pinned']
    
    def make_published(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} articles marked as published.')
    make_published.short_description = 'Mark selected articles as published'
    
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} articles marked as draft.')
    make_draft.short_description = 'Mark selected articles as draft'
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} articles marked as featured.')
    make_featured.short_description = 'Mark selected articles as featured'
    
    def make_pinned(self, request, queryset):
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} articles marked as pinned.')
    make_pinned.short_description = 'Mark selected articles as pinned'


@admin.register(NewsLike)
class NewsLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at', 'article__category')
    search_fields = ('user__username', 'user__email', 'article__title')
    readonly_fields = ('created_at',)


@admin.register(NewsView)
class NewsViewAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'ip_address', 'created_at')
    list_filter = ('created_at', 'article__category')
    search_fields = ('article__title', 'ip_address', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'short_content', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'article__category')
    search_fields = ('content', 'user__username', 'article__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content Preview'
    
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments disapproved.')
    disapprove_comments.short_description = 'Disapprove selected comments'


@admin.register(NewsTranslation)
class NewsTranslationAdmin(admin.ModelAdmin):
    list_display = ('article', 'language', 'title', 'created_at')
    list_filter = ('language', 'created_at')
    search_fields = ('article__title', 'title', 'content')
    readonly_fields = ('created_at',)
