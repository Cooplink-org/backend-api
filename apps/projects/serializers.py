from rest_framework import serializers
from .models import Project, ProjectTranslation, Purchase, Review, ProjectReport
from apps.accounts.serializers import UserProfileSerializer

class ProjectTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTranslation
        fields = ('language', 'title', 'description')

class ProjectListSerializer(serializers.ModelSerializer):
    seller = UserProfileSerializer(read_only=True)
    languages_list = serializers.SerializerMethodField()
    frameworks_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ('id', 'seller', 'title', 'image', 'demo_link', 'project_type', 
                 'languages_list', 'frameworks_list', 'price_uzs', 'downloads', 
                 'rating', 'reviews_count', 'created_at')
    
    def get_languages_list(self, obj):
        return [lang.strip() for lang in obj.languages.split(',') if lang.strip()]
    
    def get_frameworks_list(self, obj):
        return [fw.strip() for fw in obj.frameworks.split(',') if fw.strip()]

class ProjectDetailSerializer(serializers.ModelSerializer):
    seller = UserProfileSerializer(read_only=True)
    translations = ProjectTranslationSerializer(many=True, read_only=True)
    languages_list = serializers.SerializerMethodField()
    frameworks_list = serializers.SerializerMethodField()
    user_purchased = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ('id', 'seller', 'title', 'description', 'image', 'demo_link', 
                 'project_type', 'languages_list', 'frameworks_list', 'price_uzs', 
                 'downloads', 'rating', 'reviews_count', 'translations', 
                 'user_purchased', 'created_at', 'updated_at')
    
    def get_languages_list(self, obj):
        return [lang.strip() for lang in obj.languages.split(',') if lang.strip()]
    
    def get_frameworks_list(self, obj):
        return [fw.strip() for fw in obj.frameworks.split(',') if fw.strip()]
    
    def get_user_purchased(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Purchase.objects.filter(
                buyer=request.user, 
                project=obj, 
                status='completed'
            ).exists()
        return False

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('title', 'description', 'image', 'demo_link', 'project_type', 
                 'languages', 'frameworks', 'price_uzs', 'file')
    
    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

class PurchaseSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    buyer = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Purchase
        fields = ('id', 'buyer', 'project', 'amount_uzs', 'status', 'verification_deadline', 
                 'is_verified', 'created_at', 'completed_at')

class ReviewSerializer(serializers.ModelSerializer):
    buyer = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'buyer', 'rating', 'comment', 'created_at')

class ProjectReportSerializer(serializers.ModelSerializer):
    purchase = PurchaseSerializer(read_only=True)
    
    class Meta:
        model = ProjectReport
        fields = ('id', 'purchase', 'reason', 'admin_notes', 'status', 'created_at', 'resolved_at')
