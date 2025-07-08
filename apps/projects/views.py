from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, F, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import structlog

from .models import Project, Purchase, Review, ProjectReport
from .serializers import (
    ProjectListSerializer as ProjectSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    PurchaseSerializer,
    ReviewSerializer,
    ProjectReportSerializer
)
from rest_framework import serializers

logger = structlog.get_logger(__name__)


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.filter(
        is_approved=True,
        is_active=True
    ).select_related('seller').prefetch_related('reviews', 'translations')
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project_type', 'seller', 'languages', 'frameworks']
    search_fields = ['title', 'description', 'languages', 'frameworks']
    ordering_fields = ['created_at', 'price_uzs', 'downloads', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Project.objects.filter(
            is_approved=True,
            is_active=True
        ).select_related('seller').prefetch_related('reviews', 'translations')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment view count
        Project.objects.filter(pk=instance.pk).update(
            downloads=F('downloads') + 1
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured projects"""
        projects = self.get_queryset().filter(
            rating__gte=4.0,
            downloads__gte=10
        ).order_by('-rating', '-downloads')[:10]
        
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending projects"""
        week_ago = timezone.now() - timezone.timedelta(days=7)
        projects = self.get_queryset().filter(
            created_at__gte=week_ago
        ).order_by('-downloads', '-rating')[:10]
        
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get project categories/types"""
        categories = Project.PROJECT_TYPES
        return Response([
            {'value': value, 'label': label} 
            for value, label in categories
        ])


@method_decorator(ratelimit(key='user', rate='10/m', method='POST'), name='post')
class PurchaseCreateView(generics.CreateAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        
        # Check if user is trying to buy their own project
        if project.seller == self.request.user:
            raise serializers.ValidationError("You cannot purchase your own project")
        
        # Check if user already purchased this project
        if Purchase.objects.filter(
            buyer=self.request.user,
            project=project,
            status__in=['completed', 'pending']
        ).exists():
            raise serializers.ValidationError("You have already purchased this project")
        
        # Set verification deadline (24 hours from now)
        verification_deadline = timezone.now() + timezone.timedelta(hours=24)
        
        serializer.save(
            buyer=self.request.user,
            amount_uzs=project.price_uzs,
            verification_deadline=verification_deadline
        )


class PurchaseListView(generics.ListAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Purchase.objects.filter(
            buyer=self.request.user
        ).select_related('project', 'project__seller').order_by('-created_at')


class PurchaseDetailView(generics.RetrieveAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Purchase.objects.filter(
            buyer=self.request.user
        ).select_related('project', 'project__seller')


@method_decorator(ratelimit(key='user', rate='5/m', method='POST'), name='post')
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        purchase = serializer.validated_data['purchase']
        
        # Check if user owns the purchase
        if purchase.buyer != self.request.user:
            raise serializers.ValidationError("You can only review your own purchases")
        
        # Check if purchase is completed
        if purchase.status != 'completed':
            raise serializers.ValidationError("You can only review completed purchases")
        
        # Check if review already exists
        if Review.objects.filter(purchase=purchase).exists():
            raise serializers.ValidationError("You have already reviewed this purchase")
        
        project = purchase.project
        serializer.save(
            buyer=self.request.user,
            project=project
        )
        
        # Update project rating
        self.update_project_rating(project)
    
    def update_project_rating(self, project):
        """Update project rating and review count"""
        reviews = Review.objects.filter(project=project)
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
            project.rating = round(avg_rating, 2)
            project.reviews_count = reviews.count()
            project.save(update_fields=['rating', 'reviews_count'])


class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        if project_id:
            return Review.objects.filter(
                project_id=project_id
            ).select_related('buyer', 'project').order_by('-created_at')
        return Review.objects.none()


@method_decorator(ratelimit(key='user', rate='3/h', method='POST'), name='post')
class ProjectReportCreateView(generics.CreateAPIView):
    serializer_class = ProjectReportSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        purchase = serializer.validated_data['purchase']
        
        # Check if user owns the purchase
        if purchase.buyer != self.request.user:
            raise serializers.ValidationError("You can only report your own purchases")
        
        # Check if report already exists
        if ProjectReport.objects.filter(purchase=purchase).exists():
            raise serializers.ValidationError("You have already reported this purchase")
        
        serializer.save()


class MyProjectsView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(
            seller=self.request.user
        ).order_by('-created_at')


class ProjectUploadView(generics.CreateAPIView):
    serializer_class = ProjectCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(
            seller=self.request.user,
            is_approved=False  # Requires admin approval
        )


class ProjectUpdateView(generics.UpdateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(seller=self.request.user)


class ProjectDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(seller=self.request.user)


class ProjectDownloadView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, project_id):
        try:
            project = Project.objects.get(
                id=project_id,
                is_approved=True,
                is_active=True
            )
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user has purchased the project
        purchase = Purchase.objects.filter(
            buyer=request.user,
            project=project,
            status='completed'
        ).first()
        
        if not purchase:
            return Response(
                {'error': 'You must purchase this project to download it'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate download URL or return file
        return Response({
            'download_url': project.file.url,
            'project_title': project.title,
            'download_count': project.downloads
        })


class ProjectStatsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, project_id):
        try:
            project = Project.objects.get(
                id=project_id,
                seller=request.user
            )
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get project statistics
        purchases = Purchase.objects.filter(project=project)
        reviews = Review.objects.filter(project=project)
        
        stats = {
            'total_sales': purchases.filter(status='completed').count(),
            'total_revenue': sum(p.amount_uzs for p in purchases.filter(status='completed')),
            'pending_sales': purchases.filter(status='pending').count(),
            'total_downloads': project.downloads,
            'average_rating': project.rating,
            'total_reviews': reviews.count(),
            'rating_distribution': self.get_rating_distribution(reviews),
            'recent_sales': purchases.filter(
                status='completed',
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()
        }
        
        return Response(stats)
    
    def get_rating_distribution(self, reviews):
        """Get distribution of ratings"""
        distribution = {}
        for i in range(1, 6):
            distribution[str(i)] = reviews.filter(rating=i).count()
        return distribution
