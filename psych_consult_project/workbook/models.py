from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Workbook(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    banner = models.ImageField(upload_to='workbooks/banners/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='workbooks/pdfs/')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='workbooks')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class FavoriteWorkbook(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='favorite_workbook')
    workbooks = models.ManyToManyField(Workbook, related_name='favorited_by', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Favorite Workbook"