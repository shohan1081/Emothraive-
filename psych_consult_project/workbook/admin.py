from django.contrib import admin
from .models import Workbook, Category, FavoriteWorkbook

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Workbook)
class WorkbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title',)
    autocomplete_fields = ('category',)

@admin.register(FavoriteWorkbook)
class FavoriteWorkbookAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
    filter_horizontal = ('workbooks',)
