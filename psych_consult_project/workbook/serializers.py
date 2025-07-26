from rest_framework import serializers
from .models import Workbook, Category, FavoriteWorkbook

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class WorkbookSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, allow_null=True)

    class Meta:
        model = Workbook
        fields = ('id', 'title', 'banner', 'pdf_file', 'category', 'category_id', 'created_at', 'is_locked')

    def get_is_locked(self, obj):
        return False

class WorkbookBannerSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()
    pdf_file = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Workbook
        fields = ('id', 'title', 'banner', 'pdf_file', 'description', 'category', 'created_at', 'is_locked')

    def get_is_locked(self, obj):
        return False

    def get_pdf_file(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None

class FavoriteWorkbookSerializer(serializers.ModelSerializer):
    workbooks = WorkbookSerializer(many=True, read_only=True)
    workbook_ids = serializers.PrimaryKeyRelatedField(queryset=Workbook.objects.all(), many=True, write_only=True, source='workbooks')

    class Meta:
        model = FavoriteWorkbook
        fields = ['id', 'workbooks', 'workbook_ids', 'created_at', 'updated_at']
        read_only_fields = ('user',)
