from rest_framework import serializers
from website_sources.models import News, Category, Admission, ContactMessage, JobPosition, CareerApplication, TalentPool


class CategorySerializer(serializers.ModelSerializer):
    # Har bir kategoriyada nechta published yangilik borligini ko'rsatadi
    news_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'branch', 'news_count']

    def get_news_count(self, obj):
        if hasattr(obj, '_news_count'):
            return obj._news_count
        return obj.news_set.filter(published=True).count()


class NewsListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True,
        required=False, allow_null=True
    )

    class Meta:
        model = News
        fields = [
            'id', 'title', 'description', 'category', 'category_id',
            'date', 'image_url', 'image', 'published', 'slug',
            'views', 'branch', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'views', 'created_by', 'created_at', 'updated_at']


class PublicNewsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'description', 'category',
            'date', 'image_url', 'image', 'slug', 'views', 'created_at'
        ]


class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        fields = [
            'id', 'application_id', 'student_name', 'phone',
            'grade', 'status', 'notes', 'branch', 'created_at', 'updated_at'
        ]
        read_only_fields = ['application_id', 'created_at', 'updated_at']


class AdmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        fields = ['student_name', 'phone', 'grade', 'branch']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'message', 'status', 'branch', 'created_at']
        read_only_fields = ['status', 'created_at']


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message', 'branch']


class JobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = [
            'id', 'title', 'type', 'location', 'employment_type',
            'description', 'requirements', 'posted_date', 'deadline',
            'is_active', 'branch', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CareerApplicationSerializer(serializers.ModelSerializer):
    position_title = serializers.CharField(source='position.title', read_only=True)

    class Meta:
        model = CareerApplication
        fields = [
            'id', 'application_id', 'name', 'email', 'phone',
            'position', 'position_title', 'cv_file', 'cover_letter',
            'status', 'branch', 'created_at'
        ]
        read_only_fields = ['application_id', 'status', 'created_at']


class CareerApplicationUpdateSerializer(serializers.ModelSerializer):
    """
    PATCH /api/admin/careers/applications/:id/ uchun.

    Foydalanuvchi yuborishi mumkin:
      - multipart/form-data (agar cv_file o'zgarsa)
      - application/json   (faqat matn maydonlari o'zgarsa)

    cv_file yuborilmasa — eski fayl saqlanib qoladi.
    Faqat o'zgartirmoqchi bo'lgan maydonlarni yuboring.
    """
    cv_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = CareerApplication
        fields = ['name', 'email', 'phone', 'position', 'cv_file', 'cover_letter', 'status', 'branch']

    def update(self, instance, validated_data):
        # cv_file kelmagan bo'lsa — eskisini saqla
        if 'cv_file' not in validated_data or validated_data.get('cv_file') is None:
            validated_data.pop('cv_file', None)
        return super().update(instance, validated_data)


class TalentPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentPool
        fields = ['id', 'name', 'email', 'phone', 'expertise', 'cv_file', 'branch', 'created_at']
        read_only_fields = ['created_at']


class TalentPoolUpdateSerializer(serializers.ModelSerializer):
    """
    PATCH /api/admin/careers/talent-pool/:id/ uchun.
    cv_file ixtiyoriy — yuborilmasa eski fayl qoladi.
    """
    cv_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = TalentPool
        fields = ['name', 'email', 'phone', 'expertise', 'cv_file', 'branch']

    def update(self, instance, validated_data):
        if 'cv_file' not in validated_data or validated_data.get('cv_file') is None:
            validated_data.pop('cv_file', None)
        return super().update(instance, validated_data)
